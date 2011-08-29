import os
import sys
from bzrlib.branch import Branch
from bzrlib.osutils import format_date
from bzrlib import log

HOME_DIR = "/var/anvil/"

logvar = ""

def list_branches(user):
    homedir = HOME_DIR + user + "/bzr/"
    branches = os.listdir(homedir)
    branches.remove('.bzr')
    return branches

def get_branch_log(user, branch):
    path = HOME_DIR + user + "/bzr/" + branch
    branch = Branch.open(path)
    global logvar
    logvar = ""
    lf = HtmlLogFormatter(to_file=sys.stdout)
    rqst = log.make_log_request_dict()
    log.Logger(branch, rqst).show(lf)
    return logvar

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
        logvar += '<div class="revision">'
        logvar += '<div class="revdate">%s</div>' % format_date(revision.rev.timestamp,
                                                                revision.rev.timezone or 0,
                                                                self.show_timezone, date_fmt="%Y-%m-%d",
                                                                show_offset=False)

        logvar += '<div class="revbody">'
        logvar += '<p class="revinfo">%s committed revision <span class="hl">%s</span> %s</p>' % (self.short_author(revision.rev),
                                                 revision.revno or "",
                                                 self.merge_marker(revision))
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
                logvar += '<p class="revmessage">%s</p>' % l

        if revision.delta is not None:
            # Use the standard status output to display changes
            from bzrlib.delta import report_delta
            report_delta(to_file, revision.delta,
                         short_status=self.delta_format==1,
                         show_ids=self.show_ids, indent=indent + offset)
        if revision.diff is not None:
            self.show_diff(self.to_exact_file, revision.diff, '      ')
        logvar += '</div><div class="clear"></div></div>'

