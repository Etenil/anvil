import MySQLdb

# Action queue system.

db = MySQLdb.connect(host='localhost', user='anvil', passwd='anvil', db='anvil')

def get_queue():
    """Fetches an array of orders to be processed."""
    c = db.cursor(MySQLdb.cursors.DictCursor)
    c.execute("SELECT * FROM actionqueue WHERE state='0'")
    table = c.fetchall()
    queue = []
    for r in table:
        queue.append(Order(row=r))
    return queue

class Order():
    """Represents an order and the associated actions."""
    id = None
    action = ""
    item = ""
    args = []
    state = 0
    created = ""
    completed = ""

    def __init__(self, id=None, row=None):
        if id != None:
            c = db.cursor(MySQLdb.cursors.DictCursor)
            c.execute("SELECT * FROM actionqueue WHERE id='%s'", id)
            table = c.fetchall()
            if len(table) < 1:
                raise Exception, "No such order."
            row = table[0]
        self.id        = row['id']
        self.action    = row['action']
        self.item      = row['item']
        if row['args'] != None:
            self.args      = row['args'].split(',')
        self.state     = row['state']
        self.created   = row['created']

    def complete(self):
        if self.id == None:
            raise Exception, "Order not saved."
        c = db.cursor()
        c.execute("UPDATE actionqueue SET state='1' WHERE id='%s'", self.id)
        db.commit()

    def fail(self):
        if self.id == None:
            raise Exception, "Order not saved."
        c = db.cursor()
        c.execute("UPDATE actionqueue SET state='2' WHERE id='%s'", self.id)
        db.commit()

    def save(self):
        if self.id != None:
            raise Exception, "Order already exists."
        c = db.cursor()
        c.execute("""INSERT INTO actionqueue SET action='%s', item='%s',
                      args='%s', created=NOW()""",
                  self.action, self.item, ','.join(self.args))
        db.commit()

