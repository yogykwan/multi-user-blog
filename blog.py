import os
import hmac
import hashlib
import re
import string
import random
import time
import webapp2
import jinja2


from models import User, Comment, Post, Like

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


SECRET = 'http://Jennica.Space'


def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(SECRET, val).hexdigest())


def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    return secure_val == make_secure_val(val) and val


class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')


class MainPage(BlogHandler):
    def get(self):
        self.redirect('/blog')


class BlogFront(BlogHandler):
    def get(self):
        posts = Post.by_limit(10)
        self.render("front.html", posts=posts)


class PostPage(BlogHandler):
    def get(self, post_id):
        post = Post.by_id(int(post_id))
        if post:
            liked = self.user and self.user.user_likes.filter("post =", post).count() > 0
            comments = post.post_comments.order('-created')
            self.render("permalink.html", post=post, user=self.user, liked=liked, comments=comments)
        else:
            self.error(404)


class NewPost(BlogHandler):
    def get(self):
        if not self.user:
            self.redirect('/login')
        self.render("newpost.html")

    def post(self):
        if not self.user:
            self.redirect('/login')
        subject = self.request.get('subject')
        content = self.request.get('content')
        if subject and content:
            post = Post.create(subject, content, self.user)
            post.put()
            self.redirect('/blog/' + str(post.key().id()))
        else:
            error = "Complete subject or content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error, user=self.user)


class EditPost(BlogHandler):
    def get(self, post_id):
        post = Post.by_id(int(post_id))
        print self.user.name, post.user.name, post.subject
        if self.user and post and self.user.key().id() == post.user.key().id():
            self.render("editpost.html", subject=post.subject, content=post.content)
        else:
            self.error(404)

    def post(self, post_id):
        post = Post.by_id(int(post_id))
        subject = self.request.get('subject')
        content = self.request.get('content')
        if self.user and post and self.user.key().id() == post.user.key().id():
            if subject and content:
                post.subject = subject
                post.content = content
                post.put()
                self.redirect('/blog/' + str(post_id))
            else:
                error = "Complete subject or content, please!"
                self.render("editpost.html", subject=subject, content=content, error=error)


class DeletePost(BlogHandler):
    def post(self, post_id):
        post = Post.by_id(int(post_id))
        if self.user and post and self.user.key().id() == post.user.key().id():
            post.delete()
            time.sleep(0.1)
            self.redirect('/blog')
        else:
            self.error(403)


USERNAME_RE = re.compile("^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile("^.{3,20}$")
EMAIL_RE = re.compile("^[\S]+@[\S]+.[\S]+$")


def valid_username(username):
    return username and USERNAME_RE.match(username)


def valid_password(password):
    return password and PASSWORD_RE.match(password)


def valid_email(email):
    return email and EMAIL_RE.match(email)


class Signup(BlogHandler):
    def get(self):
        self.render("signup.html")

    def post(self):
        self.username = self.request.get("username")
        self.password = self.request.get("password")
        self.verify = self.request.get("verify")
        self.email = self.request.get("email")

        params = dict(username=self.username, email=self.email)
        passed = True
        if not valid_username(self.username):
            params["error_username"] = "Invalid username!"
            passed = False
        else:
            u = User.by_name(self.username)
            if u:
                params["error_username"] = "User already exists!"
                passed = False
        if not valid_password(self.password):
            params["error_password"] = "Invalid password!"
            passed = False
        elif self.password != self.verify:
            params["error_verify"] = "Two passwords not same!"
            passed = False
        if self.email and not valid_email(self.email):
            params["error_email"] = "Invalid email!"
            passed = False

        if passed:
            u = User.register(self.username, self.password, self.email)
            u.put()
            self.login(u)
            self.redirect('/welcome')
        else:
            self.render("signup.html", **params)

    def done(self, *a, **kw):
        raise NotImplementedError


class Welcome(BlogHandler):
    def get(self):
        if self.user:
            username = self.user.name
            self.render("welcome.html", username=username)
        else:
            self.redirect('/signup')


class Login(BlogHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/welcome')
        else:
            self.render("login.html", error="Username and password don't match!")


class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/signup')

class LikeBtn(BlogHandler):
    def post(self, post_id):
        post = Post.by_id(int(post_id))
        like_btn = self.request.get('like-btn')
        if post.user != self.user and post:
            like = self.user.user_likes.filter("post =", post).get()
            if like_btn == 'like':
                if not like:
                    like = Like.create(self.user, post)
                    like.put()
            elif like_btn == 'unlike':
                if like:
                    like.delete()
            time.sleep(0.1)
            self.redirect('/blog/' + post_id)
        else:
            self.error(403)

class NewComment(BlogHandler):
    def get(self, post_id):
        post = Post.by_id(int(post_id))
        if post and self.user:
            self.render('newcomment.html')
        else:
            self.error(404)

    def post(self, post_id):
        post = Post.by_id(int(post_id))
        content = self.request.get('comment')
        if post and self.user:
            if content:
                comment = Comment.create(content, self.user, post)
                comment.put()
                time.sleep(0.1)
                self.redirect('/blog/' + post_id)
            else:
                error = "Complete content of comment, please!"
                self.render('newcomment.html', comment=content, error=error)
        else:
            self.error(404)


class EditComment(BlogHandler):
    def get(self, post_id, comment_id):
        post = Post.by_id(int(post_id))
        comment = Comment.by_id(int(comment_id))
        if comment and self.user.key().id() == comment.user.key().id():
            self.render('editcomment.html', comment=comment.content)
        else:
            self.error(403)

    def post(self, post_id, comment_id):
        post = Post.by_id(int(post_id))
        comment = Comment.by_id(int(comment_id))
        content = self.request.get('comment')
        if comment and self.user.key().id() == comment.user.key().id():
            if content:
                comment.content = content
                comment.put()
                self.redirect('/blog/' + post_id)
            else:
                error = "Complete content of comment, please!"
                self.render('editcomment.html', comment=content, error=error)
        else:
            self.error(403)


class DeleteComment(BlogHandler):
    def post(self, post_id, comment_id):
        post = Post.by_id(int(post_id))
        comment = Comment.by_id(int(comment_id))
        if comment and self.user.key().id() == comment.user.key().id():
            comment.delete()
            time.sleep(0.1)
            self.redirect('/blog/' + post_id)
        else:
            self.error(403)


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/([0-9]+)/like', LikeBtn),
                               ('/blog/([0-9]+)/comment/newcomment', NewComment),
                               ('/blog/([0-9]+)/comment/([0-9]+)/delete', DeleteComment),
                               ('/blog/([0-9]+)/comment/([0-9]+)/edit', EditComment),
                               ('/blog/newpost', NewPost),
                               ('/blog/([0-9]+)/edit', EditPost),
                               ('/blog/([0-9]+)/delete', DeletePost),
                               ('/signup', Signup),
                               ('/welcome', Welcome),
                               ('/login', Login),
                               ('/logout', Logout),
                               ],
                              debug=True)
