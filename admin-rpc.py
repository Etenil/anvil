#!/usr/bin/python

import xmlrpclib
import subprocess
from subprocess import check_call

from SimpleXMLRPCServer import SimpleXMLRPCServer

def create_user(username):
    print "Creating user %s" % username
    try:
        check_call(["useradd", "-m", "-b", "/var/anvil/",
                    "-G", "anvil", username])
        check_call(["su", "-c", "bzr init-repo --no-trees ~/bzr", username])
        return "OK"
    except:
        return "FAILED"

def delete_user(username):
    try:
        check_call(["userdel", "-f", "-r", username])
        return "OK"
    except subprocess.CalledProcessError as e:
        if e.returncode == 12:
            return "OK"
        else:
            return "FAILED"

def delete_branch(username, branch):
    try:
        check_call(["su", "-c", "rm -rf ~/bzr/%s" % branch, username])
        return "OK"
    except:
        return "FAILED"

def main():
    server = SimpleXMLRPCServer(("localhost", 300))
    print "Listening on port 300"
    server.register_function(create_user, "create_user")
    server.register_function(delete_user, "delete_user")
    server.register_function(delete_branch, "delete_branch")
    server.serve_forever()

if __name__ == "__main__": main()
