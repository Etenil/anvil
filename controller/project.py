import web
from web import form
import common
from web.contrib.template import render_mako
from anvillib.form import AjaxTextbox
import anvillib.xmlrpc
import model.project
import model.user
import re

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
        elif action == "list":
            return self.list_projects()
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
        return common.render.newproject(htTitle="New project",
                                        form=f)
    #end new_project

    def list_projects(self):
        return common.render.projectslist(projs=model.project.list_proj(),
                                   htTitle="Projects")


    def make_new(self):
        f = self.new_form()
        error = False
        errors = []

        if not f.validates():
            error = True

        i = web.input()
        proj = model.project.Project()
        proj.name = i.name
        proj.owner = model.user.User(name=common.session.user)
        proj.homepage = i.homepage
        proj.description = i.description
        try:
            anvillib.xmlrpc.create_user(proj.name)
            proj.save()
        except:
            error = True
            errors.append("Projects already exists.")

        if error:
            return common.render.newproject(errors=errors,
                                     htTitle="New project",
                                     form=f)
        else:
            raise web.seeother('/' + proj.name)
    #end make_new

    def show_project(self, name):
        """Displays details about project <name>."""
        try:
            proj = model.project.Project(name=name)
        except:
            raise web.seeother('/')

        return common.render.project(proj=proj,
                              canedit=proj.isadmin(common.session.user),
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
        proj = model.project.Project(name)
        if not proj.isadmin(common.session.user):
            raise web.seeother('/' + name)

        f = self.make_edit_form(proj)
        return common.render.newproject(proj=proj,
                                 htTitle="New project",
                                 form=f)
    #end edit_project

    def make_edit_project(self, name):
        proj = None
        try:
            proj = model.project.Project(name)
        except:
            raise web.seeother('/')

        if not proj.isadmin(common.session.user):
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
            return common.render.newproject(errors=["Name already in use."],
                                     proj=proj,
                                     htTitle="New project",
                                     form=f)
    #end make_edit_project
#end Project
