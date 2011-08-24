import web
import model
from common import *
from web import form
from web.contrib.template import render_mako
from anvillib.form import AjaxTextbox
import re

urls = (
    '/', 'Main',
    '/login', 'Login',
    '/logout', 'Logout',
    '/register', 'Register',
    '/\*([a-z0-9._-]+)$', 'User',
    '/([a-z0-9._-]+)(?:/(.+))?$', 'Project',
    '/profile$', 'UserProfile',
    '/message(?:/(.+))?$', 'UserMessage',
    '/ajax/listusers', 'AjaxListUsers',
    '/project(?:/(.+))?$', 'Project',
    )

app = web.application(urls, globals(), autoreload=False)
render = render_mako(
        directories=['templates'],
        input_encoding='utf-8',
        output_encoding='utf-8',
        )

session = web.session.Session(app,
                              web.session.DBStore(db, 'sessions'),
                              initializer={'user': None})


class Main:
    def GET(self):
        return render.main(content="Welcome to Anvil",
                           user=session.user,
                           msg_count=model.num_unread_msgs(session.user),
                           title=title,
                           htTitle="Welcome to Anvil!")
    #end GET
#end test

class Login:
    form = form.Form(
        form.Textbox('email'),
        form.Password('password'),
        form.Button('Login')
        )

    def GET(self):
        f = self.form()
        return render.login(form=f,
                            user=session.user,
                            msg_count=model.num_unread_msgs(session.user),
                            title=title,
                            htTitle="Login")

    def POST(self):
        f = self.form()
        if not f.validates():
            return render.login(form=f,
                                user=session.user,
                                title=title,
                                msg_count=model.num_unread_msgs(session.user),
                                htTitle="Login")
        i = web.input()
        user = model.user_login(email=i.email, password = i.password)
        if not user:
            return render.login(error="Incorrect username or password.",
                                user=session.user,
                                msg_count=model.num_unread_msgs(session.user),
                                form=f,
                                title=title,
                                htTitle="Login")
        session.user = user.name
        raise web.seeother('/')

class Logout:
    def GET(self):
        session.user = None
        raise web.seeother('/')

class Register:
    form = form.Form(
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

    def GET(self):
        f = self.form()
        return render.register(form=f,
                               user=session.user,
                               title=title,
                               msg_count=model.num_unread_msgs(session.user),
                               htTitle="Register")

    def POST(self):
        f = self.form()
        if not f.validates():
            return render.register(form=f,
                                   user=session.user,
                                   title=title,
                                   msg_count=model.num_unread_msgs(session.user),
                                   htTitle="Register")
        i = web.input()
        try:
            model.create_user(name=i.name,
                              email=i.email,
                              password=i.password,
                              homepage=i.homepage,
                              description=i.description)
            session.user = i.name
            raise web.seeother('/')
        except model.UserError:
            return render.register(error="Username already exists!",
                                   user=session.user,
                                   form=f,
                                   msg_count=model.num_unread_msgs(session.user),
                                   title=title,
                                   htTitle="Register")


class User:
    def GET(self, username):
        try:
            user = model.User(name=username)
            canedit = (session.user == user.name)
            return render.profile(title=title,
                                  user=session.user,
                                  canedit=canedit,
                                  msg_count=model.num_unread_msgs(session.user),
                                  u=user,
                                  htTitle="Profile")
        except model.UserError as error:
            #raise web.seeother('/')
            return render.main(content=str(error),
                               user=session.user,
                               msg_count=model.num_unread_msgs(session.user),
                               title=title,
                               htTitle="Welcome to Anvil!")

class UserProfile:
    user = None

    def GET(self):
        try:
            self.user = model.User(name=session.user)
            f = self.makeform()
            return render.editprofile(title=title,
                                      user=session.user,
                                      username=self.user.name,
                                      msg_count=model.num_unread_msgs(session.user),
                                      form=f,
                                      htTitle="Edit Profile")
        except model.UserError as error:
            #raise web.seeother('/')
            return render.main(content=str(error),
                               user=session.user,
                               msg_count=model.num_unread_msgs(session.user),
                               title=title,
                               htTitle="Welcome to Anvil!")

    def makeform(self):
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

    def POST(self):
        self.user = model.User(name=session.user)
        f = self.makeform()

        if not f.validates():
            return render.editprofile(title=title,
                                      user=session.user,
                                      username=self.user.name,
                                      msg_count=model.num_unread_msgs(session.user),
                                      form=f,
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
            return render.register(error="Username already exists!",
                                   user=session.user,
                                   form=f,
                                   msg_count=model.num_unread_msgs(session.user),
                                   title=title,
                                   htTitle="Register")

class UserMessage:
    new_form = form.Form(AjaxTextbox('to', '/ajax/listusers'),
                         form.Textbox('subject'),
                         form.Textarea('message'),
                         form.Button('Send'))

    def GET(self, action=None):
        if action == None or action == "all":
            return self.list_messages(action)
        elif re.match("^\d+$", action):
            return self.get_message(action)
        elif action == "new":
            return self.new_message()
        else:
            return self.list_messages(None)

    def POST(self, action=None):
        if action == "new":
            self.make_new_message()
        else:
            raise web.seeother('message/list')


    def list_messages(self, extra):
        user = model.User(name=session.user)
        read = (extra != None)
        msgs = model.get_user_inbox(user.id, read)
        return render.messages(msgs=msgs,
                               show_all=read,
                               u=user,
                               user=session.user,
                               msg_count=model.num_unread_msgs(session.user),
                               title=title,
                               htTitle="Inbox")

    def get_message(self, msgid):
        msg = model.Message(msgid)
        # Marking read
        msg.read = True
        msg.mark_read()
        return render.message(msg=msg,
                              user=session.user,
                              msg_count=model.num_unread_msgs(session.user),
                              title=title,
                              htTitle="Message")
    def new_message(self):
        return render.newmessage(user=session.user,
                                 title=title,
                                 msg_count=model.num_unread_msgs(session.user),
                                 htTitle="New message",
                                 form=self.new_form)

    def make_new_message(self):
        msg = model.Message()
        i = web.input()
        user = model.User(name=session.user)
        dests = i.to.split(',')

        errors = []
        for dest_name in dests:
            name = dest_name.strip()
            try:
                dest = model.User(name=name)
            except:
                errors.append("User '"+name+"' not found")

            msg.sender = user
            msg.dest = dest
            msg.subject = i.subject
            msg.content = i.message
            try:
                msg.save()
            except:
                errors.append("Couldn't send message to '"+name+"'")

        if len(errors) > 0:
            return render.newmessage(error="<br />".join(errors),
                                     user=session.user,
                                     title=title,
                                     msg_count=model.num_unread_msgs(session.user),
                                     htTitle="New message",
                                     form=self.new_form)
        raise web.seeother('/message/list')

class AjaxListUsers:
    def POST(self):
        i = web.input()
        users = model.list_users(i.value)
        if users != False:
            return render.autocomplete(users=users)
        else:
            return ""
#end AjaxListUsers

class Project:
    new_form = form.Form(
        form.Textbox('name',
                     form.notnull,
                     form.regexp('^[a-z0-9._-]+$', "Name must only include low-case letters, digits, '.'. '_' and '-'")),
        form.Textbox('homepage'),
        form.Textarea('description'),
        form.Button('Register'))

    def GET(self, action=None, other=None):
        if action == "new":
            return self.new_project()
        else:
            name = action
            if other == "edit":
                return self.edit_project(name)
            else:
                return self.show_project(name)
    #end GET

    def POST(self, action=None, other=None):
        if action == "new":
            return self.make_new()
        elif other == "edit":
            return self.make_edit_project(action)
        else:
            raise web.seeother('/')

    def new_project(self):
        f = self.new_form()
        return render.newproject(user=session.user,
                                 title=title,
                                 msg_count=model.num_unread_msgs(session.user),
                                 htTitle="New project",
                                 form=f)
    #end new_project

    def make_new(self):
        f = self.new_form()
        error = False
        errors = []

        if not f.validates():
            error = True

        i = web.input()
        proj = model.Project()
        proj.name = i.name
        proj.owner = model.User(name=session.user)
        proj.homepage = i.homepage
        proj.description = i.description
        try:
            proj.save()
        except:
            error = True
            errors.append("Projects already exists.")

        if error:
            return render.newproject(errors=errors,
                                     user=session.user,
                                     title=title,
                                     msg_count=model.num_unread_msgs(session.user),
                                     htTitle="New project",
                                     form=f)
        else:
            raise web.seeother('/' + proj.name)
    #end make_new

    def show_project(self, name):
        """Displays details about project <name>."""
        try:
            proj = model.Project(name=name)
        except:
            raise web.seeother('/')

        return render.project(proj=proj,
                              user=session.user,
                              title=title,
                              canedit=proj.isadmin(session.user),
                              msg_count=model.num_unread_msgs(session.user),
                              htTitle="Project")

    def make_edit_form(self, proj):
        edit_form = form.Form(
            form.Textbox('name',
                         form.notnull,
                         form.regexp('^[a-z0-9._-]+$', "Name must only include low-case letters, digits, '.'. '_' and '-'"), value=proj.name),
            form.Textbox('homepage', value=proj.homepage),
            form.Textarea('description', value=proj.description),
            form.Button('Save'))
        return edit_form

    def edit_project(self, name):
        proj = model.Project(name)
        if not proj.isadmin(session.user):
            raise web.seeother('/' + name)

        f = self.make_edit_form(proj)
        return render.newproject(proj=proj,
                                 user=session.user,
                                 title=title,
                                 msg_count=model.num_unread_msgs(session.user),
                                 htTitle="New project",
                                 form=f)
    #end edit_project

    def make_edit_project(self, name):
        proj = None
        try:
            proj = model.Project(name)
        except:
            raise web.seeother('/')

        if not proj.isadmin(session.user):
            raise web.seeother('/+' + name)

        i = web.input()
        proj2 = proj
        proj2.name = i.name
        proj2.homepage = i.homepage
        proj2.description = i.description
        try:
            proj2.save()
            web.seeother('/' + proj2.name)
        except:
            return render.newproject(errors=["Name already in use."],
                                     proj=proj,
                                     user=session.user,
                                     title=title,
                                     msg_count=model.num_unread_msgs(session.user),
                                     htTitle="New project",
                                     form=f)
    #end make_edit_project
#end Project


if __name__ == "__main__": app.run()
