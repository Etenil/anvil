import web
from web import form
import common
from web.contrib.template import render_mako
from anvillib.form import AjaxTextbox
import model.message
import model.user
import re
from anvillib import config

class Message:
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
            raise web.seeother(config.prefix + '/message/list')


    def list_messages(self, extra):
        user = model.user.User(name=common.session.user)
        read = (extra != None)
        msgs = model.message.get_user_inbox(user.id, read)
        return common.render.messages(msgs=msgs,
                               show_all=read,
                               u=user,
                               htTitle="Inbox")

    def get_message(self, msgid):
        msg = model.message.Message(msgid)
        # Marking read
        msg.read = True
        msg.mark_read()
        return common.render.message(msg=msg,
                                     htTitle="Message")
    def new_message(self):
        return common.render.newmessage(htTitle="New message",
                                 form=self.new_form)

    def make_new_message(self):
        msg = model.message.Message()
        i = web.input()
        user = model.user.User(name=common.session.user)
        dests = i.to.split(',')

        errors = []
        for dest_name in dests:
            name = dest_name.strip()
            try:
                dest = model.user.User(name=name)
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
            return common.render.newmessage(error="<br />".join(errors),
                                     htTitle="New message",
                                     form=self.new_form)
        raise web.seeother(config.prefix + '/message/list')
