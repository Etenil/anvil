import web
import common

from controller.user import User
from controller.project import Project
from controller.message import Message
from controller.bug import Bug
from controller.doc import Doc

import model.project
import model.message

urls = (
    '/'                                            , 'Main',
    '/(login)'                                     , 'User',
    '/(logout)'                                    , 'User',
    '/(register)'                                  , 'User',
    '/(profile)'                                   , 'User',
    '/(users)'                                     , 'User',
    '/message(?:/(.+))?$'                          , 'Message',
    '/ajax/(listusers)'                            , 'User',
    '/project(?:/(.+))?$'                          , 'Project',
    '/\*([a-z0-9._-]+)$'                           , 'User',
    '/\*([a-z0-9._-]+)/(key)(?:/(.+?)(?:/(.+))?)?$' , 'User',
    '/([a-z0-9._-]+)/bugs(?:/(.+?)(?:/(.+))?)?$'   , 'Bug',
    '/([a-z0-9._-]+)/doc(?:/(.+?)(?:/(.+))?)?$'    , 'Doc',
    '/([a-z0-9._-]+)(?:/(.+))?$'                   , 'Project', #Leave me at the bottom!
    )

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
    #end GET
#end test

if __name__ == "__main__": app.run()

