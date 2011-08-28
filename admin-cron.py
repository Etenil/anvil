#!/usr/bin/python

# This program maintains users and their bazaar repositories.

import anvillib.actionqueue
import subprocess
from subprocess import check_call

def process_queue():
    queue = anvillib.actionqueue.get_queue()
    for order in queue:
        if order.action == "createuser":
            try:
                check_call(["useradd", "-m", "-b", "/var/anvil/",
                            "-G", "anvil", order.item])
                check_call(["su", "-c", "bzr init-repo --no-trees ~/bzr", order.item])
                order.complete()
            except:
                order.fail()
        elif order.action == "deleteuser":
            try:
                check_call(["userdel", "-f", "-r", order.item])
                order.complete()
            except subprocess.CalledProcessError as e:
                if e.returncode == 12:
                    order.complete()
                    pass
                else:
                    order.fail()
        elif order.action == "delbranch":
            try:
                check_call(["su", "-c", "rm -rf ~/bzr/%s" % order.args[0], order.item])
                order.complete()
            except:
                order.fail()


if __name__ == "__main__": process_queue()
