import time

from blog_handler import BlogHandler
from models import Like
from utility import user_logged_in, post_exists


class LikeBtn(BlogHandler):
    @user_logged_in
    @post_exists
    def post(self, post):
        like_btn = self.request.get('like-btn')
        like = self.user.user_likes.filter("post =", post).get()
        if like_btn == 'like' and not like:
            like = Like.create(self.user, post)
            like.put()
        elif like_btn == 'unlike' and like:
            like.delete()
        time.sleep(0.1)
        self.redirect('/blog/' + str(post.key().id()))
