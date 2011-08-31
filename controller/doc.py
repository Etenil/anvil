import web
from web import form
import common
from web.contrib.template import render_mako
from anvillib.form import AjaxTextbox
import model.doc
import model.project
import model.user
import re
from anvillib.text import normalize_name

class Doc:
    def GET(self, project=None, action=None, extra=None):
        if project == None:
            raise web.seeother(common.prefix + '/')
        elif action == None:
            return self.list_docs(project)
        elif action == "new":
            return self.new_doc(project)
        elif action != None and extra == "edit":
            return self.edit_doc(project, action)
        elif action != None:
            return self.show_doc(project, action)
        else:
            raise web.seeother(common.prefix + '/' + project + '/doc')

    def POST(self, project=None, action=None, extra=None):
        if project == None:
            raise web.seeother(common.prefix + '/')
        if action == "new":
            self.do_new_doc(project)
        elif action != None and extra == "delete":
            return self.do_delete(project, action)
        elif action != None and extra == "edit":
            return self.do_edit_doc(project, action)
        else:
            raise web.seeother(common.prefix + '/' + project + '/doc')

    def _admin_or_die(self, project):
        p = model.project.Project(name=project)
        if not p.isadmin(common.session.user):
            raise web.seeother(common.prefix + '/' + project + '/doc')
        return p

    def list_docs(self, project):
        p = model.project.Project(name=project)
        docs = model.doc.get_docs(p.id)
        return common.render.doclist(docs=docs,
                                     proj=p,
                                     htTitle="Documents for " + p.name)

    def new_doc(self, project):
        p = self._admin_or_die(project)
        f = self._make_doc_form()
        return common.render.docedit(form=f,
                                     proj=project,
                                     htTitle="New document for " + p.name)

    def do_new_doc(self, project):
        p = self._admin_or_die(project)
        f = self._make_doc_form()
        if not f.validates():
            return common.render.docedit(form=f,
                                         proj=project,
                                         htTitle="New document for " + p.name)
        u = model.user.User(name=common.session.user)
        i = web.input()
        doc = model.doc.Doc()
        doc.project = p.id
        doc.name = normalize_name(i.title)
        doc.title = i.title
        doc.content = i.content
        doc.author = u.id
        doc.save()
        raise web.seeother(common.prefix + '/' + project + '/doc/' + doc.name)

    def show_doc(self, project, docname):
        p = model.project.Project(name=project)
        doc = model.doc.Doc(name=docname)
        return common.render.document(proj=project,
                                      canedit=p.isadmin(common.session.user),
                                      doc=doc)

    def _make_doc_form(self, doc=None):
        if doc == None:
            return form.Form(form.Textbox('title',
                                          form.notnull,
                                          description="Title"),
                             form.Textarea('content',
                                           description="Content",
                                           class_="largetextarea"),
                             form.Button('Save'))
        else:
            return form.Form(form.Textbox('title',
                                          form.notnull,
                                          description="Title",
                                          value=doc.title),
                             form.Textarea('content',
                                           description="Content",
                                           class_="largetextarea",
                                           value=doc.content),
                             form.Button('Save'))

    def edit_doc(self, project, docname):
        p = self._admin_or_die(project)
        d = model.doc.Doc(name=docname)
        f = self._make_doc_form(d)
        return common.render.docedit(edit=True,
                                     doc=d,
                                     form=f,
                                     proj=project,
                                     htTitle="Edit document")

    def do_edit_doc(self, project, docname):
        p = self._admin_or_die(project)
        d = model.doc.Doc(name=docname)
        f = self._make_doc_form()
        if not f.validates():
            return common.render.docedit(doc=d,
                                         form=f,
                                         proj=project,
                                         htTitle="Edit document")
        i = web.input()
        d.name = normalize_name(i.title)
        d.title = i.title
        d.content = i.content
        d.save()
        raise web.seeother(common.prefix + '/' + project + '/doc/' + d.name)

