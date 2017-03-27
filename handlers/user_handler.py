from blog_handler import BlogHandler
from models import User
from utility import valid_email, valid_password, valid_username


class Signup(BlogHandler):
    def get(self):
        self.render("signup.html")

    def post(self):
        self.username = self.request.get("username")
        self.password = self.request.get("password")
        self.verify = self.request.get("verify")
        self.email = self.request.get("email")

        params = dict(username=self.username, email=self.email)
        passed = True
        if not valid_username(self.username):
            params["error_username"] = "Invalid username!"
            passed = False
        else:
            u = User.by_name(self.username)
            if u:
                params["error_username"] = "User already exists!"
                passed = False
        if not valid_password(self.password):
            params["error_password"] = "Invalid password!"
            passed = False
        elif self.password != self.verify:
            params["error_verify"] = "Two passwords not same!"
            passed = False
        if self.email and not valid_email(self.email):
            params["error_email"] = "Invalid email!"
            passed = False

        if passed:
            u = User.register(self.username, self.password, self.email)
            u.put()
            self.login(u)
            self.redirect('/welcome')
        else:
            self.render("signup.html", **params)

    def done(self, *a, **kw):
        raise NotImplementedError


class Welcome(BlogHandler):
    def get(self):
        if self.user:
            username = self.user.name
            self.render("welcome.html", username=username)
        else:
            self.redirect('/signup')


class Login(BlogHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/welcome')
        else:
            self.render("login.html", error="Username and password don't match!")


class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/signup')
