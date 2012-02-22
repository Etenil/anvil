import web
from anvillib.avatar import avatar, logo
import common
from hashlib import sha256
import user


class ProjectError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

def count_proj():
    counts = common.db.query("SELECT COUNT(id) AS count FROM project")
    return counts[0].count

def list_proj():
    return common.db.query('SELECT * FROM project ORDER BY created DESC')

def get_user_projects(user):
    results = common.db.query("SELECT project FROM commiters WHERE user='%d'" % user.id)
    projs = []
    for row in results:
        projs.append(Project(id=row.project))
    return projs

class Project:
    id = None
    name = ""
    owner = ""
    homepage = ""
    description = ""
    created = ""

    def __init__(self, name=None, id=None):
        if name != None or id != None:
            where = ""
            if id != None:
                where="id=" + web.db.sqlquote(id)
            elif name != None:
                where="name=" + web.db.sqlquote(name)

            projects = common.db.select('project', where=where)

            if len(projects) == 0:
                raise ProjectError("Unknown project")
            else:
                proj = projects[0]
                self.id = proj.id
                self.name = proj.name
                self.homepage = proj.homepage
                self.description = proj.description
                self.created = proj.created
                self.owner = user.User(id=proj.owner)
    #end __init__

    def save(self):
        if self.id != None:
            common.db.update('project', where="id=" + web.db.sqlquote(self.id),
                      name=self.name, description=self.description, owner=self.owner.id,
                      homepage=self.homepage)
        else:
            self.id = common.db.insert('project', name=self.name, seqname="id",
                                       description=self.description, owner=self.owner.id,
                                       homepage=self.homepage)
    #end save

    def logo(self):
        return logo(self.homepage)
    #end logo

    def isadmin(self, username):
        commiters = self.get_commiters()
        for c in commiters:
            if c.name == username:
                return True
        return False

    def get_commiters(self):
        """Returns the list of members of the project."""
        commiters_a = common.db.select('commiters', where=("project=%d" % self.id))
        commiters = []
        for c in commiters_a:
            commiters.append(user.User(id=c.user))
        return commiters

    def add_commiter(self, user_id):
        """Adds a commiter to the project."""
        common.db.insert('commiters', project=self.id, user=user_id)

    def rem_commiter(self, user_id):
        """Removes a commiter from the project."""
        common.db.delete('commiters', where=("project=%d AND user=%d" % (self.id, user_id)))
#end Project
