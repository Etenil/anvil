import web
from anvillib.avatar import avatar, logo
import common
import user
import project

def get_bugs(project=None, user=None, open_only=True):
    where = ""
    if project != None:
        if where != "":
            where += " AND "
        where = "project=" + web.db.sqlquote(project)
    if user != None:
        if where != "":
            where += " AND "
        where += "author_intern=" + web.db.sqlquote(user)
    if open_only:
        if where != "":
            where += " AND "
        where += "status!='3' AND status!='4'"
    rbugs = common.db.select('bugs', where=where)
    bugs = []
    for bug in rbugs:
        bugs.append(Bug(bug.id))
    return bugs

class MessageError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class Bug:
    id = None
    subject = ""
    description = ""
    guest = False
    author_extern = ""
    author_extern_email = ""
    author_intern = None
    project = None
    assigned_to = None
    status = 0
    version = ""
    modified = ""

    def __init__(self, id=None):
        if id != None:
            bugs = common.db.select('bugs', where="id=" + web.db.sqlquote(id))
            if len(bugs) == 0:
                raise BugError("No such bug")
            bug = bugs[0]
            self.id = bug.id
            self.subject = bug.subject
            self.description = bug.description
            self.modified = bug.modified
            self.guest = (bug.guest != 0)
            self.author_extern = bug.author_extern
            self.author_extern_email = bug.author_extern_email
            if not self.guest:
                self.author_intern = user.User(id=bug.author_intern)
            self.project = project.Project(id=bug.project)
            if bug.assigned_to > 0:
                self.assigned_to = user.User(bug.assigned_to)
            self.status = bug.status
            self.version = bug.version

    def get_status(self):
        status = ['new',
                  'confirmed',
                  'assigned',
                  'closed',
                  'rejected']
        return status[self.status]

    def save(self):
        auth_int = web.db.sqlliteral('NULL')
        if self.author_intern != None:
            auth_int = web.db.sqlquote(self.author_intern.id)
        guest = '0'
        if self.guest:
            guest = '1'
        assignee = web.db.sqlliteral('NULL')
        if self.assigned_to != None:
            assignee = web.db.sqlquote(self.assigned_to.id)
        if self.id != None:
            common.db.update('bugs', where="id=" + web.db.sqlquote(self.id),
                             subject=self.subject, description=self.description,
                             guest=guest, author_extern=self.author_extern,
                             author_extern_email=self.author_extern_email,
                             author_intern=auth_int, project=self.project.id,
                             status=self.status, version=self.version,
                             modified=web.db.sqlliteral('NOW()'))
        else:
            common.db.insert('bugs',
                             subject=self.subject, description=self.description,
                             guest=guest, author_extern=self.author_extern,
                             author_extern_email=self.author_extern_email,
                             author_intern=auth_int, project=self.project.id,
                             status=self.status, version=self.version,
                             modified=web.db.sqlliteral('NOW()'))

