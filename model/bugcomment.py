import web
from anvillib.avatar import avatar, logo
import common
import user
import bug

def get_bug_comments(bug):
    rcomms = common.db.select('bug_comments', where="bug=" + web.db.sqlquote(bug))
    comms = []
    for rcomm in rcomms:
        comms.append(BugComment(row=rcomm))
    return comms

class BugComment:
    id = None
    bug = None
    author = ""
    author_email = ""
    extern = False
    message = ""
    created = ""

    def __init__(self, id=None, row=None):
        if id != None:
            comments = common.db.select('bug_comments', where="id=" + web.db.sqlquote(id))
            if len(comments) == 0:
                raise bug.BugError("Comment not found.")
            row = comments[0]
        if row != None:
            self.id = row.id
            self.bug = row.bug
            self.author = row.author
            self.email = row.author_email
            self.extern = (row.is_extern != 0)
            self.message = row.message
            self.created = row.created

    def save(self):
        extern = '0'
        if self.extern:
            extern = '1'
        if self.id != None:
            common.db.update('bug_comments', where="id=" + web.db.sqlquote(self.id),
                             bug=self.bug, author=self.author,
                             author_email=self.author_email, is_extern=extern,
                             message=self.message, created=web.db.sqlliteral('NOW()'))
        else:
            common.db.insert('bug_comments',
                             bug=self.bug, author=self.author,
                             author_email=self.author_email, is_extern=extern,
                             message=self.message)
