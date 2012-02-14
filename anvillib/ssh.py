import os
import stat
import config
import MySQLdb

def regenerate_keys():
    db = None
    try:
        db = MySQLdb.connect(host=config.val('db.host'),
                             user=config.val('db.user'),
                             passwd=config.val('db.pwd'),
                             db=config.val('db.name'))
    except:
        return False
    c = db.cursor()
    c.execute("SELECT * FROM ssh_keys")
    if not os.path.exists(os.path.join(config.val('home_dir'), '.ssh')):
        os.makedirs(os.path.join(config.val('home_dir'), '.ssh'))
    auth_keys = os.path.join(config.val('home_dir'), ".ssh/authorized_keys")
    key_file = open(auth_keys, 'w')
    for row in c:
        key_file.write("command=\"bzr anv-serve %d --inet\" %s\n" % (row[1], row[2]))
    key_file.close()
    os.chmod(auth_keys, stat.S_IRWXU)
    return True
