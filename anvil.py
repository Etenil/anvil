#!/usr/bin/python

import web
import common
import sys
import os

from controller.user import User
from controller.project import Project
from controller.message import Message
from controller.bug import Bug
from controller.doc import Doc

import model.project
import model.message
import model.event
from anvillib import config

### Parsing the configuration
config.load_conf()

# Generating an argv from the config file (for web.py; pretty dirty I
# know).
sys.argv = ['anvil.py', config.val('port')]

### URL mapping

urls = (
    '/'                                                          , 'Main',
    '/(login)'                                                   , 'User',
    '/(logout)'                                                  , 'User',
    '/(register)'                                                , 'User',
    '/(profile)'                                                 , 'User',
    '/(users)'                                                   , 'User',
    '/message(?:/(.+))?$'                                        , 'Message',
    '/ajax/(listusers)'                                          , 'User',
    '/project(?:/(.+))?$'                                        , 'Project',
    '/\*([a-z0-9._-]+)$'                                         , 'User',
    '/\*([a-z0-9._-]+)/(key)(?:/(.+?)(?:/(.+))?)?$'              , 'User',
    '/\*([a-z0-9._-]+)/(branch)(?:/(.+?)(?:/(.+?)(?:/(.+))?)?)?$' , 'User',
    '/([a-z0-9._-]+)/bugs(?:/(.+?)(?:/(.+))?)?$'                 , 'Bug',
    '/([a-z0-9._-]+)/doc(?:/(.+?)(?:/(.+))?)?$'                  , 'Doc',
    '/([a-z0-9._-]+)/(commiters)/(del|add)/(.+)$'                , 'Project',
    '/([a-z0-9._-]+)/(branch)/(.+?)(?:/(.+?)(?:/(.+))?)?$'        , 'Project',
    '/([a-z0-9._-]+)(?:/(.+))?$'                                 , 'Project', #Leave at bottom!
    '.*'                                                         , 'Main',
    )

### Runing the server

app = web.application(urls, globals(), autoreload=False)
common.session = web.session.Session(app,
                                     web.session.DBStore(common.db, 'sessions'),
                                     initializer={'user': None})

# This is a hook that is run on every request handling. This ensures
# we always display the number of unread messages to the user.
def refresh_messages(handler):
    common.msgs = model.message.num_unread_msgs(common.session.user)
    web.header('Content-Type', 'text/html')
    return handler()

app.add_processor(refresh_messages)

# Default page in case we don't know what to do (shouldn't happen).
class Main:
    def GET(self):
        activity = model.event.get_events(0, 30)
        custom_logged_page=None
        custom_visitor_page=None
        if os.path.exists("custom.logged.html"):
            f = open("custom.logged.html")
            custom_logged_page = f.read()
            f.close()
        if os.path.exists("custom.visitor.html"):
            f = open("custom.visitor.html")
            custom_visitor_page = f.read()
            f.close()
        return common.render.main(content="Welcome to " + config.val('title'),
                                  num_proj=model.project.count_proj(),
                                  activity=activity,
                                  custom_logged_page=custom_logged_page,
                                  custom_visitor_page=custom_visitor_page,
                                  htTitle="Welcome to " + config.val('title') + "!")

# Defining the mode
if config.val('mode') == 'fcgi':
    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)

# Serving.
if __name__ == "__main__": app.run()
