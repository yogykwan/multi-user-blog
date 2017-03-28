import os
import hmac
import hashlib
import re
import string
import random
from functools import wraps

import jinja2

from google.appengine.ext import db

# render post

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


# hash password

def make_salt(length=5):
    return ''.join(random.choice(string.letters) for x in xrange(length))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)


# model keys

def users_key(name='default'):
    return db.Key.from_path('users', name)


def comment_key(name='default'):
    return db.Key.from_path('comments', name)


def blog_key(name='default'):
    return db.Key.from_path('blogs', name)


def like_key(name='default'):
    return db.Key.from_path('likes', name)


# hash cookie

SECRET = 'http://Jennica.Space'


def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(SECRET, val).hexdigest())


def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    return secure_val == make_secure_val(val) and val


# validate signup

USERNAME_RE = re.compile("^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile("^.{3,20}$")
EMAIL_RE = re.compile("^[\S]+@[\S]+.[\S]+$")


def valid_username(username):
    return username and USERNAME_RE.match(username)


def valid_password(password):
    return password and PASSWORD_RE.match(password)


def valid_email(email):
    return email and EMAIL_RE.match(email)


# validation decorators

def user_logged_in(function):
    @wraps(function)
    def wrapper(self, *a, **kw):
        print kw
        if self.user:
            return function(self, *a, **kw)
        else:
            self.redirect('/login')

    return wrapper


def post_exists(function):
    @wraps(function)
    def wrapper(self, post_id):
        post = db.get(db.Key.from_path('Post', int(post_id), parent=blog_key()))
        if post:
            return function(self, post)
        else:
            self.error(404)
            return

    return wrapper


def comment_exists(function):
    @wraps(function)
    def wrapper(self, post_id, comment_id):
        post = db.get(db.Key.from_path('Post', int(post_id), parent=blog_key()))
        comment = db.get(db.Key.from_path('Comment', int(comment_id), parent=comment_key()))
        if post and comment:
            return function(self, post, comment)
        else:
            self.error(404)
            return

    return wrapper


def user_owns_post(function):
    @wraps(function)
    def wrapper(self, post):
        if self.user.key().id() == post.user.key().id():
            return function(self, post)
        else:
            self.error(401)
            return

    return wrapper


def user_owns_comment(function):
    @wraps(function)
    def wrapper(self, post, comment):
        if self.user.key().id() == comment.user.key().id():
            return function(self, post, comment)
        else:
            self.error(401)
            return

    return wrapper
