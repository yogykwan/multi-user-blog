import time

from blog_handler import BlogHandler
from models import Comment
from utility import user_logged_in, comment_exists, user_owns_comment, post_exists


class NewComment(BlogHandler):
    @user_logged_in
    @post_exists
    def get(self, post):
        self.render('newcomment.html')

    @user_logged_in
    @post_exists
    def post(self, post):
        content = self.request.get('comment')
        if content:
            comment = Comment.create(content, self.user, post)
            comment.put()
            time.sleep(0.1)
            self.redirect('/blog/' + str(post.key().id()))
        else:
            error = "Complete content of comment, please!"
            self.render('newcomment.html', comment=content, error=error)


class EditComment(BlogHandler):
    @user_logged_in
    @comment_exists
    @user_owns_comment
    def get(self, post, comment):
        self.render('editcomment.html', comment=comment.content, post_id=post.key().id())

    @user_logged_in
    @comment_exists
    @user_owns_comment
    def post(self, post, comment):
        content = self.request.get('comment')
        if content:
            comment.content = content
            comment.put()
            time.sleep(0.1)
            self.redirect('/blog/' + str(post.key().id()))
        else:
            error = "Complete content of comment, please!"
            self.render('editcomment.html', comment=content, post_id=post.key().id(), error=error)


class DeleteComment(BlogHandler):
    @user_logged_in
    @comment_exists
    @user_owns_comment
    def post(self, post, comment):
        comment.delete()
        time.sleep(0.1)
        self.redirect('/blog/' + str(post.key().id()))
