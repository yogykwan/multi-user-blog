import time

from blog_handler import BlogHandler
from models import Post


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
            self.render("editpost.html", subject=post.subject, content=post.content, post_id=post_id)
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
