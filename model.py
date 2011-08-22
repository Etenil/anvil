import web
from common import *
from hashlib import sha256

def create_user(name, email, password, description):
    db.insert('user',
              name=name,
              email=email,
              password=sha256(password).hexdigest(),
              description=description)
#end create_user

def user_login(email, password):
    result = db.select('user', where="email="+web.db.sqlquote(email)+
                       " and password="+web.db.sqlquote(sha256(password).hexdigest()))
    if(result == 0):
        return False
    else:
        return User(result[0].id)
#end user_login

class User:
    id = 0
    name = ""
    email = ""
    created = 0
    description = ""

    def __init__(self, id):
        users = db.select('user', where="id=" + web.db.sqlquote(id))
        if len(users) > 0:
            user = users[0]
            self.id          = user.id
            self.name        = user.name
            self.email       = user.email
            self.created     = user.created
            self.description = user.description
    #end __init__
#end User
