#!/usr/bin/python

import os
import xmlrpclib
import daemon
import lockfile
import subprocess
from subprocess import check_call
from SimpleXMLRPCServer import SimpleXMLRPCServer

log = open("/var/log/anvil-admin.log", "w+")

context = daemon.DaemonContext(
    working_directory = "/var/www/anvil/",
    umask = 0o002,
    pidfile = lockfile.FileLock('/var/run/anvil.pid'),
    files_preserve = [log],
    stdout = log,
    stderr = log
    )

HOME_DIR = "/var/anvil/"

def _format_ssh_key(user, key):
    homedir = HOME_DIR + user
    return 'command="bzr serve --inet --directory=%s/bzr --allow-writes",no-port-forwarding,no-pty,no-agent-forwarding,no-X11-forwarding %s' % (homedir.strip(), key.strip())

def _read_keys(user):
    homedir = HOME_DIR + user
    fh = open(homedir + "/.ssh/authorized_keys", "r")
    keys = []
    k = fh.readline()
    while k:
        if k != "\n":
            keys.append(k.strip())
        k = fh.readline()
    fh.close()
    return keys

def _write_keys(user, keys):
    homedir = HOME_DIR + user
    fh = open(homedir + "/.ssh/authorized_keys", "w")
    fh.seek(0)
    if len(keys) == 0:
        fh.write('')
    else:
        fh.write("\n".join(keys) + "\n")
    fh.close()
    check_call(["su", "-c", "chown %s -R 700 ~/.ssh" % user, user])
    check_call(["su", "-c", "chmod -R 700 ~/.ssh", user])

def create_user(username):
    try:
        check_call(["useradd", "-m", "-b", HOME_DIR,
                    "-g", "anvil", username])
        check_call(["su", "-c", "mkdir -p ~/.ssh/", username])
        check_call(["su", "-c", "touch ~/.ssh/authorized_keys", username])
        check_call(["su", "-c", "chown %s -R 700 ~/.ssh" % username, username])
        check_call(["su", "-c", "chmod -R 700 ~/.ssh", username])
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

def add_ssh_key(key, user):
    #try:
    keys = _read_keys(user)
        # Checking if the key's there.
    ssh_line = _format_ssh_key(user, key)
    if keys.count(ssh_line) > 0:
        return "FAILED"
    keys.append(ssh_line)
    _write_keys(user, keys)
    return "OK"
    #except:
    #    return "FAILED"

def remove_ssh_key(key, user):
    #try:
    keys = _read_keys(user)
        # Checking if the key's there.
    ssh_line = _format_ssh_key(user, key)
    if keys.count(ssh_line) == 0:
        return "FAILED"
    keys.remove(ssh_line)
    print keys
    _write_keys(user, keys)
    return "OK"
    #except:
    #    return "FAILED"

def main():
    server = SimpleXMLRPCServer(("localhost", 300))
    print "Listening on port 300"
    server.register_function(create_user, "create_user")
    server.register_function(delete_user, "delete_user")
    server.register_function(delete_branch, "delete_branch")
    server.register_function(add_ssh_key, "add_ssh_key")
    server.register_function(remove_ssh_key, "remove_ssh_key")
    server.serve_forever()

def test():
    add_ssh_key("prout", "etenil")
    remove_ssh_key("prout", "etenil")

if __name__ == "__main__":
    with context:
        main()
