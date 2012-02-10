import web
from anvillib.avatar import avatar, logo
import common
from hashlib import sha256
import re

def create_user(name, email, password, homepage, description):
    if not re.match('^https?://', homepage):
        homepage = 'http://' + homepage
    common.db.insert('user',
                     name=name,
                     email=email,
                     homepage=homepage,
                     password=sha256(password).hexdigest(),
                     description=description)
#end create_user

def user_login(email, password):
    try:
        user = User(email=email)
        if user.checkpassword(password):
            return user
        else:
            return False
    except UserError:
        return False
#end user_login

def get_user_proj():
    try:
        user = User(name=common.session.user)
    except:
        return False
    return common.db.select('project', where="owner=" + web.db.sqlquote(user.id))
#end get_user_proj

def list_users(hint=False):
    if not hint:
        users = common.db.query('SELECT * FROM user ORDER BY name')
    else:
        users = common.db.query('SELECT * FROM user WHERE name LIKE '
                         + web.db.sqlquote("%" + hint + "%")
                         + " ORDER BY name")
    if len(users) < 1:
        return False
    else:
        return users

class UserError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class User:
    id = 0
    name = ""
    email = ""
    password = ""
    created = 0
    homepage = ""
    description = ""

    def __init__(self, id=None, name=None, email=None):
        where = ""
        if id != None:
            where = "id=" + web.db.sqlquote(id)
        elif email != None:
            where = "email=" + web.db.sqlquote(email)
        elif name != None:
            where = "name=" + web.db.sqlquote(name)

        users = common.db.select('user', where=where)
        if len(users) > 0:
            user = users[0]
            self.id          = user.id
            self.name        = user.name
            self.password    = user.password
            self.email       = user.email
            self.created     = user.created
            self.homepage    = user.homepage
            self.description = user.description
        else:
            raise UserError("Unknown user")
    #end __init__

    def checkpassword(self, password):
        if sha256(password).hexdigest() == self.password:
            return True
        else:
            return False
    #end checkpassword

    def avatar(self):
        return avatar(self.homepage, self.email)

    def save(self):
        common.db.update('user', where="id=" + web.db.sqlquote(self.id),
                  name=self.name, email=self.email,
                  homepage=self.homepage, description=self.description)
#end User
