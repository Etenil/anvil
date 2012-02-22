import web
import common
import user as moduser
import project as modproject
import datetime

# Some constants
EV_SYSTEM  = 0
EV_PROJECT = 1
EV_USER    = 2
EV_BUG     = 3
EV_DOC     = 4

def _make_limit(length, start=0):
    return ("%d, %d" % (start, length))

# Syntactic sugar
def get_events(start=0, length=10):
    e = common.db.select('event', limit=_make_limit(length=length, start=start),
                         order="stamp DESC")
    events = []
    for row in e:
        events.append(Event(row=row))
    return events

def get_project_events(proj, start=0, length=10):
    e = common.db.select('event', where=("project=%d" % proj),
                         limit=_make_limit(length=length, start=start),
                         order="stamp DESC")
    events = []
    for row in e:
        events.append(Event(row=row))
    return events

def get_user_events(user, start=0, length=0):
    e = common.db.select('event', where=("user=%d" % user),
                         limit=_make_limit(length=length, start=start),
                         order="stamp DESC")
    events = []
    for row in e:
        events.append(Event(row=row))
    return events

def add(user=None, project=None, link=None, type=EV_SYSTEM, msg="",
        username=None, projectname=None):
    if user == None and username != None:
        u = moduser.User(name=username)
        user = u.id
    if project == None and projectname != None:
        u = modproject.Project(name=projectname)
        project = u.id
    if user == None and project == None:
        raise EventError("Must specify a user or a project.")
    e = Event()
    e.user = user
    e.project = project
    e.message = msg
    e.link = link
    e.type = type
    e.save()

class EventError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class Event:
    id = None
    user = None
    project = None
    stamp = ""
    type = 0
    message = ""
    link = ""

    types = ('system', 'project', 'user', 'bug', 'doc')

    def __init__(self, id=None, row=None):
        if id != None:
            events = common.db.select('event', where=("id='%d'" % id))
            if len(events) == 0:
                raise EventError("No such event")
            row = events[0]
        if row != None:
            self.id      = row.id
            self.user    = row.user
            self.project = row.project
            self.stamp   = row.stamp
            self.type    = self.types.index(row.type)
            self.message = row.message
            self.link    = row.link

    def save(self):
        if self.id != None:
            common.db.update('event', where="id=" + web.db.sqlquote(self.id),
                             user=self.user, project=self.project,
                             message=self.message, type=self.types[self.type],
                             link=self.link)
        else:
            common.db.insert('event', user=self.user, project=self.project,
                             message=self.message, type=self.types[self.type],
                             link=self.link)

    def get_msg(self):
        return self.message.replace("%l%", self.link)

    def get_human_date(self):
        now = datetime.datetime.now()
        if now.year == self.stamp.year and now.month == self.stamp.month:
            daydiff = now.day - self.stamp.day
            plural = ""
            if daydiff == 0:
                return "today, %s" % self.stamp.strftime("%H:%M")
            if daydiff > 1:
                plural = "s"
            return "%d day%s ago, %s" % (daydiff, plural, \
                                         self.stamp.strftime("%H:%M"))
        else:
            return self.stamp.strftime("%A, %d %B %Y, %H:%M")
        
    
