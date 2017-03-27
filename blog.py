import webapp2

from handlers import *

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
