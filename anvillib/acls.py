from anvillib import config
import MySQLdb
import os

config.load_conf()

class Repo:
    def branch_loc(self, branch_name):
        return branch_name

class UserFS(Repo):
    username = ""

    def __init__(self, user_id):
        db = MySQLdb.connect(host=config.val('db.host'),
                             user=config.val('db.user'),
                             passwd=config.val('db.pwd'),
                             db=config.val('db.name'))
        c = db.cursor()
        c.execute("SELECT * FROM `user` WHERE id=%s", user_id)
        row = c.fetchone()
        self.username = row[1]

    def branch_loc(self, branch_name):
        return os.path.join(config.val('home_dir'), "users", self.username, branch_name)


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
        return os.path.join(config.val('home_dir'), "projects", self.projectname, branch_name)
