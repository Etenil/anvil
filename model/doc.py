import web
from anvillib.avatar import avatar, logo
import common
import user
import project
import difflib

def get_docs(project):
    rdocs = common.db.select('document', where="project=" + web.db.sqlquote(project))
    docs = []
    for rdoc in rdocs:
        docs.append(Doc(doc=rdoc))
    return docs


class DocError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class Doc:
    id = None
    project = None
    name = ""
    title = ""
    content = ""
    author = None
    mtime = ""

    def __init__(self, id=None, name=None, doc=None):
        if id != None or name != None or doc != None:
            if id != None:
                docs = common.db.select('document', where="id=" + web.db.sqlquote(id))
                if len(docs) == 0:
                    raise DocError("No document found")
                doc = docs[0]
            elif name != None:
                docs = common.db.select('document', where="name=" + web.db.sqlquote(name))
                if len(docs) == 0:
                    raise DocError("No document found")
                doc = docs[0]
            self.id = doc.id
            self.project = doc.project
            self.name = doc.name
            self.title = doc.title
            self.content = doc.content
            self.author = user.User(id=doc.author)
            self.mtime = doc.mtime

    def save(self):
        if self.id != None:
            common.db.update('document', where="id=" + web.db.sqlquote(self.id),
                             name=self.name, project=self.project,
                             title=self.title, content=self.content,
                             author=self.author.id)
        else:
            common.db.insert('document',
                             name=self.name, project=self.project,
                             title=self.title, content=self.content,
                             author=self.author.id)



