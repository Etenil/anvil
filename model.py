import web
from anvillib.avatar import gravatar, pavatar
from common import *
from hashlib import sha256

def create_user(name, email, password, homepage, description):
    db.insert('user',
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

def list_users(hint):
    users = db.query('SELECT name FROM user WHERE name LIKE '
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

        users = db.select('user', where=where)
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
        avatar = pavatar(self.homepage)

        if not avatar:
            avatar = gravatar(self.email)

        return avatar

    def save(self):
        db.update('user', where="id=" + web.db.sqlquote(self.id),
                  name=self.name, email=self.email,
                  homepage=self.homepage, description=self.description)
#end User

def get_user_inbox(userid, read=False):
    where = "messages.destination=" + web.db.sqlquote(userid)

    if not read:
        where += " and messages.is_read='0'"

    messages = db.query("SELECT messages.*, user.name AS sender FROM messages "+
                        "JOIN user ON messages.author=user.id "+
                        "WHERE " + where + " ORDER BY created DESC")
    if len(messages) == 0:
        return False
    else:
        return messages
#end get_user_inbox

def num_unread_msgs(username):
    if username != None:
        u = User(name=username)
        counts = db.query("SELECT COUNT(id) AS count FROM messages WHERE destination="
                          + web.db.sqlquote(u.id) + " AND is_read='0'")
        return counts[0].count
    else:
        return False
#end num_unread_msgs

class MessageError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class Message:
    id = None
    sender = None
    dest = None
    subject = ""
    content = ""
    created = ""
    read = False

    def __init__(self, id=None):
        if id != None:
            messages = db.select('messages', where="id=" + web.db.sqlquote(id))
            if len(messages) == 0:
                raise MessageError("No such message.")
            msg = messages[0]
            self.id      = msg.id
            self.sender  = User(id=msg.author)
            self.dest    = User(id=msg.destination)
            self.subject = msg.subject
            self.content = msg.content
            self.created = msg.created
            self.read    = (msg.is_read != 0)

    def save(self):
        if self.id != None:
            num_read = '0'
            if self.read:
                num_read = '1'
            db.update('messages', where="id=" + web.db.sqlquote(self.id),
                      author=self.sender.id, destination=self.dest.id,
                      subject=self.subject, content=self.content,
                      is_read=num_read)
        else:
            num_read = '0'
            if self.read:
                num_read = '1'
            db.insert('messages', author=self.sender.id,
                      destination=self.dest.id, subject=self.subject,
                      content=self.content, is_read=num_read)

    def mark_read(self):
        if self.id == None:
            return False
        db.update('messages', where="id=" + web.db.sqlquote(self.id), is_read='1')

    def mark_unread(self):
        if self.id == None:
            return False
        db.update('messages', where="id=" + web.db.sqlquote(self.id), is_read='0')
#end Message
