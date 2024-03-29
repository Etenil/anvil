import web
from web import form
import common
from web.contrib.template import render_mako
from anvillib.form import AjaxTextbox
import anvillib.fs
import anvillib.bzr
import anvillib.sh
import model.project
import model.user
from model import event
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

    def GET(self, action=None, other=None, arg1=None, arg2=None, arg3=None):
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
            elif other == "branch" and arg1 != None and arg2 == "source":
                return self.show_tree(name, arg1)
            elif other == "branch" and arg1 != None and arg2 == "file" and arg3 != None:
                return self.get_branch_file(name, arg1, arg3)
            elif other == "branch" and arg1 != None and arg2 == "feed":
                return self.branch_rss(name, arg1)
            elif other == "branch" and arg1 != None:
                return self.show_branch(name, arg1)
            elif other == "commiters":
                if arg1 == "add":
                    return self.add_commiter(name, arg2)
                else:
                    return self.rem_commiter(name, arg2)
            elif other == "events":
                return self.events_rss(name)
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
        try:
            anvillib.fs.create_project(proj.name)
            proj.save()
        except:
            error = True
            errors.append("Project already exists.")
        else:
            proj.add_commiter(proj.owner.id)
            event.add(user=proj.owner.id, type=event.EV_PROJECT,
                      project=proj.id,
                      link=config.prefix + '/' + proj.name,
                      msg="%s created project %s" % (proj.owner.name, proj.name))

        if error:
            raise Exception(error)
            return common.render.newproject(htTitle="New project",
                                            form=f)
        else:
            raise web.seeother(config.prefix + '/' + proj.name)
    #end make_new

    def show_project(self, name):
        """Displays details about project <name>."""
        try:
            proj = model.project.Project(name=name)
            branches = anvillib.bzr.list_project_branches(name)
            return common.render.project(proj=proj,
                                         is_project=True,
                                         is_main=False,
                                         canedit=proj.isadmin(common.session.user),
                                         branches=branches,
                                         activity=model.event.get_project_events(proj.id),
                                         commiters=proj.get_commiters(),
                                         htTitle="Project")
        except:
            raise web.notfound()

    def events_rss(self, projectname):
        try:
            proj = model.project.Project(name=projectname)
            activity = model.event.get_project_events(proj.id, 0, 30)
            web.header('Content-Type', 'text/xml')
            link = "http://%s/%s/%s" % (config.val('host'),
                                        config.val('prefix'),
                                        projectname)
            link = link.replace("//", "/")
            return common.render.eventsrss(is_main=False,
                                           project=proj,
                                           activity=activity,
                                           htTitle="Events for project %s" % projectname,
                                           link=link)
        except:
            web.header('Content-Type', 'text/html')
            return web.notfound()

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
        else:
            event.add(user=proj2.owner.id, type=event.EV_PROJECT,
                      project=proj2.id,
                      link=config.prefix + '/' + proj.name,
                      msg=("Edited project %s" % proj2.name))
    #end make_edit_project

    def show_branch(self, project, branch):
        p = model.project.Project(name=project)
        canedit = p.isadmin(common.session.user)
        log = anvillib.bzr.get_project_branch_log(p.name, branch)
        return common.render.branch(branch=branch,
                                    canedit=canedit,
                                    log=log,
                                    item=p.name,
                                    is_project=True,
                                    htTitle="Branch " + branch)

    def branch_rss(self, project, branch):
        feed = anvillib.bzr.get_project_branch_rss(project, branch)
        link = "http://%s/%s/%s/branch/%s" % (config.val('host'),
                                              config.val('prefix'),
                                              project, branch)
        link = link.replace("//", "/")
        feed = feed.replace("$l", link)
        web.header('Content-Type', 'text/xml')
        return common.render.rss(link=link,
                                 feed=feed,
                                 htTitle="Branch " + branch)

    def show_tree(self, project, branch):
        p = model.project.Project(name=project)
        canedit = p.isadmin(common.session.user)
        tree = anvillib.bzr.get_project_branch_tree(project, branch)
        tree.pop(0)
        return common.render.branchtree(branch=branch,
                                        canedit=canedit,
                                        tree=tree,
                                        item=p.name,
                                        is_project=True,
                                        htTitle="Branch " + branch)

    def get_branch_file(self, project, branch, fileid):
        p = model.project.Project(name=project)
        canedit = p.isadmin(common.session.user)
        f = anvillib.bzr.get_project_branch_file(project, branch, fileid)
        return common.render.branchfile(branch=branch,
                                        canedit=canedit,
                                        file_title=f[0],
                                        file_contents=f[1],
                                        brush=anvillib.sh.brush(f[0]),
                                        item=project,
                                        is_project=True,
                                        htTitle="Branch " + branch)

    def del_branch(self, project, branch):
        p = model.project.Project(name=project)
        if p.isadmin(common.session.user):
            try:
                anvillib.fs.delete_project_branch(project, branch)
            except:
                pass
            else:
                event.add(username=common.session.user, type=event.EV_PROJECT,
                          project=p.id,
                          link=config.prefix + '/' + proj.name,
                          msg=("Deleted branch %s of project %s" % (branch, p.name)))
        raise web.seeother(config.prefix + '/' + project)

    def add_commiter(self, proj_name, commiter_name):
        proj = model.project.Project(name=proj_name)
        if proj.isadmin(common.session.user):
            try:
                commiter = model.user.User(name=commiter_name)
            except:
                return web.notfound()
            # Checking if the commiter is already linked.
            commiters = proj.get_commiters()
            for c in commiters:
                if c.id == commiter.id:
                    return web.forbidden()
            # OK, we add.
            proj.add_commiter(commiter.id)
            event.add(username=common.session.user, type=event.EV_PROJECT,
                      project=proj.id,
                      link=config.prefix + '/' + proj.name,
                      msg=("Added user %s to project %s as commiter" % (commiter_name, proj_name)))
            return ""
        else:
            return web.forbidden()

    def rem_commiter(self, proj_name, commiter_name):
        proj = model.project.Project(name=proj_name)
        if proj.isadmin(common.session.user):
            try:
                commiter = model.user.User(name=commiter_name)
            except:
                a = 2
            else:
                proj.rem_commiter(commiter.id)
                event.add(username=common.session.user, type=event.EV_PROJECT,
                          project=proj.id,
                          link=config.prefix + '/' + proj.name,
                          msg=("Removed user %s from project %s" % (commiter_name, proj_name)))
        raise web.seeother(config.prefix + '/' + proj_name)
#end Project
