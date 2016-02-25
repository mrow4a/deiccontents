import os, stat, sys
import ctypes
# UF_HIDDEN is a stat flag not defined in the stat module.
# It is used by BSD to indicate hidden files.
UF_HIDDEN = getattr(stat, 'UF_HIDDEN', 32768)
_win32_FILE_ATTRIBUTE_HIDDEN = 0x02

def is_hidden(abs_path, abs_root=''):
    """Is a file hidden or contained in a hidden directory?
    
    This will start with the rightmost path element and work backwards to the
    given root to see if a path is hidden or in a hidden directory. Hidden is
    determined by either name starting with '.' or the UF_HIDDEN flag as 
    reported by stat.
    
    Parameters
    ----------
    abs_path : unicode
        The absolute path to check for hidden directories.
    abs_root : unicode
        The absolute path of the root directory in which hidden directories
        should be checked for.
    """
    print "in is_hidden:, abs_path:%s, abs_root:%s"%(abs_path,abs_root)
    
    if not abs_root:
        abs_root = abs_path.split(os.sep, 1)[0] + os.sep
    inside_root = abs_path[len(abs_root):]
    if any(part.startswith('.') for part in inside_root.split(os.sep)):
        return True
    
    # check that dirs can be listed
    # may fail on Windows junctions or non-user-readable dirs
    if os.path.isdir(abs_path):
        try:
            os.listdir(abs_path)
        except OSError:
            return True
    
    # check UF_HIDDEN on any location up to root
    path = abs_path
    while path and path.startswith(abs_root) and path != abs_root:
        if not os.path.exists(path):
            path = os.path.dirname(path)
            continue
        try:
            # may fail on Windows junctions
            st = os.stat(path)
        except OSError:
            return True
        if getattr(st, 'st_flags', 0) & UF_HIDDEN:
            return True
        path = os.path.dirname(path)
    
    if sys.platform == 'win32':
        try:
            attrs = ctypes.windll.kernel32.GetFileAttributesW(py3compat.cast_unicode(path))
        except AttributeError:
            pass
        else:
            if attrs > 0 and attrs & _win32_FILE_ATTRIBUTE_HIDDEN:
                return True

    return False

def to_api_path(os_path, root=''):
    """Convert a filesystem path to an API path
    
    If given, root will be removed from the path.
    root must be a filesystem path already.
    """
    if os_path.startswith(root):
        os_path = os_path[len(root):]
    parts = os_path.strip(os.path.sep).split(os.path.sep)
    parts = [p for p in parts if p != ''] # remove duplicate splits
    path = '/'.join(parts)
    return path