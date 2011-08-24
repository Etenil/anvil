import web
import model
from common import *
from web import form
from web.contrib.template import render_mako
from anvillib.form import AjaxTextbox

urls = (
    '/', 'Main',
    '/login', 'Login',
    '/logout', 'Logout',
    '/register', 'Register',
    '/\*([a-z0-9._-]+)$', 'User',
    '/\*([a-z0-9._-]+)/edit$', 'UserProfile',
    '/messages(?:/(.+))?$', 'UserMessages',
    '/message/(\d+)$', 'UserMessage',
    '/message/new$', 'NewMessage',
    '/ajax/listusers', 'AjaxListUsers',
    )

app = web.application(urls, globals())
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
                              msg_count=model.num_unread_msgs(session.user),
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

    def GET(self, username):
        try:
            self.user = model.User(name=username)
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

    def POST(self, username):
        self.user = model.User(name=username)
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

class UserMessages:
    def GET(self, extra=None):
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

class UserMessage:
    def GET(self, msgid):
        msg = model.Message(msgid)
        # Marking read
        msg.read = True
        msg.mark_read()
        return render.message(msg=msg,
                              user=session.user,
                              msg_count=model.num_unread_msgs(session.user),
                              title=title,
                              htTitle="Message")

class NewMessage:
    f = form.Form(AjaxTextbox('to', '/ajax/listusers'),
                  form.Textbox('subject'),
                  form.Textarea('message'),
                  form.Button('Send'))

    def GET(self):
        return render.newmessage(user=session.user,
                                 title=title,
                                 msg_count=model.num_unread_msgs(session.user),
                                 htTitle="New message",
                                 form=self.f)

    def POST(self):
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
                                     form=self.f)
        raise web.seeother('/*' + username + "/messages")

class AjaxListUsers:
    def POST(self):
        i = web.input()
        users = model.list_users(i.value)
        if users != False:
            return render.autocomplete(users=users)
        else:
            return ""

if __name__ == "__main__": app.run()
