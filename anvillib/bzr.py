import os, sys
from bzrlib.branch import Branch
from bzrlib import log

def get_branch_log(path):
    branch = Branch.open(path)
    lf = HtmlLogFormatter(to_file=sys.stdout)
    log.show_log(branch, lf)

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
        to_file.write(indent + "%*s %s\t%s%s%s\n" % (revno_width,
                revision.revno or "", self.short_author(revision.rev),
                format_date(revision.rev.timestamp,
                            revision.rev.timezone or 0,
                            self.show_timezone, date_fmt="%Y-%m-%d",
                            show_offset=False),
                tags, self.merge_marker(revision)))
        self.show_properties(revision.rev, indent+offset)
        if self.show_ids or revision.revno is None:
            to_file.write(indent + offset + 'revision-id:%s\n'
                          % (revision.rev.revision_id,))
        if not revision.rev.message:
            to_file.write(indent + offset + '(no message)\n')
        else:
            message = revision.rev.message.rstrip('\r\n')
            for l in message.split('\n'):
                to_file.write(indent + offset + '%s\n' % (l,))

        if revision.delta is not None:
            # Use the standard status output to display changes
            from bzrlib.delta import report_delta
            report_delta(to_file, revision.delta,
                         short_status=self.delta_format==1,
                         show_ids=self.show_ids, indent=indent + offset)
        if revision.diff is not None:
            self.show_diff(self.to_exact_file, revision.diff, '      ')
        to_file.write('\n')

