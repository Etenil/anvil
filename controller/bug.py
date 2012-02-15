import web
from web import form
import common
from web.contrib.template import render_mako
from anvillib.form import AjaxTextbox
import model.bug
import model.project
import model.user
import model.bugcomment
from model import event
import re
from anvillib import config

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

    new_comm_form = form.Form(form.Textarea('comment', form.notnull),
                              form.Button('Send'))

    def GET(self, project=None, action=None, extra=None):
        if project == None:
            raise web.seeother(config.prefix + '/')
        elif action == None:
            return self.list_bugs(project)
        elif action == "all":
            return self.list_bugs(project, True)
        elif re.match("^\d+$", action) and extra == "edit":
            return self.edit_bug(project, action)
        elif re.match("^\d+$", action):
            return self.show_bug(project, action)
        elif action == "new":
            return self.new_bug(project)
        else:
            raise web.seeother(config.prefix + '/')

    def POST(self, project=None, action=None, extra=None):
        if project == None:
            raise web.seeother(config.prefix + '/')
        if action == "new":
            self.do_new_bug(project)
        elif re.match("^\d+$", action) and extra == "newcomm":
            return self.do_add_comment(project, action)
        elif re.match("^\d+$", action) and extra == "edit":
            return self.do_edit_bug(project, action)
        else:
            raise web.seeother(config.prefix + '/' + project + '/bugs')

    def list_bugs(self, project, closed=False):
        proj = model.project.Project(name=project)
        bugs = model.bug.get_bugs(project=proj.id, open_only=(not closed))
        return common.render.bugs(bugs=bugs,
                                  show_all=closed,
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
            event.add(user=common.session.user, project=project,
                      type=event.EV_BUG,
                      link=(config.prefix + '/' + project + '/bugs/' + bug.id),
                      msg=("Bug %d added" % bug.id))
        except:
            pass
        raise web.seeother(config.prefix + '/' + project + '/bugs')

    def show_bug(self, project, num):
        bug = model.bug.Bug(num)
        if bug.project.name != project:
            raise web.seeother(config.prefix + '/' + project + '/bugs')
        else:
            f = self.new_comm_form()
            p = model.project.Project(name=project)
            comms = model.bugcomment.get_bug_comments(num)
            return common.render.bug(bug=bug,
                                     can_edit=p.isadmin(common.session.user),
                                     comm_form=f,
                                     comms=comms,
                                     htTitle="Bug #" + str(bug.id))

    def do_add_comment(self, project, bugnum):
        i = web.input()
        comm = model.bugcomment.BugComment()
        comm.bug = bugnum
        comm.message = i.comment

        if common.session.user != None:
            user = model.user.User(name=common.session.user)
            comm.author = user.name
            comm.author_email = user.email
            comm.extern = False
        else:
            comm.author = i.name
            comm.author_email = i.email
            comm.extern = True

        try:
            comm.save()
            event.add(user=common.session.user,
                      project=project, type=event.EV_BUG,
                      link=config.prefix + '/' + project + '/bugs/' + bugnum,
                      msg=("Comment added to bug %d" % bugnum))
        except:
            a = 1
        raise web.seeother(config.prefix + '/' + project + '/bugs/' + bugnum)

    def _make_edit_form(self, proj, bug):
        p = model.project.Project(name=proj)
        devs = p.members()
        dev_options = [('*none', 'No one')]
        for dev in devs:
            dev_options.append((dev.name, dev.name))
        f = form.Form(form.Textbox('version', form.notnull, value=bug.version),
                      form.Dropdown('assigned_to', dev_options, description="assigned to"),
                      form.Dropdown('status',
                                    [(0, 'new'),
                                     (1, 'confirmed'),
                                     (2, 'assigned'),
                                     (3, 'closed'),
                                     (4, 'rejected')],
                                    value=bug.status),
                      form.Textarea('comment'),
                      form.Button('Save'))
        return f()


    def edit_bug(self, project, bugnum):
        p = model.project.Project(name=project)
        if not p.isadmin(common.session.user):
            raise web.seeother(config.prefix + '/' + project + '/bugs/' + bugnum)
        bug = model.bug.Bug(bugnum)
        return common.render.bugedit(proj=project,
                                     bug=bug,
                                     form=self._make_edit_form(project, bug),
                                     htTitle="Bug #" + str(bug.id))

    def do_edit_bug(self, project, bugnum):
        p = model.project.Project(name=project)
        if not p.isadmin(common.session.user):
            raise web.seeother(config.prefix + '/' + project + '/bugs/' + bugnum)

        comm = model.bugcomment.BugComment()

        # Saving bug
        i = web.input()
        bug = model.bug.Bug(bugnum)
        assignee = None
        if i.assigned_to != "*none" and (bug.assigned_to == None or i.assigned_to != bug.assigned_to.name):
            assignee = model.user.User(name=i.assigned_to)
            bug.assigned_to = assignee
            comm.message += '<p class="system-msg">Assigned to ' + assignee.name + '</p>'
        elif bug.assigned_to != None:
                bug.assigned_to = None
                comm.message += '<p class="system-msg">Bug unassigned</p>'

        if bug.status != int(i.status):
            bug.status = int(i.status)
            comm.message += '<p class="system-msg">Status changed to ' + bug.get_status() + '</p>'
        if bug.version != i.version:
            bug.version = i.version
            comm.message += '<p class="system-msg">Version changed to ' + bug.version + '</p>'
        event.add(user=common.session.user,
                  project=project, type=EV_BUG,
                  link=config.prefix + '/' + project + '/bugs/' + bugnum,
                  msg=("Bug %d edited: %s" % (bug.id, i.comment)))
        bug.save()

        # Adding comment
        user = model.user.User(name=common.session.user)
        comm.author = user.name
        comm.author_email = user.email
        comm.extern = False
        comm.bug = bugnum
        comm.message += i.comment

        comm.save()
        #except:
        #    a = 1
        raise web.seeother(config.prefix + '/' + project + '/bugs/' + bugnum)
