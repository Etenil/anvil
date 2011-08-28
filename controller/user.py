import web
from web import form
import common
from web.contrib.template import render_mako
from anvillib.form import AjaxTextbox
import anvillib.xmlrpc
import model.user
import model.project
import re

class User:
    user = None

    login_form = form.Form(
        form.Textbox('email'),
        form.Password('password'),
        form.Button('Login')
        )

    reg_form = form.Form(
        form.Textbox('name',
                     form.notnull,
                     form.regexp('^[a-z0-9._-]+$', "Name must only include low-case letters, digits, '.'. '_' and '-'")),
        form.Textbox('email',
                     form.notnull,
                     form.regexp('^[\w-]+(\.[\w-]+)*@([a-z0-9-]+(\.[a-z0-9-]+)*?\.[a-z]{2,6}|(\d{1,3}\.){3}\d{1,3})(:\d{4})?$', 'Invalid email address')),
        form.Password('password',
                      form.Validator('Must have more than 4 characters)',
                                     lambda x:len(x)>4)),
        form.Textbox('homepage'),
        form.Textarea('description'),
        form.Button('Register')
        )

    def GET(self, action=None, username=None):
        if action == "profile":
            return self.edit_profile()
        elif action == "login":
            return self.login()
        elif action == "logout":
            return self.logout()
        elif action == "register":
            return self.register()
        elif action == "users":
            return self.list_users()
        else:
            return self.show_user(action)

    def POST(self, action=None):
        if action == "listusers":
            return self.list_users_ajax()
        elif action == "profile":
            return self.do_edit_profile()
        elif action == "login":
            return self.do_login()
        elif action == "register":
            return self.do_register()
        else:
            return self.show_user(action)

    def list_users_ajax(self):
        i = web.input()
        users = model.user.list_users(i.value)
        if users != False:
            return common.render.autocomplete(users=users)
        else:
            return ""

    def register(self):
        f = self.reg_form()
        return common.render.register(form=f,
                               htTitle="Register")

    def do_register(self):
        f = self.reg_form()
        if not f.validates():
            return common.render.register(form=f,
                                   htTitle="Register")
        i = web.input()
        try:
            # Creating the user on the system
            anvillib.xmlrpc.create_user(i.name)
            # Adding the user
            model.user.create_user(name=i.name,
                                   email=i.email,
                                   password=i.password,
                                   homepage=i.homepage,
                                   description=i.description)
            common.session.user = i.name
            raise web.seeother('/')
        except model.user.UserError:
            return common.render.register(error="Username already exists!",
                                   form=f,
                                   htTitle="Register")

    def login(self):
        f = self.login_form()
        return common.render.login(form=f,
                                   htTitle="Login")

    def do_login(self):
        f = self.login_form()
        if not f.validates():
            return common.render.login(form=f,
                                htTitle="Login")
        i = web.input()
        user = model.user.user_login(email=i.email, password = i.password)
        if not user:
            return common.render.login(error="Incorrect username or password.",
                                form=f,
                                htTitle="Login")
        common.session.user = user.name
        raise web.seeother('/')

    def logout(self):
        common.session.user = None
        raise web.seeother('/')

    def show_user(self, username):
        try:
            user = model.user.User(name=username)
            canedit = (common.session.user == user.name)
            return common.render.profile(canedit=canedit,
                                  projs=model.user.get_user_proj(),
                                  u=user,
                                  htTitle="Profile")
        except model.user.UserError as error:
            #raise web.seeother('/')
            return common.render.main(content=str(error),
                               num_proj=model.project.count_proj(),
                               htTitle="Welcome to Anvil!")
    def list_users(self):
        users = model.user.list_users()
        return common.render.listusers(users=users,
                                htTitle="Users")

    def make_profile_form(self):
        f = form.Form(form.Textbox('name',
                                   form.notnull,
                                   form.regexp('^[a-z0-9._-]+$', "Name must only include low-case letters, digits, '.'. '_' and '-'"),
                                   value=self.user.name),
                      form.Textbox('email',
                                   form.notnull,
                                   form.regexp('^[\w-]+(\.[\w-]+)*@([a-z0-9-]+(\.[a-z0-9-]+)*?\.[a-z]{2,6}|(\d{1,3}\.){3}\d{1,3})(:\d{4})?$', 'Invalid email address'),
                                   value=self.user.email),
                      form.Textbox('homepage', value=self.user.homepage),
                      form.Textarea('description',
                                    value=self.user.description),
                      form.Button('Save'))
        return f

    def edit_profile(self):
        try:
            self.user = model.user.User(name=common.session.user)
            f = self.make_profile_form()
            return common.render.editprofile(username=self.user.name,
                                      form=f,
                                      htTitle="Edit Profile")
        except model.user.UserError as error:
            #raise web.seeother('/')
            return common.render.main(content=str(error),
                               num_proj=model.project.count_proj(),
                               htTitle="Welcome to Anvil!")

    def do_edit_profile(self):
        self.user = model.user.User(name=common.session.user)
        f = self.make_profile_form()

        if not f.validates():
            return common.render.editprofile(form=f,
                                      htTitle="Edit Profile")
        i = web.input()
        self.user.name = i.name
        self.user.email = i.email
        self.user.homepage = i.homepage
        self.user.description = i.description
        try:
            self.user.save()
            raise web.seeother('/*' + self.user.name)
        except:
            return common.render.register(error="Username already exists!",
                                   form=f,
                                   htTitle="Register")
