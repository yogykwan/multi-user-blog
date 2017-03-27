import os
import hmac
import hashlib
import re
import string
import random

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
