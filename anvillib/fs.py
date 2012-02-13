import os
import shutil
import config

# USER
def create_user(username):
    os.makedirs(os.path.join(config.val('home_dir'), "users", username))

def add_user_branch(username, branch):
    os.makedirs(os.path.join(config.val('home_dir'), "users", username, branch))

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
    os.makedirs(os.path.join(config.val('home_dir'), "projects", projectname))

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
