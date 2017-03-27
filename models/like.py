from google.appengine.ext import db
from user import User
from post import Post
from utility import like_key

class Like(db.Model):
    user = db.ReferenceProperty(User, required=True, collection_name='user_likes')
    post = db.ReferenceProperty(Post, required=True, collection_name='post_likes')

    @classmethod
    def create(cls, user, post):
        return Like(user=user, post=post, parent=like_key())
