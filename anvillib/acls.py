from anvillib import config
import MySQLdb
import os
import fs

config.load_conf()

class Repo:
    def branch_loc(self, branch_name):
        return branch_name

class UserFS(Repo):
    user_id = 0
    username = ""

    def __init__(self, user_id):
        self.db = MySQLdb.connect(host=config.val('db.host'),
                                  user=config.val('db.user'),
                                  passwd=config.val('db.pwd'),
                                  db=config.val('db.name'))
        c = self.db.cursor()
        c.execute("SELECT * FROM user WHERE id=%s", user_id)
        row = c.fetchone()
        self.user_id = user_id
        self.username = row[1]

    def branch_loc(self, branch_name):
        return fs.user_branch_dir(self.username, branch_name)

    def can_access_project(self, project):
        c = self.db.cursor()
        c.execute("SELECT COUNT(commiters.id) FROM project, commiters WHERE commiters.user=%s AND project.name=%s AND commiters.project=project.id",
                  (self.user_id, project))
        num = c.fetchone()
        if num[0] > 0:
            return True
        else:
            print "Unauthorized!"
            return False


class ProjectFS(Repo):
    projectname = ""

    def __init__(self, project_id):
        db = MySQLdb.connect(host=config.val('db.host'),
                             user=config.val('db.user'),
                             passwd=config.val('db.pwd'),
                             db=config.val('db.name'))
        c = db.cursor()
        c.execute("SELECT * FROM `project` WHERE id=%s", project_id)
        row = c.fetchone()
        self.projectname = row[1]

    def branch_loc(self, branch_name):
        return fs.project_branch_dir(self.projectname, branch_name)
