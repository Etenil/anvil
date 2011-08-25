import web
from web import form
import common
from web.contrib.template import render_mako
from anvillib.form import AjaxTextbox
import model.bug
import model.project
import model.user
import re

class Bug:
    new_user_form = form.Form(form.Textbox('summary'),
                              form.Textarea('description'),
                              form.Textbox('version'),
                              form.Button('Send'))

    new_anon_form = form.Form(form.Textbox('summary'),
                              form.Textarea('description'),
                              form.Textbox('version'),
                              form.Textbox('name', form.notnull),
                              form.Textbox('email',
                                           form.notnull,
                                           form.regexp('^[\w-]+(\.[\w-]+)*@([a-z0-9-]+(\.[a-z0-9-]+)*?\.[a-z]{2,6}|(\d{1,3}\.){3}\d{1,3})(:\d{4})?$', 'Invalid email address')),
                              form.Button('Send'))

    def GET(self, project=None, action=None):
        if project == None:
            raise web.seeother('/')
        elif action == None:
            return self.list_bugs(project)
        elif re.match("^\d+$", action):
            return self.show_bug(project, action)
        elif action == "new":
            return self.new_bug(project)
        else:
            raise web.seeother('/')

    def POST(self, project=None, action=None):
        if project == None:
            raise web.seeother('/')
        if action == "new":
            self.do_new_bug(project)
        else:
            raise web.seeother('/' + project + '/bugs')

    def list_bugs(self, project):
        proj = model.project.Project(name=project)
        bugs = model.bug.get_bugs(project=proj.id)
        return common.render.bugs(bugs=bugs,
                                  proj=proj,
                                  htTitle="Bugs")

    def new_bug(self, project):
        form = None
        if common.session.user != None:
            form = self.new_user_form()
        else:
            form = self.new_anon_form()
        return common.render.bugnew(f=form,
                                    proj=project,
                                    htTitle="Report a bug")

    def do_new_bug(self, project):
        i = web.input()
        bug = model.bug.Bug()
        bug.subject = i.summary
        bug.description = i.description
        bug.version = i.version
        bug.project = model.project.Project(name=project)

        f = None
        if common.session.user == None:
            f = self.new_anon_form()
            bug.guest = True
            bug.author_extern = i.name
            bug.author_extern_email = i.email
        else:
            f = self.new_user_form()
            bug.guest = False
            bug.author_intern = model.user.User(name=common.session.user)
        if not f.validates():
            return common.render.bugnew(f=form,
                                        proj=project,
                                        htTitle="Report a bug")
        try:
            bug.save()
        except:
            a = 1
        raise web.seeother('/' + project + '/bugs')

    def show_bug(self, project, num):
        bug = model.bug.Bug(num)
        if bug.project.name != project:
            raise web.seeother('/' + project + '/bugs')
        else:
            return common.render.bug(bug=bug,
                                     htTitle="Bug #" + str(bug.id))
