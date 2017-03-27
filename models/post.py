from google.appengine.ext import db
from user import User
from utility import render_str, blog_key

class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    user = db.ReferenceProperty(User, required=True, collection_name='user_posts')

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p=self)

    @classmethod
    def by_limit(cls, limit):
        return db.GqlQuery("select * from Post order by created desc limit {}".format(limit))

    @classmethod
    def by_id(cls, post_id):
        return Post.get_by_id(post_id, parent=blog_key())

    @classmethod
    def create(cls, subject, content, user):
        return Post(subject=subject, content=content, user=user, parent=blog_key())

