import os
import shutil

# USER
def create_user(home_dir, username):
    os.makedirs(os.path.join(home_dir, "users", username))

def add_user_branch(home_dir, username, branch):
    os.makedirs(os.path.join(home_dir, "users", username, branch))

def delete_user_branch(home_dir, username, branch):
    shutil.rmtree(os.path.join(home_dir, "users", username, branch))

def delete_user(home_dir, username):
    shutil.rmtree(os.path.join(home_dir, "users", username))

# PROJECT
def create_project(home_dir, projectname):
    os.makedirs(os.path.join(home_dir, "projects", projectname))

def add_project_branch(home_dir, projectname, branch):
    os.makedirs(os.path.join(home_dir, "projects", projectname, branch))

def delete_project_branch(home_dir, projectname, branch):
    shutil.rmtree(os.path.join(home_dir, "projects", projectname, branch))

def delete_project(home_dir, projectname):
    shutil.rmtree(os.path.join(home_dir, "projects", projectname))
