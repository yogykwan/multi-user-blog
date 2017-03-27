import time

from blog_handler import BlogHandler
from models import Post, Comment


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
            self.render('editcomment.html', comment=comment.content, post=post)
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
