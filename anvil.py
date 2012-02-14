#!/usr/bin/python

import web
import common
import sys

from controller.user import User
from controller.project import Project
from controller.message import Message
from controller.bug import Bug
from controller.doc import Doc

import model.project
import model.message
from anvillib import config

### Parsing the configuration
config.load_conf()

# Generating an argv from the config file (for web.py; pretty dirty I
# know).
sys.argv = ['anvil.py', config.val('port')]

### URL mapping

urls = (
    '/'                                                , 'Main',
    '/(login)'                                         , 'User',
    '/(logout)'                                        , 'User',
    '/(register)'                                      , 'User',
    '/(profile)'                                       , 'User',
    '/(users)'                                         , 'User',
    '/message(?:/(.+))?$'                              , 'Message',
    '/ajax/(listusers)'                                , 'User',
    '/project(?:/(.+))?$'                              , 'Project',
    '/\*([a-z0-9._-]+)$'                               , 'User',
    '/\*([a-z0-9._-]+)/(key)(?:/(.+?)(?:/(.+))?)?$'    , 'User',
    '/\*([a-z0-9._-]+)/(branch)(?:/(.+?)(?:/(.+))?)?$' , 'User',
    '/([a-z0-9._-]+)/bugs(?:/(.+?)(?:/(.+))?)?$'       , 'Bug',
    '/([a-z0-9._-]+)/doc(?:/(.+?)(?:/(.+))?)?$'        , 'Doc',
    '/([a-z0-9._-]+)/(commiters)/(del|add)/(.+)$'        , 'Project',
    '/([a-z0-9._-]+)/(branch)/(.+?)(?:/(.+))?$'        , 'Project',
    '/([a-z0-9._-]+)(?:/(.+))?$'                       , 'Project', #Leave me at the bottom!
    '.*'                                               , 'Main',
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
    return handler()

app.add_processor(refresh_messages)

# Default page in case we don't know what to do (shouldn't happen).
class Main:
    def GET(self):
        return common.render.main(content="Welcome to " + config.val('title'),
                                  num_proj=model.project.count_proj(),
                                  htTitle="Welcome to " + config.val('title') + "!")

# Defining the mode
if config.val('mode') == 'fcgi':
    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)

# Serving.
if __name__ == "__main__": app.run()
