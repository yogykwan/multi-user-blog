import time

from blog_handler import BlogHandler
from models import Post, Like


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
