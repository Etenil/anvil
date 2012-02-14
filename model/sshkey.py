import web
from web import form
import common
import model.project
import model.user
import re

def get_keys(user):
    rkeys = common.db.select('ssh_keys', where="user=" + web.db.sqlquote(user))
    keys = []
    for r in rkeys:
        keys.append(SSHKey(row=r))
    return keys

def has_key(somekey):
    rkeys = common.db.select('ssh_keys', where=("pubkey='%s'" % somekey))
    if len(rkeys) > 0:
        return True
    else:
        return False

class SSHKey:
    id = None
    user = None
    key = ""

    def __init__(self, id=None, row=None):
        if id != None or row != None:
            if id != None:
                keys = common.db.select('ssh_keys', where="id=" + web.db.sqlquote(id))
                if len(keys) < 1:
                    raise Exception, "Key does not exist."
                row = keys[0]
            self.id = row.id
            self.user = row.user
            self.key = row.pubkey

    def save(self):
        if self.id != None:
            raise Exception, "Key already exists."
        common.db.insert('ssh_keys', user=self.user, pubkey=self.key)

    def delete(self):
        if self.id == None:
            raise Exception, "Key doesn't exist."
        common.db.delete('ssh_keys', where="id=" + web.db.sqlquote(self.id))
