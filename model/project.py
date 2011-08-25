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

class Project:
    id = None
    name = ""
    owned_by_team = None
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
                self.owned_by_team = (proj.owned_by_team != 0)
                self.homepage = proj.homepage
                self.description = proj.description
                self.created = proj.created
                if not self.owned_by_team:
                    self.owner = user.User(id=proj.owner)
    #end __init__

    def save(self):
        owned_by_team = '0'
        if self.owned_by_team == True:
            owned_by_team = '1'

        if self.id != None:
            common.db.update('project', where="id=" + web.db.sqlquote(self.id),
                      name=self.name, owned_by_team=owned_by_team,
                      description=self.description, owner=self.owner.id,
                      homepage=self.homepage)
        else:
            common.db.insert('project', name=self.name, owned_by_team=owned_by_team,
                      description=self.description, owner=self.owner.id,
                      homepage=self.homepage)
    #end save

    def logo(self):
        return logo(self.homepage)
    #end logo

    def isadmin(self, username):
        try:
            usr = user.User(name=username)
        except:
            return False

        return (usr.id == self.owner.id)

#end Project
