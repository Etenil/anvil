import web
import model
from common import *
from web import form
from web.contrib.template import render_mako

urls = (
    '/', 'main',
    '/login', 'login',
    '/logout', 'logout',
    '/register', 'register',
    )

web.config.debug = False
app = web.application(urls, globals())
render = render_mako(
        directories=['templates'],
        input_encoding='utf-8',
        output_encoding='utf-8',
        )

session = web.session.Session(app,
                              web.session.DBStore(db, 'sessions'),
                              initializer={'user': None})

title = "Anvil"


class main:
    def GET(self):
        return render.main(content="Welcome to Anvil",
                           user=session.user,
                           title=title,
                           htTitle="Welcome to Anvil!")
    #end GET
#end test

class login:
    form = form.Form(
        form.Textbox('email'),
        form.Password('password'),
        form.Button('Login')
        )

    def GET(self):
        f = self.form()
        return render.login(form=f,
                            title=title,
                            htTitle="Login")

    def POST(self):
        f = self.form()
        if not f.validates():
            return render.login(form=f,
                                title=title,
                                htTitle="Login")
        i = web.input()
        user = model.user_login(email=i.email, password = i.password)
        if not user:
            return render.login(error="Incorrect username or password.",
                                form=f,
                                title=title,
                                htTitle="Login")
        session.user = user.name
        raise web.seeother('/')

class logout:
    def GET(self):
        session.user = None
        raise web.seeother('/')

class register:
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
        form.Textarea('description'),
        form.Button('Register')
        )

    def GET(self):
        f = self.form()
        return render.register(form=f,
                               title=title,
                               htTitle="Register")

    def POST(self):
        f = self.form()
        if not f.validates():
            return render.register(form=f,
                                   title=title,
                                   htTitle="Register")
        i = web.input()
        try:
            model.create_user(name=i.name,
                              email=i.email,
                              password=i.password,
                              description=i.description)
            session.user = i.name
            raise web.seeother('/')
        except:
            return render.register(error="Username already exists!",
                                   form=f,
                                   title=title,
                                   htTitle="Register")


if __name__ == "__main__": app.run()
