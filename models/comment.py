from google.appengine.ext import db
from user import User
from post import Post
from utility import comment_key, render_str


class Comment(db.Model):
    user = db.ReferenceProperty(User, required=True, collection_name='user_comments')
    post = db.ReferenceProperty(Post, required=True, collection_name='post_comments')
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    def render(self, post, user):
        self._render_text = self.content.replace('\n', '<br>')
        print self._render_text
        return render_str('comment.html', comment=self, post=post, user=user)

    @classmethod
    def create(cls, content, user, post):
        return Comment(content=content, user=user, post=post, parent=comment_key())

    @classmethod
    def by_id(cls, comment_id):
        return Comment.get_by_id(comment_id, parent=comment_key())
