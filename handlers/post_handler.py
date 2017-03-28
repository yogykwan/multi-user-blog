import time

from blog_handler import BlogHandler
from models import Post
from utility import user_logged_in, post_exists, user_owns_post


class BlogFront(BlogHandler):
    def get(self):
        posts = Post.by_limit(10)
        self.render("front.html", posts=posts)


class PostPage(BlogHandler):
    @post_exists
    def get(self, post):
        liked = self.user and self.user.user_likes.filter("post =", post).count() > 0
        comments = post.post_comments.order('-created')
        self.render("permalink.html", post=post, user=self.user, liked=liked, comments=comments)


class NewPost(BlogHandler):
    @user_logged_in
    def get(self):
        self.render("newpost.html")

    @user_logged_in
    def post(self):
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
    @user_logged_in
    @post_exists
    @user_owns_post
    def get(self, post):
        self.render("editpost.html", subject=post.subject, content=post.content, post_id=post.key().id())

    @user_logged_in
    @post_exists
    @user_owns_post
    def post(self, post):
        subject = self.request.get('subject')
        content = self.request.get('content')
        if subject and content:
            post.subject = subject
            post.content = content
            post.put()
            self.redirect('/blog/' + str(post.key().id()))
        else:
            error = "Complete subject or content, please!"
            self.render("editpost.html", subject=subject, content=content, post_id=post.key().id(), error=error)


class DeletePost(BlogHandler):
    @user_logged_in
    @post_exists
    @user_owns_post
    def post(self, post):
        post.delete()
        time.sleep(0.1)
        self.redirect('/blog')
