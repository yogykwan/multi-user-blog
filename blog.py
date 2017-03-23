import os
import hmac
import hashlib
import re
import string
import random

import webapp2
import jinja2

from google.appengine.ext import db

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


### user

def make_salt(length=5):
    return ''.join(random.choice(string.letters) for x in xrange(length))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)


def users_key(name='default'):
    return db.Key.from_path('users', name)


class User(db.Model):
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent=users_key())

    @classmethod
    def by_name(cls, name):
        return User.all().filter('name =', name).get()

    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = make_pw_hash(name, pw)
        return User(name=name, pw_hash=pw_hash, email=email, parent=users_key())

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u
        return None


### blog

def blog_key(name='default'):
    return db.Key.from_path('blogs', name)


class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    user = db.ReferenceProperty(User, required=True, collection_name='user_posts')

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p=self)


class MainPage(BlogHandler):
    def get(self):
        self.redirect('/blog')


class BlogFront(BlogHandler):
    def get(self):
        posts = db.GqlQuery("select * from Post order by created desc limit 10")
        self.render("front.html", posts=posts)


class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
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
            p = Post(subject=subject, content=content, user=self.user, parent=blog_key())
            p.put()
            self.redirect('/blog/' + str(p.key().id()))
        else:
            error = "Complete subject or content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)


class EditPost(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        print self.user.name, post.user.name, post.subject
        if self.user and post and self.user.key().id() == post.user.key().id():
            self.render("editpost.html", subject=post.subject, content=post.content)
        else:
            self.error(404)

    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
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
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        if self.user and post and self.user.key().id() == post.user.key().id():
            post.delete()
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


def like_key(name='default'):
    return db.Key.from_path('likes', name)


class Like(db.Model):
    user = db.ReferenceProperty(User, required=True, collection_name='user_likes')
    post = db.ReferenceProperty(Post, required=True, collection_name='post_likes')


class LikeBtn(BlogHandler):
    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        like_btn = self.request.get('like-btn')
        if post.user != self.user and post:
            like = self.user.user_likes.filter("post =", post).get()
            if like_btn == 'like':
                if not like:
                    like = Like(user=self.user, post=post, parent=like_key())
                    like.put()
            elif like_btn == 'unlike':
                if like:
                    like.delete()
            self.redirect('/blog/' + post_id)
        else:
            self.error(403)


class Comment(db.Model):
    user = db.ReferenceProperty(User, required=True, collection_name='user_comments')
    post = db.ReferenceProperty(Post, required=True, collection_name='post_comments')
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)


def comment_key(name='default'):
    return db.Key.from_path('comments', name)


class NewComment(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        if post and self.user:
            self.render('newcomment.html')
        else:
            self.error(404)

    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        content = self.request.get('comment')
        if post and self.user:
            if content:
                comment = Comment(content=content, user=self.user, post=post, parent=comment_key())
                comment.put()
                self.redirect('/blog/' + post_id)
            else:
                error = "Complete content of comment, please!"
                self.render('newcomment.html', comment=content, error=error)
        else:
            self.error(404)


class EditComment(BlogHandler):
    def get(self, post_id, comment_id):
        p_key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(p_key)
        c_key = db.Key.from_path('Comment', int(comment_id), parent=comment_key())
        comment = db.get(c_key)
        if comment and self.user.key().id() == comment.user.key().id():
            self.render('editcomment.html', comment=comment.content)
        else:
            self.error(403)

    def post(self, post_id, comment_id):
        p_key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(p_key)
        c_key = db.Key.from_path('Comment', int(comment_id), parent=comment_key())
        comment = db.get(c_key)
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
        p_key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(p_key)
        c_key = db.Key.from_path('Comment', int(comment_id), parent=comment_key())
        comment = db.get(c_key)
        if comment and self.user.key().id() == comment.user.key().id():
            comment.delete()
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
