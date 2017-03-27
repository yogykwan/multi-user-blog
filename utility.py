import os
import hmac
import hashlib
import re
import string
import random

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

# render post

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

# keys

def users_key(name='default'):
    return db.Key.from_path('users', name)


def comment_key(name='default'):
    return db.Key.from_path('comments', name)

def blog_key(name='default'):
    return db.Key.from_path('blogs', name)

def like_key(name='default'):
    return db.Key.from_path('likes', name)



