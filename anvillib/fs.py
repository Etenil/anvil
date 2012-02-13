import os
import shutil
import config
import bzr

# USER
def create_user(username):
    check_defaults()
    bzr.initrepo(user_branch_dir(username))

def check_users():
    userspath = os.path.join(config.val('home_dir'), "users")
    logf = open("/tmp/anvserve", "w")
    logf.write(userspath)
    logf.close()
    if not os.path.exists(userspath):
        os.makedirs(userspath)

def add_user_branch(username, branch):
    bzr.initbranch(user_branch_dir(username, branch))

def delete_user_branch(username, branch):
    shutil.rmtree(os.path.join(config.val('home_dir'), "users", username, branch))

def delete_user(username):
    shutil.rmtree(os.path.join(config.val('home_dir'), "users", username))

def user_branch_dir(username, branch=None):
    """Returns the path to the branch of user. If branch is None,
    then returns the path to the user's branch repository."""
    if branch == None:
        return os.path.join(config.val('home_dir'), "users", username)
    else:
        return os.path.join(config.val('home_dir'), "users", username, branch)

# PROJECT
def create_project(projectname):
    check_defaults()
    os.makedirs(os.path.join(config.val('home_dir'), "projects", projectname))

def check_projects():
    projspath = os.path.join(config.val('home_dir'), "projects")
    if not os.path.exists(projspath):
        os.makedirs(projspath)

def add_project_branch(projectname, branch):
    os.makedirs(os.path.join(config.val('home_dir'), "projects", projectname, branch))

def delete_project_branch(projectname, branch):
    shutil.rmtree(os.path.join(config.val('home_dir'), "projects", projectname, branch))

def delete_project(projectname):
    shutil.rmtree(os.path.join(config.val('home_dir'), "projects", projectname))

def project_branch_dir(project, branch=None):
    """Returns the path to the branch of project. If branch is None,
    then returns the path to the project's branch repository."""
    if branch == None:
        return os.path.join(config.val('home_dir'), "users", project)
    else:
        return os.path.join(config.val('home_dir'), "users", project, branch)


def check_defaults():
    check_users()
    check_projects()
