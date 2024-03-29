import web
from web import form
import common
from web.contrib.template import render_mako
from anvillib.form import AjaxTextbox
import anvillib.bzr
import anvillib.fs
import anvillib.ssh
import anvillib.sh
import model.user
import model.sshkey
import model.project
from model import event
from anvillib import email
import re
from anvillib import config

class User:
    user = None

    login_form = form.Form(
        form.Textbox('email'),
        form.Password('password'),
        form.Button('Login')
        )

    key_form = form.Form(
        form.Textarea('key'),
        form.Button('Add')
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

    def GET(self, action=None, item=None, extra=None, more=None, moremore=None):
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
        elif item == "key":
            if extra != None and re.match("^\d+$", extra) and more == "delete":
                return self.do_del_key(action, extra)
            return self.list_keys(action)
        elif item == "branch" and extra != None:
            if more == "delete":
                return self.del_branch(action, extra)
            elif more == "source":
                return self.show_tree(action, extra)
            elif more == "feed":
                return self.branch_rss(action, extra)
            elif more == "file" and moremore != None:
                return self.get_branch_file(action, extra, moremore)
            else:
                return self.show_branch(action, extra)
        elif item == "events":
            return self.events_rss(action)
        else:
            return self.show_user(action)

    def POST(self, action=None, item=None, extra=None, more=None):
        if action == "listusers":
            return self.list_users_ajax()
        elif action == "profile":
            return self.do_edit_profile()
        elif action == "login":
            return self.do_login()
        elif action == "register":
            return self.do_register()
        elif item == "key":
            if extra == "new":
                return self.do_new_key(action)
            return self.list_keys(action)
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
            anvillib.fs.create_user(i.name)
            # Adding the user
            model.user.create_user(name=i.name,
                                   email=i.email,
                                   password=i.password,
                                   homepage=i.homepage,
                                   description=i.description)
            common.session.user = i.name
            event.add(username=i.name, type=event.EV_USER,
                      link=config.prefix + '/*' + i.name,
                      msg=("%s registered to %s" % (i.name, config.val('title'))))
            email.send("noreply@anvil.com", i.email, "Welcome to Anvil",
                       """Thank you for registering on Anvil.""")
            raise web.seeother(config.prefix + '/*' + i.name)
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
        raise web.seeother(config.prefix + '/')

    def show_user(self, username):
        try:
            user = model.user.User(name=username)
            canedit = (common.session.user == user.name)
            branches = anvillib.bzr.list_user_branches(user.name)
            projects = model.project.get_user_projects(user)
            activity = model.event.get_user_events(user.id, 0, 30)
            return common.render.profile(canedit=canedit,
                                         projs=projects,
                                         user=user,
                                         is_main=False,
                                         activity=activity,
                                         branches=branches,
                                         htTitle="Profile")
        except model.user.UserError as error:
            #raise web.seeother(config.prefix + '/')
            return common.render.main(content=str(error),
                               num_proj=model.project.count_proj(),
                               htTitle="Welcome to Anvil!")

    def events_rss(self, username):
        try:
            user = model.user.User(name=username)
            activity = model.event.get_user_events(user.id, 0, 30)
            web.header('Content-Type', 'text/xml')
            link = "http://%s/%s/*%s" % (config.val('host'),
                                         config.val('prefix'),
                                         username)
            link = link.replace("//", "/")
            return common.render.eventsrss(is_main=False,
                                           user=user,
                                           activity=activity,
                                           htTitle="Events for %s" % username,
                                           link=link)
        except:
            web.header('Content-Type', 'text/html')
            return web.notfound()

    def list_users(self):
        users = model.user.list_users()
        return common.render.listusers(users=users,
                                htTitle="Users")

    def make_profile_form(self):
        f = form.Form(form.Textbox('email',
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
            #raise web.seeother(config.prefix + '/')
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
        self.user.email = i.email
        self.user.homepage = i.homepage
        self.user.description = i.description
        try:
            self.user.save()
            raise web.seeother(config.prefix + '/*' + self.user.name)
        except:
            return common.render.register(error="Username already exists!",
                                          form=f,
                                          htTitle="Register")

    def list_keys(self, username):
        user = model.user.User(name=username)
        if user.name != common.session.user:
            raise web.seeother(config.prefix + '/*' + username)
        keys = model.sshkey.get_keys(user.id)
        f = self.key_form()
        return common.render.keylist(keys=keys,
                                     form=f,
                                     user=username,
                                     htTitle="SSH Keys")

    def do_new_key(self, username):
        user = model.user.User(name=username)
        if user.name != common.session.user:
            raise web.seeother(config.prefix + '/*' + username)

        # Does the key already exist?
        i = web.input()
        if not model.sshkey.has_key(i.key):
            key = model.sshkey.SSHKey()
            key.user = user.id
            key.key = i.key
            key.save()
            anvillib.ssh.regenerate_keys()
        raise web.seeother(config.prefix + '/*' + username + '/key')

    def do_del_key(self, username, key):
        user = model.user.User(name=username)
        if user.name != common.session.user:
            raise web.seeother(config.prefix + '/*' + username)

        key = model.sshkey.SSHKey(id=key)

        if user.id == key.user:
            try:
                key.delete()
                anvillib.ssh.regenerate_keys()
            except:
                pass
        raise web.seeother(config.prefix + '/*' + username + '/key')

    def show_branch(self, username, branch):
        user = model.user.User(name=username)
        canedit = (common.session.user == user.name)
        log = anvillib.bzr.get_user_branch_log(user.name, branch)
        return common.render.branch(branch=branch,
                                    canedit=canedit,
                                    log=log,
                                    is_project=False,
                                    item=username,
                                    htTitle="Branch " + branch)

    def show_tree(self, username, branch):
        user = model.user.User(name=username)
        canedit = (common.session.user == user.name)
        tree = anvillib.bzr.get_user_branch_tree(username, branch)
        tree.pop(0)
        return common.render.branchtree(branch=branch,
                                        canedit=canedit,
                                        tree=tree,
                                        item=username,
                                        is_project=False,
                                        htTitle="Branch " + branch)

    def branch_rss(self, username, branch):
        user = model.user.User(name=username)
        canedit = (common.session.user == user.name)
        feed = anvillib.bzr.get_user_branch_rss(user.name, branch)
        link = "http://%s/%s/*%s/branch/%s" % (config.val('host'),
                                       config.val('prefix'),
                                       username, branch)
        link = link.replace("//", "/")
        feed = feed.replace("$l", link)
        web.header('Content-Type', 'text/xml')
        return common.render.rss(link=link,
                                 feed=feed,
                                 htTitle="Branch " + branch)

    def get_branch_file(self, username, branch, fileid):
        user = model.user.User(name=username)
        canedit = (common.session.user == user.name)
        f = anvillib.bzr.get_user_branch_file(username, branch, fileid)
        return common.render.branchfile(branch=branch,
                                        canedit=canedit,
                                        file_title=f[0],
                                        file_contents=f[1],
                                        item=username,
                                        is_project=False,
                                        brush=anvillib.sh.brush(f[1]),
                                        htTitle="Branch " + branch)

    def del_branch(self, username, branch):
        user = model.user.User(name=username)
        if user.name == common.session.user:
            try:
                anvillib.fs.delete_user_branch(username, branch)
            except:
                pass
            else:
                event.add(user=user.id, type=event.EV_USER,
                          link=config.prefix + '/*' + username,
                          msg=("%s deleted branch %s" % (username, branch)))
        raise web.seeother(config.prefix + '/*' + username)
