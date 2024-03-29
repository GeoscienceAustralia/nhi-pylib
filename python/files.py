import os
import sys
import logging

import datetime
import numpy as np
from time import ctime, localtime, strftime
from git import Repo, InvalidGitRepositoryError

import hashlib

LOGGER = logging.getLogger(__name__)

if not getattr(__builtins__, "WindowsError", None):

    class WindowsError(OSError):
        pass


flDateFormat = "%Y-%m-%d %H:%M:%S"


def flGetDateFormat():
    global flDateFormat
    return flDateFormat


def flSetDateFormat(fmt=None):
    global flDateFormat
    if fmt:
        flDateFormat = fmt
    return flDateFormat


def flModulePath(level=1):
    """
    Get the path of the module <level> levels above this function

    :param int level: level in the stack of the module calling this function
                      (default = 1, function calling ``flModulePath``)

    :returns: path, basename and extension of the file containing the module

    Example: path, base, ext = flModulePath( )
    Calling flModulePath() from "/foo/bar/baz.py" produces the result
    "/foo/bar", "baz", ".py"
    """
    filename = os.path.realpath(sys._getframe(level).f_code.co_filename)
    path, fname = os.path.split(filename)
    path.replace(os.path.sep, "/")
    base, ext = os.path.splitext(fname)
    return path, base, ext


def flModuleName(level=1):
    """
    Get the name of the module <level> levels above this function

    :param int level: Level in the stack of the module calling this function
                      (default = 1, function calling ``flModuleName``)
    :returns: Module name.
    :rtype: str

    Example: mymodule = flModuleName( )
    Calling flModuleName() from "/foo/bar/baz.py" returns "baz"

    """
    package = sys._getframe(level).f_code.co_name
    return package


def flProgramVersion(path=""):
    """
    Return the latest tag and/or commit of the git repo (if it is a git repo)

    :param str path: Path of the executing program
    """
    try:
        r = Repo(path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        LOGGER.warning("No version information available")
        return " "
    else:
        try:
            tag = r.tags[-1]
        except IndexError:
            LOGGER.warn("No tagged versions")
            tag = ""
        commit = str(r.commit("HEAD"))
        return f"{tag} ({commit})"


def flGitRepository(filepath: str):
    """
    Get basic git repo information for a given file

    :param filepath: Full or relative path of the file
    :type filepath: str
    """

    filepath = os.path.abspath(filepath)
    try:
        r = Repo(filepath, search_parent_directories=True)
    except (InvalidGitRepositoryError, TypeError):
        LOGGER.warn("No version information available")
        mtime = os.path.getmtime(os.path.realpath(filepath))
        dt = datetime.datetime.fromtimestamp(mtime).strftime(flDateFormat)
        url = filepath
        commit = "unknown"
        tag = ""
        return commit, tag, dt, url
    else:
        commit = str(r.commit("HEAD"))
        dt = r.commit("HEAD").committed_datetime.strftime(flDateFormat)
        root = r.git.rev_parse("--show-toplevel")
        try:
            remote_url = r.remotes.origin.url
            relfilepath = os.path.relpath(filepath, root)
            url = remote_url.rstrip(".git") + "/blob/master/" + relfilepath
        except AttributeError:
            LOGGER.warn("No remote URL for the repo")
            url = ""
        try:
            tag = r.tags[-1]
        except IndexError:
            LOGGER.warn("No tags available for this repo")
            tag = ""
        return commit, tag, dt, url


def flLoadFile(filename, comments="%", delimiter=",", skiprows=0):
    """
    Load a delimited text file -- uses :func:`numpy.genfromtxt`

    :param filename: File, filename, or generator to read
    :type  filename: file or str
    :param comments: (default '%') indicator
    :type  comments: str, optional
    :param delimiter: The string used to separate values.
    :type  delimiter: str, int or sequence, optional

    """
    return np.genfromtxt(
        filename, comments=comments, delimiter=delimiter, skip_header=skiprows
    )


def flSaveFile(filename, data, header="", delimiter=",", fmt="%.18e"):
    """
    Save data to a file.

    Does some basic checks to ensure the path exists before attempting
    to write the file. Uses :class:`numpy.savetxt` to save the data.

    :param str filename: Path to the destination file.
    :param data: Array data to be written to file.
    :param str header: Column headers (optional).
    :param str delimiter: Field delimiter (default ',').
    :param str fmt: Format statement for writing the data.

    """

    directory = os.path.dirname(filename)
    if not os.path.isdir(directory):
        os.makedirs(directory)

    try:
        np.savetxt(
            filename, data, header=header, delimiter=delimiter, fmt=fmt, comments="%"  # noqa E501
        )
    except TypeError:
        np.savetxt(filename, data, delimiter=delimiter, fmt=fmt, comments="%")


def flGetStat(filename, CHUNK=2**16):
    """
    Get basic statistics of filename - namely directory, name (excluding
    base path), md5sum and the last modified date. Useful for checking
    if a file has previously been processed.

    NOTE: This can be slow for large files, as the file is opened and read to
    evaluate the MD5 checksum.

    :param str filename: Filename to check.
    :param int CHUNK: (optional) chunk size (for md5sum calculation).

    :returns: path, name, md5sum, modification date for the file.
    :raises TypeError: if the input file is not a string.
    :raises IOError: if the file is not a valid file, or if the file
                     cannot be opened.

    Example: dir, name, md5sum, moddate = flGetStat(filename)

    """
    try:
        fh = open(filename)
        fh.close()
    except (IOError, WindowsError):
        LOGGER.exception("Cannot open %s" % (filename))
        raise IOError("Cannot open %s" % (filename))

    try:
        directory, fname = os.path.split(filename)
    except TypeError:
        LOGGER.exception("Input file is not a string")
        raise TypeError("Input file is not a string")

    try:
        si = os.stat(filename)
    except IOError:
        LOGGER.exception("Input file is not a valid file: %s" % (filename))
        raise IOError("Input file is not a valid file: %s" % (filename))

    moddate = ctime(si.st_mtime)
    m = hashlib.md5()
    f = open(filename, "rb")

    while 1:
        chunk = f.read(CHUNK)
        if not chunk:
            break
        m.update(chunk)
    f.close()
    md5sum = m.hexdigest()

    return directory, fname, md5sum, moddate


def flConfigFile(extension=".ini", prefix="", level=None):
    """
    Build a configuration filename (default extension .ini) based on the
    name and path of the function/module calling this function. Can also
    be useful for setting log file names automatically.
    If prefix is passed, this is preprended to the filename.

    :param str extension: file extension to use (default '.ini'). The
                          period ('.') must be included.
    :param str prefix: Optional prefix to the filename (default '').
    :param level: Optional level in the stack of the main script
                  (default = maximum level in the stack).
    :returns: Full path of calling function/module, with the source file's
              extension replaced with extension, and optionally prefix
              inserted after the last path separator.

    Example: configFile = flConfigFile('.ini')
    Calling flConfigFile from /foo/bar/baz.py should return /foo/bar/baz.ini

    """

    if not level:
        import inspect

        level = len(inspect.stack())

    path, base, ext = flModulePath(level)
    config_file = os.path.join(path, prefix + base + extension)
    return config_file


def flStartLog(logFile, logLevel, verbose=False, datestamp=False, newlog=True):
    """
    Start logging to logFile all messages of logLevel and higher.
    Setting ``verbose=True`` will report all messages to STDOUT as well.

    :param str logFile: Full path to log file.
    :param str logLevel: String specifiying one of the standard Python logging
                         levels ('NOTSET','DEBUG','INFO','WARNING','ERROR',
                         'CRITICAL')
    :param boolean verbose: ``True`` will echo all logging calls to STDOUT
    :param boolean datestamp: ``True`` will include a timestamp of the creation
                              time in the filename.
    :param boolean newlog: ``True`` will create a new log file each time this
                           function is called. ``False`` will append to the
                           existing file.

    :returns: :class:`logging.logger` object.

    Example: flStartLog('/home/user/log/app.log', 'INFO', verbose=True)
    """
    if datestamp:
        base, ext = os.path.splitext(logFile)
        curdate = datetime.datetime.now()
        curdatestr = curdate.strftime("%Y%m%d%H%M")
        # The lstrip on the extension is required as splitext leaves it on.
        logFile = "%s.%s.%s" % (base, curdatestr, ext.lstrip("."))

    logDir = os.path.dirname(os.path.realpath(logFile))
    if not os.path.isdir(logDir):
        try:
            os.makedirs(logDir)
        except OSError:
            # Unable to create the directory, so stick it in the
            # current working directory:
            fname = os.path.basename(logFile)
            logFile = os.path.join(os.getcwd(), fname)

    if newlog:
        mode = "w"
    else:
        mode = "a"

    logging.basicConfig(
        level=getattr(logging, logLevel),
        format="%(asctime)s: %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=logFile,
        filemode=mode,
    )
    LOGGER = logging.getLogger()

    if len(LOGGER.handlers) < 2:
        # Assume that the second handler is a StreamHandler for verbose
        # logging. This ensures we do not create multiple StreamHandler
        # instances that will *each* print to STDOUT
        if verbose:
            console = logging.StreamHandler(sys.stdout)
            console.setLevel(getattr(logging, logLevel))
            formatter = logging.Formatter(
                "%(asctime)s: %(levelname)s %(message)s",
                "%H:%M:%S",
            )
            console.setFormatter(formatter)
            LOGGER.addHandler(console)

    basepath = os.path.dirname(sys.argv[0])
    LOGGER.info(f"Started log file {logFile} (detail level {logLevel})")
    LOGGER.info(f"Running {sys.argv[0]} (pid {os.getpid()})")
    LOGGER.info(f"Program version {flProgramVersion(basepath)}")
    return LOGGER


def flLogFatalError(tblines):
    """
    Log the error messages normally reported in a traceback so that
    all error messages can be caught, then exit. The input 'tblines'
    is created by calling ``traceback.format_exc().splitlines()``.

    :param list tblines: List of lines from the traceback.

    """
    for line in tblines:
        LOGGER.critical(line.lstrip())
    sys.exit()


def flModDate(filename, dateformat="%Y-%m-%d %H:%M:%S"):
    """
    Return the last modified date of the input file

    :param str filename: file name (full path).
    :param str dateformat: Format string for the date (default
                           '%Y-%m-%d %H:%M:%S')
    :returns: File modification date/time as a string
    :rtype: str

    Example: modDate = flModDate('C:/foo/bar.csv' ,
                                 dateformat='%Y-%m-%dT%H:%M:%S')
    """
    try:
        si = os.stat(filename)
    except (IOError, WindowsError):
        LOGGER.exception("Input file is not a valid file: %s" % (filename))
        raise IOError("Input file is not a valid file: %s" % (filename))
    moddate = localtime(si.st_mtime)
    if dateformat:
        return strftime(dateformat, moddate)
    else:
        return datetime.datetime(*moddate[:6])


def flSize(filename):
    """
    Return the size of the input file in bytes

    :param str filename: Full path to the file.
    :returns: File size in bytes.
    :rtype: int

    Example: file_size = flSize( 'C:/foo/bar.csv' )
    """
    try:
        si = os.stat(filename)
    except (IOError, WindowsError):
        LOGGER.exception("Input file is not a valid file: %s" % (filename))
        raise OSError("Input file is not a valid file: %s" % (filename))
    else:
        size = si.st_size

    return size


def flPathTime(path):
    """
    Retrieve the modified time of a folder

    :param str file: Full path to a valid folder

    :returns: ISO-format of the modification time of the file
    """
    mtime = max(os.stat(root).st_mtime for root, _, _ in os.walk(path))
    dt = datetime.datetime.fromtimestamp(mtime)
    return dt.strftime(flDateFormat)
