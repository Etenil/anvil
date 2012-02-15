import os
import sys
import web
from bzrlib.branch import Branch
from bzrlib.osutils import format_date
from bzrlib import log
from bzrlib import transport
from bzrlib import bzrdir
import config
import fs

logvar = ""

def _list_branches(path):
    branches = os.listdir(path)
    branches.remove('.bzr')
    return branches

def list_user_branches(user):
    return _list_branches(fs.user_branch_dir(user))

def list_project_branches(project):
    return _list_branches(fs.project_branch_dir(project))

def initrepo(path):
    format = bzrdir.format_registry.make_bzrdir('default')
    to_transport = transport.get_transport(path)
    to_transport.ensure_base()
    newdir = format.initialize_on_transport(to_transport)
    repo = newdir.create_repository(shared=True)
    repo.set_make_working_trees(False) # We don't want trees.
    #Done.

def initbranch(path):
    format = bzrdir.format_registry.make_bzrdir('default')
    to_transport = transport.get_transport(path)
    to_transport.ensure_base()

    a_bzrdir = bzrdir.BzrDir.open_from_transport(to_transport)
    from bzrlib.transport.local import LocalTransport
    if a_bzrdir.has_branch():
        return # The branch already exists
    branch = a_bzrdir.create_branch()
    a_bzrdir.create_workingtree()
    #Done.

def _get_branch_tree(path):
    b = Branch.open(path)
    t = b.basis_tree()
    b.lock_read()
    files = t.iter_entries_by_dir()
    buffer = []
    from bzrlib.inventory import InventoryFile
    for f in files:
        type = 'dir'
        if f[1].__class__ == InventoryFile:
            type = 'file'
        buffer.append((f[1].file_id, f[0], type))
    b.unlock()
    return buffer

def get_project_branch_tree(project, branch):
    return _get_branch_tree(fs.project_branch_dir(project, branch))

def get_user_branch_tree(user, branch):
    return _get_branch_tree(fs.user_branch_dir(user, branch))

def _get_branch_log(path):
    branch = Branch.open(path)
    global logvar
    logvar = ""
    lf = HtmlLogFormatter(to_file=sys.stdout)
    rqst = log.make_log_request_dict()
    log.Logger(branch, rqst).show(lf)
    return logvar

def get_user_branch_log(user, branch):
    return _get_branch_log(fs.user_branch_dir(user, branch))

def get_project_branch_log(user, branch):
    return _get_branch_log(fs.project_branch_dir(user, branch))

class HtmlLogFormatter(log.LogFormatter):
    supports_merge_revisions = True
    preferred_levels = 1
    supports_delta = True
    supports_tags = True
    supports_diff = True

    def __init__(self, *args, **kwargs):
        super(HtmlLogFormatter, self).__init__(*args, **kwargs)
        self.revno_width_by_depth = {}

    def log_revision(self, revision):
        # We need two indents: one per depth and one for the information
        # relative to that indent. Most mainline revnos are 5 chars or
        # less while dotted revnos are typically 11 chars or less. Once
        # calculated, we need to remember the offset for a given depth
        # as we might be starting from a dotted revno in the first column
        # and we want subsequent mainline revisions to line up.
        depth = revision.merge_depth
        indent = '    ' * depth
        global logvar
        revno_width = self.revno_width_by_depth.get(depth)
        if revno_width is None:
            if revision.revno is None or revision.revno.find('.') == -1:
                # mainline revno, e.g. 12345
                revno_width = 5
            else:
                # dotted revno, e.g. 12345.10.55
                revno_width = 11
            self.revno_width_by_depth[depth] = revno_width
        offset = ' ' * (revno_width + 1)

        to_file = self.to_file
        tags = ''
        if revision.tags:
            tags = ' {%s}' % (', '.join(revision.tags))
        logvar += '<div id="%s" class="revision">' % revision.revno
        logvar += '<div class="revdate">%s</div>' % format_date(revision.rev.timestamp,
                                                                revision.rev.timezone or 0,
                                                                self.show_timezone, date_fmt="%Y-%m-%d",
                                                                show_offset=False)

        logvar += '<div class="revbody">'
        logvar += '<p class="revinfo">%s committed revision <span class="hl">%s</span> %s</p>' % (self.short_author(revision.rev), revision.revno or "", self.merge_marker(revision))
        if tags != "":
            logvar += '<p class="tags">%s</p>' % tags

        self.show_properties(revision.rev, indent+offset)
        if self.show_ids or revision.revno is None:
            logvar += '<p class="revmessage">revision-id:%s</p>' % revision.rev.revision_id
        if not revision.rev.message:
            logvar += '<p class="revmessage">(no message)</p>'
        else:
            message = revision.rev.message.rstrip('\r\n')
            for l in message.split('\n'):
                logvar += '<p class="revmessage">%s</p>' % web.net.websafe(l)

        if revision.delta is not None:
            # Use the standard status output to display changes
            from bzrlib.delta import report_delta
            report_delta(to_file, revision.delta,
                         short_status=self.delta_format==1,
                         show_ids=self.show_ids, indent=indent + offset)
        if revision.diff is not None:
            self.show_diff(self.to_exact_file, revision.diff, '      ')
        logvar += '</div><div class="clear"></div></div>'
