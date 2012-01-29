#!/usr/bin/python

import web
import common
import sys
import ConfigParser

from controller.user import User
from controller.project import Project
from controller.message import Message
from controller.bug import Bug
from controller.doc import Doc

import model.project
import model.message

### Parsing the configuration

conf = ConfigParser.RawConfigParser();

if len(sys.argv) > 1:
    conf.read(sys.argv[1])

port = '80'
mode = 'http'

if conf.has_option('anvil', 'port'):
    port = conf.get('anvil', 'port')

if conf.has_option('anvil', 'mode'):
    mode = conf.get('anvil', 'mode')

# Generating an argv from the config file (for web.py; pretty dirty I know).
sys.argv = [port]


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
    '/([a-z0-9._-]+)/(branch)/(.+?)(?:/(.+))?$'        , 'Project',
    '/([a-z0-9._-]+)(?:/(.+))?$'                       , 'Project', #Leave me at the bottom!
    '.*'                                               , 'Main',
    )

### Runing the server

app = web.application(urls, globals(), autoreload=False)
common.session = web.session.Session(app,
                                     web.session.DBStore(common.db, 'sessions'),
                                     initializer={'user': None})

def refresh_messages(handler):
    common.msgs = model.message.num_unread_msgs(common.session.user)
    return handler()

app.add_processor(refresh_messages)

class Main:
    def GET(self):
        return common.render.main(content="Welcome to Anvil",
                                  num_proj=model.project.count_proj(),
                                  htTitle="Welcome to Anvil!")

if mode == 'fcgi':
    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)

if __name__ == "__main__": app.run()

