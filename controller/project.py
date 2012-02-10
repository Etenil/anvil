import web
from web import form
import common
from web.contrib.template import render_mako
from anvillib.form import AjaxTextbox
import anvillib.fs
import anvillib.bzr
import model.project
import model.user
import re
from anvillib import config

class Project:
    new_form = form.Form(
        form.Textbox('name',
                     form.notnull,
                     form.regexp('^[a-z0-9._-]+$', "Name must only include low-case letters, digits, '.'. '_' and '-'")),
        form.Textbox('homepage'),
        form.Textarea('description'),
        form.Button('Register'))

    def GET(self, action=None, other=None, arg1=None, arg2=None):
        if action == "new":
            return self.new_project()
        elif action == "list":
            return self.list_projects()
        else:
            name = action
            if other == "edit":
                return self.edit_project(name)
            elif other == "branch" and arg1 != None and arg2 == "delete":
                return self.del_branch(name, arg1)
            elif other == "branch" and arg1 != None:
                return self.show_branch(name, arg1)
            else:
                return self.show_project(name)
    #end GET

    def POST(self, action=None, other=None):
        if action == "new":
            return self.make_new()
        elif other == "edit":
            return self.make_edit_project(action)
        else:
            raise web.seeother(config.prefix + '/')

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
        sshkeys = model.sshkey.get_keys(proj.owner.id)
        try:
            anvillib.fs.create_project(proj.name)
            # Importing SSH keys
            # for k in sshkeys:
            #     k.id = None
            #     anvillib.xmlrpc.add_ssh_key(k.key, proj.name)
            #     k.save()
            # proj.save()
        except:
            error = True
            errors.append("Project already exists.")

        if error:
            return common.render.newproject(htTitle="New project",
                                            form=f)
        else:
            raise web.seeother(config.prefix + '/' + proj.name)
    #end make_new

    def show_project(self, name):
        """Displays details about project <name>."""
        try:
            proj = model.project.Project(name=name)
            branches = anvillib.bzr.list_branches(name)
            return common.render.project(proj=proj,
                                         canedit=proj.isadmin(common.session.user),
                                         branches=branches,
                                         htTitle="Project")
        except:
            raise web.seeother(config.prefix + '/')

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
        proj = model.project.Project(name=name)
        if not proj.isadmin(common.session.user):
            raise web.seeother(config.prefix + '/' + name)

        f = self.make_edit_form(proj)
        return common.render.newproject(proj=proj,
                                 htTitle="New project",
                                 form=f)
    #end edit_project

    def make_edit_project(self, name):
        proj = None
        try:
            proj = model.project.Project(name=name)
        except:
            raise web.seeother(config.prefix + '/')

        if not proj.isadmin(common.session.user):
            raise web.seeother(config.prefix + '/+' + name)

        i = web.input()
        proj2 = proj
        proj2.name = i.name
        proj2.homepage = i.homepage
        proj2.description = i.description
        try:
            proj2.save()
            web.seeother(config.prefix + '/' + proj2.name)
        except:
            return common.render.newproject(errors=["Name already in use."],
                                     proj=proj,
                                     htTitle="New project",
                                     form=f)
    #end make_edit_project

    def show_branch(self, project, branch):
        p = model.project.Project(name=project)
        canedit = p.isadmin(common.session.user)
        log = anvillib.bzr.get_branch_log(p.name, branch)
        return common.render.branch(branch=branch,
                                    canedit=canedit,
                                    log=log,
                                    item=p.name,
                                    is_project=True,
                                    htTitle="Branch " + branch)

    def del_branch(self, project, branch):
        p = model.project.Project(name=project)
        if p.isadmin(common.session.user):
            try:
                anvillib.fs.delete_project_branch(project, branch)
            except:
                pass
        raise web.seeother(config.prefix + '/' + project)
#end Project
