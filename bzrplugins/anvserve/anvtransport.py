__all__ = ['AnvLocalTransport']

import os
from stat import ST_MODE, S_ISDIR, ST_SIZE, S_IMODE
import sys
import errno
import shutil
import anvillib.acls
import anvillib.fs

from cStringIO import StringIO

from bzrlib import (
    atomicfile,
    osutils,
    symbol_versioning,
    config,
    debug,
    errors,
    remote,
    trace,
    transport,
    urlutils,
    )
from bzrlib.smart import client, medium
from bzrlib.symbol_versioning import (
    deprecated_method,
    )

_append_flags = os.O_CREAT | os.O_APPEND | os.O_WRONLY | osutils.O_BINARY | osutils.O_NOINHERIT
_put_non_atomic_flags = os.O_CREAT | os.O_TRUNC | os.O_WRONLY | osutils.O_BINARY | osutils.O_NOINHERIT

class AnvLocalTransport(transport.Transport):
    """This is the transport agent for local filesystem access."""

    def __init__(self, base, userID):
        """Set the base path where files will be stored."""
        self.user = anvillib.acls.UserFS(userID)
        if not base.startswith('file://'):
            symbol_versioning.warn(
                "Instantiating AnvLocalTransport with a filesystem path"
                " is deprecated as of bzr 0.8."
                " Please use bzrlib.transport.get_transport()"
                " or pass in a file:// url.",
                 DeprecationWarning,
                 stacklevel=2
                 )
            base = urlutils.local_path_to_url(base)
        if base[-1] != '/':
            base = base + '/'

        # Special case : windows has no "root", but does have
        # multiple lettered drives inside it. #240910
        if sys.platform == 'win32' and base == 'file:///':
            base = ''
            self._local_base = ''
            super(AnvLocalTransport, self).__init__(base)
            return

        super(AnvLocalTransport, self).__init__(base)
        self._local_base = urlutils.local_path_from_url(base)

    def clone(self, offset=None):
        """Return a new AnvLocalTransport with root at self.base + offset
        Because the local filesystem does not require a connection,
        we can just return a new object.
        """
        if offset is None:
            return AnvLocalTransport(self.base)
        else:
            abspath = self.abspath(offset)
            if abspath == 'file://':
                # fix upwalk for UNC path
                # when clone from //HOST/path updir recursively
                # we should stop at least at //HOST part
                abspath = self.base
            return AnvLocalTransport(abspath)

    def _anvilise_path(self, somepath):
        path = somepath
        if path.startswith("%2A"):
            user = path[3:path.find("/")]
            branch = path[(path.find("/") + 1):]
            if self.user.username != user:
                return "/dev/null"
            path = anvillib.fs.user_branch_dir(user, branch)
        else:
            project = path[0:path.find("/")]
            branch = path[(path.find("/") + 1):]
            if not self.user.can_access_project(project):
                return "/dev/null"
            path = anvillib.fs.project_branch_dir(project, branch)

        return path

    def _abspath(self, relative_reference):
        """Return a path for use in os calls.

        Several assumptions are made:
         - relative_reference does not contain '..'
         - relative_reference is url escaped.
        """
        relative_reference = self._anvilise_path(relative_reference)
        if relative_reference in ('.', ''):
            # _local_base normally has a trailing slash; strip it so that stat
            # on a transport pointing to a symlink reads the link not the
            # referent but be careful of / and c:\
            return osutils.split(self._local_base)[0]
        #return self._local_base + urlutils.unescape(relative_reference)
        return urlutils.unescape(relative_reference)

    def abspath(self, relpath):
        """Return the full url to the given relative URL."""
        # TODO: url escape the result. RBC 20060523.
        # jam 20060426 Using normpath on the real path, because that ensures
        #       proper handling of stuff like
        relpath = self._anvilise_path(relpath)
        path = osutils.normpath(osutils.pathjoin(
                    self._local_base, urlutils.unescape(relpath)))
        # on windows, our _local_base may or may not have a drive specified
        # (ie, it may be "/" or "c:/foo").
        # If 'relpath' is '/' we *always* get back an abspath without
        # the drive letter - but if our transport already has a drive letter,
        # we want our abspaths to have a drive letter too - so handle that
        # here.
        if (sys.platform == "win32" and self._local_base[1:2] == ":"
            and path == '/'):
            path = self._local_base[:3]

        return urlutils.local_path_to_url(path)

    def local_abspath(self, relpath):
        """Transform the given relative path URL into the actual path on disk

        This function only exists for the AnvLocalTransport, since it is
        the only one that has direct local access.
        This is mostly for stuff like WorkingTree which needs to know
        the local working directory.  The returned path will always contain
        forward slashes as the path separator, regardless of the platform.

        This function is quite expensive: it calls realpath which resolves
        symlinks.
        """
        absurl = self.abspath(relpath)
        # mutter(u'relpath %s => base: %s, absurl %s', relpath, self.base, absurl)
        return urlutils.local_path_from_url(absurl)

    def relpath(self, abspath):
        """Return the local path portion from a given absolute path.
        """
        if abspath is None:
            abspath = u'.'

        return urlutils.file_relpath(
            urlutils.strip_trailing_slash(self.base),
            urlutils.strip_trailing_slash(abspath))

    def has(self, relpath):
        return os.access(self._abspath(relpath), os.F_OK)

    def get(self, relpath):
        """Get the file at the given relative path.

        :param relpath: The relative path to the file
        """
        logf = open("/tmp/anvserve", "a")
        canonical_url = self.abspath(relpath)
        if canonical_url in transport._file_streams:
            transport._file_streams[canonical_url].flush()
        filectt = None
        try:
            path = self._abspath(relpath)
            logf.write("Get " + relpath + " => " + path + "... ")
            filectt = osutils.open_file(path, 'rb')
            logf.write("file succesffuly opened")
        except (IOError, OSError),e:
            if e.errno == errno.EISDIR:
                filectt = LateReadError(relpath)
            self._translate_error(e, path)
        logf.write("\n")
        logf.close()
        return filectt

    def put_file(self, relpath, f, mode=None):
        """Copy the file-like object into the location.

        :param relpath: Location to put the contents, relative to base.
        :param f:       File-like object.
        :param mode: The mode for the newly created file,
                     None means just use the default
        """

        path = relpath
        try:
            path = self._abspath(relpath)
            osutils.check_legal_path(path)
            fp = atomicfile.AtomicFile(path, 'wb', new_mode=mode)
        except (IOError, OSError),e:
            self._translate_error(e, path)
        try:
            length = self._pump(f, fp)
            fp.commit()
        finally:
            fp.close()
        return length

    def put_bytes(self, relpath, bytes, mode=None):
        """Copy the string into the location.

        :param relpath: Location to put the contents, relative to base.
        :param bytes:   String
        """

        path = relpath
        try:
            path = self._abspath(relpath)
            osutils.check_legal_path(path)
            fp = atomicfile.AtomicFile(path, 'wb', new_mode=mode)
        except (IOError, OSError),e:
            self._translate_error(e, path)
        try:
            if bytes:
                fp.write(bytes)
            fp.commit()
        finally:
            fp.close()

    def _put_non_atomic_helper(self, relpath, writer,
                               mode=None,
                               create_parent_dir=False,
                               dir_mode=None):
        """Common functionality information for the put_*_non_atomic.

        This tracks all the create_parent_dir stuff.

        :param relpath: the path we are putting to.
        :param writer: A function that takes an os level file descriptor
            and writes whatever data it needs to write there.
        :param mode: The final file mode.
        :param create_parent_dir: Should we be creating the parent directory
            if it doesn't exist?
        """
        abspath = self._abspath(relpath)
        if mode is None:
            # os.open() will automatically use the umask
            local_mode = 0666
        else:
            local_mode = mode
        try:
            fd = os.open(abspath, _put_non_atomic_flags, local_mode)
        except (IOError, OSError),e:
            # We couldn't create the file, maybe we need to create
            # the parent directory, and try again
            if (not create_parent_dir
                or e.errno not in (errno.ENOENT,errno.ENOTDIR)):
                self._translate_error(e, relpath)
            parent_dir = os.path.dirname(abspath)
            if not parent_dir:
                self._translate_error(e, relpath)
            self._mkdir(parent_dir, mode=dir_mode)
            # We created the parent directory, lets try to open the
            # file again
            try:
                fd = os.open(abspath, _put_non_atomic_flags, local_mode)
            except (IOError, OSError), e:
                self._translate_error(e, relpath)
        try:
            st = os.fstat(fd)
            if mode is not None and mode != S_IMODE(st.st_mode):
                # Because of umask, we may still need to chmod the file.
                # But in the general case, we won't have to
                os.chmod(abspath, mode)
            writer(fd)
        finally:
            os.close(fd)

    def put_file_non_atomic(self, relpath, f, mode=None,
                            create_parent_dir=False,
                            dir_mode=None):
        """Copy the file-like object into the target location.

        This function is not strictly safe to use. It is only meant to
        be used when you already know that the target does not exist.
        It is not safe, because it will open and truncate the remote
        file. So there may be a time when the file has invalid contents.

        :param relpath: The remote location to put the contents.
        :param f:       File-like object.
        :param mode:    Possible access permissions for new file.
                        None means do not set remote permissions.
        :param create_parent_dir: If we cannot create the target file because
                        the parent directory does not exist, go ahead and
                        create it, and then try again.
        """
        def writer(fd):
            self._pump_to_fd(f, fd)
        self._put_non_atomic_helper(relpath, writer, mode=mode,
                                    create_parent_dir=create_parent_dir,
                                    dir_mode=dir_mode)

    def put_bytes_non_atomic(self, relpath, bytes, mode=None,
                             create_parent_dir=False, dir_mode=None):
        def writer(fd):
            if bytes:
                os.write(fd, bytes)
        self._put_non_atomic_helper(relpath, writer, mode=mode,
                                    create_parent_dir=create_parent_dir,
                                    dir_mode=dir_mode)

    def iter_files_recursive(self):
        """Iter the relative paths of files in the transports sub-tree."""
        queue = list(self.list_dir(u'.'))
        while queue:
            relpath = queue.pop(0)
            st = self.stat(relpath)
            if S_ISDIR(st[ST_MODE]):
                for i, basename in enumerate(self.list_dir(relpath)):
                    queue.insert(i, relpath+'/'+basename)
            else:
                yield relpath

    def _mkdir(self, abspath, mode=None):
        """Create a real directory, filtering through mode"""
        if mode is None:
            # os.mkdir() will filter through umask
            local_mode = 0777
        else:
            local_mode = mode
        try:
            os.mkdir(abspath, local_mode)
            if mode is not None:
                # It is probably faster to just do the chmod, rather than
                # doing a stat, and then trying to compare
                os.chmod(abspath, mode)
        except (IOError, OSError),e:
            self._translate_error(e, abspath)

    def mkdir(self, relpath, mode=None):
        """Create a directory at the given path."""
        self._mkdir(self._abspath(relpath), mode=mode)

    def open_write_stream(self, relpath, mode=None):
        """See Transport.open_write_stream."""
        # initialise the file
        self.put_bytes_non_atomic(relpath, "", mode=mode)
        abspath = self._abspath(relpath)
        handle = osutils.open_file(abspath, 'wb')
        if mode is not None:
            self._check_mode_and_size(abspath, handle.fileno(), mode)
        transport._file_streams[self.abspath(relpath)] = handle
        return transport.FileFileStream(self, relpath, handle)

    def _get_append_file(self, relpath, mode=None):
        """Call os.open() for the given relpath"""
        file_abspath = self._abspath(relpath)
        if mode is None:
            # os.open() will automatically use the umask
            local_mode = 0666
        else:
            local_mode = mode
        try:
            return file_abspath, os.open(file_abspath, _append_flags, local_mode)
        except (IOError, OSError),e:
            self._translate_error(e, relpath)

    def _check_mode_and_size(self, file_abspath, fd, mode=None):
        """Check the mode of the file, and return the current size"""
        st = os.fstat(fd)
        if mode is not None and mode != S_IMODE(st.st_mode):
            # Because of umask, we may still need to chmod the file.
            # But in the general case, we won't have to
            os.chmod(file_abspath, mode)
        return st.st_size

    def append_file(self, relpath, f, mode=None):
        """Append the text in the file-like object into the final location."""
        file_abspath, fd = self._get_append_file(relpath, mode=mode)
        try:
            result = self._check_mode_and_size(file_abspath, fd, mode=mode)
            self._pump_to_fd(f, fd)
        finally:
            os.close(fd)
        return result

    def append_bytes(self, relpath, bytes, mode=None):
        """Append the text in the string into the final location."""
        file_abspath, fd = self._get_append_file(relpath, mode=mode)
        try:
            result = self._check_mode_and_size(file_abspath, fd, mode=mode)
            if bytes:
                os.write(fd, bytes)
        finally:
            os.close(fd)
        return result

    def _pump_to_fd(self, fromfile, to_fd):
        """Copy contents of one file to another."""
        BUFSIZE = 32768
        while True:
            b = fromfile.read(BUFSIZE)
            if not b:
                break
            os.write(to_fd, b)

    def copy(self, rel_from, rel_to):
        """Copy the item at rel_from to the location at rel_to"""
        path_from = self._abspath(rel_from)
        path_to = self._abspath(rel_to)
        try:
            shutil.copy(path_from, path_to)
        except (IOError, OSError),e:
            # TODO: What about path_to?
            self._translate_error(e, path_from)

    def rename(self, rel_from, rel_to):
        path_from = self._abspath(rel_from)
        path_to = self._abspath(rel_to)
        try:
            # *don't* call bzrlib.osutils.rename, because we want to
            # detect conflicting names on rename, and osutils.rename tries to
            # mask cross-platform differences there
            os.rename(path_from, path_to)
        except (IOError, OSError),e:
            # TODO: What about path_to?
            self._translate_error(e, path_from)

    def move(self, rel_from, rel_to):
        """Move the item at rel_from to the location at rel_to"""
        path_from = self._abspath(rel_from)
        path_to = self._abspath(rel_to)

        try:
            # this version will delete the destination if necessary
            osutils.rename(path_from, path_to)
        except (IOError, OSError),e:
            # TODO: What about path_to?
            self._translate_error(e, path_from)

    def delete(self, relpath):
        """Delete the item at relpath"""
        path = relpath
        try:
            path = self._abspath(relpath)
            os.remove(path)
        except (IOError, OSError),e:
            self._translate_error(e, path)

    def external_url(self):
        """See bzrlib.transport.Transport.external_url."""
        # File URL's are externally usable.
        return self.base

    def copy_to(self, relpaths, other, mode=None, pb=None):
        """Copy a set of entries from self into another Transport.

        :param relpaths: A list/generator of entries to be copied.
        """
        if isinstance(other, AnvLocalTransport):
            # Both from & to are on the local filesystem
            # Unfortunately, I can't think of anything faster than just
            # copying them across, one by one :(
            total = self._get_total(relpaths)
            count = 0
            for path in relpaths:
                self._update_pb(pb, 'copy-to', count, total)
                try:
                    mypath = self._abspath(path)
                    otherpath = other._abspath(path)
                    shutil.copy(mypath, otherpath)
                    if mode is not None:
                        os.chmod(otherpath, mode)
                except (IOError, OSError),e:
                    self._translate_error(e, path)
                count += 1
            return count
        else:
            return super(AnvLocalTransport, self).copy_to(relpaths, other, mode=mode, pb=pb)

    def listable(self):
        """See Transport.listable."""
        return True

    def list_dir(self, relpath):
        """Return a list of all files at the given location.
        WARNING: many transports do not support this, so trying avoid using
        it if at all possible.
        """
        path = self._abspath(relpath)
        try:
            entries = os.listdir(path)
        except (IOError, OSError), e:
            self._translate_error(e, path)
        return [urlutils.escape(entry) for entry in entries]

    def stat(self, relpath):
        """Return the stat information for a file.
        """
        path = relpath
        try:
            path = self._abspath(relpath)
            return os.lstat(path)
        except (IOError, OSError),e:
            self._translate_error(e, path)

    def lock_read(self, relpath):
        """Lock the given file for shared (read) access.
        :return: A lock object, which should be passed to Transport.unlock()
        """
        from bzrlib.lock import ReadLock
        path = relpath
        try:
            path = self._abspath(relpath)
            return ReadLock(path)
        except (IOError, OSError), e:
            self._translate_error(e, path)

    def lock_write(self, relpath):
        """Lock the given file for exclusive (write) access.
        WARNING: many transports do not support this, so trying avoid using it

        :return: A lock object, which should be passed to Transport.unlock()
        """
        from bzrlib.lock import WriteLock
        return WriteLock(self._abspath(relpath))

    def rmdir(self, relpath):
        """See Transport.rmdir."""
        path = relpath
        try:
            path = self._abspath(relpath)
            os.rmdir(path)
        except (IOError, OSError),e:
            self._translate_error(e, path)

    if osutils.host_os_dereferences_symlinks():
        def readlink(self, relpath):
            """See Transport.readlink."""
            return osutils.readlink(self._abspath(relpath))

    if osutils.hardlinks_good():
        def hardlink(self, source, link_name):
            """See Transport.link."""
            try:
                os.link(self._abspath(source), self._abspath(link_name))
            except (IOError, OSError), e:
                self._translate_error(e, source)

    if osutils.has_symlinks():
        def symlink(self, source, link_name):
            """See Transport.symlink."""
            abs_link_dirpath = urlutils.dirname(self.abspath(link_name))
            source_rel = urlutils.file_relpath(
                urlutils.strip_trailing_slash(abs_link_dirpath),
                urlutils.strip_trailing_slash(self.abspath(source))
            )

            try:
                os.symlink(source_rel, self._abspath(link_name))
            except (IOError, OSError), e:
                self._translate_error(e, source_rel)

    def _can_roundtrip_unix_modebits(self):
        if sys.platform == 'win32':
            # anyone else?
            return False
        else:
            return True
