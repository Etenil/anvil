import web
from anvillib.avatar import avatar, logo
import common
import user

def get_user_inbox(userid, read=False):
    where = "messages.destination=" + web.db.sqlquote(userid)

    if not read:
        where += " and messages.is_read='0'"

    messages = common.db.query("SELECT messages.*, user.name AS sender FROM messages "+
                        "JOIN user ON messages.author=user.id "+
                        "WHERE " + where + " ORDER BY created DESC")
    if len(messages) == 0:
        return False
    else:
        return messages
#end get_user_inbox

def num_unread_msgs(username):
    if username != None:
        u = user.User(name=username)
        counts = common.db.query("SELECT COUNT(id) AS count FROM messages WHERE destination="
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
            messages = common.db.select('messages', where="id=" + web.db.sqlquote(id))
            if len(messages) == 0:
                raise MessageError("No such message.")
            msg = messages[0]
            self.id      = msg.id
            self.sender  = user.User(id=msg.author)
            self.dest    = user.User(id=msg.destination)
            self.subject = msg.subject
            self.content = msg.content
            self.created = msg.created
            self.read    = (msg.is_read != 0)

    def save(self):
        if self.id != None:
            num_read = '0'
            if self.read:
                num_read = '1'
            common.db.update('messages', where="id=" + web.db.sqlquote(self.id),
                      author=self.sender.id, destination=self.dest.id,
                      subject=self.subject, content=self.content,
                      is_read=num_read)
        else:
            num_read = '0'
            if self.read:
                num_read = '1'
            common.db.insert('messages', author=self.sender.id,
                      destination=self.dest.id, subject=self.subject,
                      content=self.content, is_read=num_read)

    def mark_read(self):
        if self.id == None:
            return False
        common.db.update('messages', where="id=" + web.db.sqlquote(self.id), is_read='1')

    def mark_unread(self):
        if self.id == None:
            return False
        common.db.update('messages', where="id=" + web.db.sqlquote(self.id), is_read='0')
#end Message
