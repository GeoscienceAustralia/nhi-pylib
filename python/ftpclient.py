import os
import re
import sys
import logging
import fnmatch

from ftplib import FTP
from datetime import datetime
import time

LOGGER = logging.getLogger(__name__)

global CONFIGFILE

global GFTP
global GASCII
global GBINARY
global GDATFILE
GFILES = {}
GLOBAL_DATFILE = None
GLOBAL_PROCFILES = {}
GASCII = True
GBINARY = False


class _FTP(FTP):
    """
    An enhanced :class:`ftplib.FTP` class that allows checking of whether files
    have previously been either retrieved from or sent to an FTP server.

    """

    def __init__(self, config, host='', user='', acct='', timeout=None,
                 source_address=None):
        super(_FTP, self).__init__(host, user, acct, timeout, source_address)

        self.gascii = True
        self.gbinary = False
        self.options = ''
        self.g_pwd = None
        self.g_use_pwd = True
        self.g_dir_list = {}
        self.g_dir_fail_bail = 0
        self.g_processed_files = {}

        # Attributes that need to be defined when the
        # class is instantiated:
        self.registered = config.getboolean('Options', 'Registered',
                                            fallback=False)
        self.datfilename = config.get('Files', 'DatFile')
        self.new_dat_file = config.getboolean('Files', 'NewDatFile',
                                              fallback=False)
        self.getProcessedFiles()
        if self.new_dat_file:
            self.DeleteDatFile()

        # Messages:
        self.g_transfer_complete = '226 Transfer complete.'
        self.g_transfer_failed = '550 Failed to open file.'

    def DeleteDatFile(self):
        """
        Remove existing dat file

        :returns: `True` if successfully deleted, `False` otherwise
        """
        rc = False
        try:
            os.unlink(self.datfilename)
            rc = True
        except FileNotFoundError:
            LOGGER.warning(("Unable to delete existing dat file"
                            f"{self.datfilename}"))
            rc = False
        return rc

    def binary(self):
        self.gbinary = True
        self.gascii = False

    def ascii(self):
        self.gascii = True
        self.gbinary = False

    def resetDirEntry(self):
        self.g_dir_list = {}

    def setDirEntry(self, directory, filename, entry):
        if directory in self.g_dir_list:
            self.g_dir_list[directory].update({filename: entry})
        else:
            self.g_dir_list.update({directory: {filename: entry}})

    def getDirEntry(self, directory, filename):
        try:
            value = self.g_dir_list[directory][filename]
        except KeyError:
            LOGGER.warn(f"No directory entry for {directory}: {filename}")
            value = None
        return value

    def dirList(self, directory):
        """
        Return whether the directory listing dict contains `directory` as a key

        :param str directory: Name of the directory being checked

        :returns: `True` if the `g_dir_list` attribute of the class has
        `directory` as a key.
        """
        rc = directory in self.g_dir_list.keys()
        return rc

    def setProcessedEntry(self, directory, filename, putget, attribute, value):
        """
        Update the processed files hash with details of the given file

        :param str directory: Directory where the file is stored
        :param str filename: Name of the file
        :param str putget: Either 'put' or 'get', depending whether putting or
        retrieving a file from a remote server.
        :param str attribute: Name of the attribute to store. Should be one
        of 'date', 'md5sum' or 'direntry'
        :param str value: Value of the attribute.
        """

        if directory in self.g_processed_files:
            if filename in self.g_processed_files[directory]:
                if putget in self.g_processed_files[directory][filename]:
                    self.g_processed_files[directory][filename][putget].\
                        update({attribute: value})
                else:
                    self.g_processed_files[directory][filename].\
                        update({putget: {attribute: value}})
            else:
                self.g_processed_files[directory].\
                    update({filename: {putget: {attribute: value}}})
        else:
            self.g_processed_files.\
                update({directory: {filename: {putget: {attribute: value}}}})

    def getProcessedEntry(self, directory, filename, putget, attribute):
        """
        Retrieve the `attribute` value from the processed files hash, given the
        directory, filename, 'put' or 'get'.

        """
        value = None
        try:
            value = self.g_processed_files[directory][filename][putget][attribute]
        except KeyError as e:
            LOGGER.debug(f"No entry {e} in list of processed files")
            pass

        return value

    def writeProcessedFile(self, directory, filename, putget,
                           date, direntry, md5sum):
        """
        Write the details of a file to a dat file
        :param str directory: Directory where the file is stored
        :param str filename: Name of the file
        :param str putget: Either 'put' or 'get', depending whether putting or
        retrieving a file from a remote server.
        :param str date: Date string for the modified time of the file
        :param str direntry: A formatted directory entry returned by the
        LIST ftp command
        :param str md5sum: String representation of the MD5 hash of the file (changes
        if there's any modification to the data in the file)

        """
        try:
            fh = open(self.datfilename, 'a')
        except IOError:
            LOGGER.info("Cannot open %s", self.datfilename)
            rc = 0
        else:
            fh.write('|'.join([directory, filename, putget, date, direntry, md5sum]) + '\n')
            self.setProcessedEntry(directory, filename, putget, 'moddate', date)
            self.setProcessedEntry(directory, filename, putget, 'md5sum', md5sum)
            self.setProcessedEntry(directory, filename, putget, 'direntry', direntry)
            fh.close()
            rc = 1
        return rc

    def getProcessedFiles(self):
        """
        Get a list of previously processed files, and store them in the
        g_processed_files hash.
        """
        rc = 0
        try:
            fh = open(self.datfilename)

        except IOError:
            LOGGER.warn(f"Couldn't open dat file {self.datfilename}")
            return rc
        else:
            LOGGER.info(("Getting previously-processed files from "
                         f"{self.datfilename}"))
            for line in fh:
                line.rstrip('\n')
                directory, filename, putget, moddate, direntry, md5sum = line.split('|')
                self.setProcessedEntry(directory, filename, putget, 'moddate', moddate)
                self.setProcessedEntry(directory, filename, putget, 'md5sum', md5sum)
                self.setProcessedEntry(directory, filename, putget, 'direntry', direntry)
            rc = 1
            fh.close()

        return rc

    def get(self, filename, newfilename=None):
        """
        Retrieve a single file

        :param str filename: Name of the file to retrieve from the remote
        server
        :param str newfilename: (Optional) store the file locally with a new
        name.
        """
        directory = self.pwd()
        if not self.dirList(directory):
            self.cacheDirList(directory)

        direntry = self.getDirEntry(directory, filename)
        processedEntry = self.getProcessedEntry(
            directory, filename, 'get', 'direntry'
        )
        if (processedEntry == direntry) and direntry is not None:
            if self.new_dat_file:
                self.writeProcessedFile(directory, filename,
                                        'get', '', direntry, '')
            LOGGER.info(f"{filename} already fetched")
        else:
            LOGGER.info(f"Retrieving {filename}")
            if self.gascii:
                rc = self.retrlines(filename, newfilename)
            else:  # self.gbinary == True
                rc = self.retrbinary(filename, newfilename)
            if rc:
                if direntry:
                    self.writeProcessedFile(directory, filename,
                                            'get', '', direntry, '')
                else:
                    LOGGER.info("Not writing...")
            else:
                LOGGER.warn(f"Get {filename} failed: {rc}")

    def retrlines(self, filename, newfilename=None):
        """
        Retrieve a file in ascii mode

        :param str filename: Name of the file on the remote server
        :param str newfilename: optional new name for the file to be stored as
        locally (if `None`, then filename is unchanged)

        :returns: `True` if the transfer was successful, `False` otherwise.
        """
        destfile = newfilename if newfilename != None else filename

        with open(destfile, 'w') as fh:
            def writer(line):
                fh.write(line + '\n')
            try:
                ret = super().retrlines(f"RETR {filename}", writer)
            except Exception as e:
                LOGGER.warning(f"{e} {filename}")
                ret = e

        if ret == self.g_transfer_complete:
            return True
        elif ret == self.g_transfer_failed:
            os.unlink(destfile)
            return False
        else:
            os.unlink(destfile)
            return False

    def retrbinary(self, filename, newfilename=None):
        """
        Retrieve a file in binary mode

        :param str filename: Name of the file on the remote server
        :param str newfilename: optional new name for the file to be stored as
        locally (if `None`, then filename is unchanged)

        :returns: `True` if the transfer was successful, `False` otherwise.
        """
        destfile = newfilename if newfilename != None else filename
        with open(destfile, 'wb') as fh:
            try:
                ret = super().retrbinary(f"RETR {filename}", fh.write)
            except Exception as e:
                LOGGER.warning(f"{e} {filename}")
                ret = e
        if ret == self.g_transfer_complete:
            return True
        else:
            os.unlink(destfile)
            return False

    def mget(self, inputfile, recursive=False, newfilename=None):
        """
        Retrieve a collection of files matching a file pattern

        :param str inputfile: The file pattern to match (a `glob` style
        pattern)
        :param bool recursive: If `True` recursively search the current working
        directory (on the remote server) for files that match `inputfile`.
        :param str newfilename: Optional new name for the files to be stored as
        locally (if `None` then file names are unchanged)

        :returns: None
        """
        if inputfile:
            LOGGER.debug(f"mget {inputfile}")

        head, tail = os.path.split(inputfile)
        if head == '':
            filepattern = inputfile
        else:
            filepattern = tail
        if head == '':
            path = self.pwd()
        else:
            self.cwd(head)

        dirlisting = self.dirlist(path)
        for entry in dirlisting:
            filename, filetype = FileName(entry)

            if filetype == 'f':
                if fileMatch(filepattern, filename):
                    self.get(filename, newfilename)
            elif (filetype == 'd' and recursive):
                self.mget(os.path.join(path, filename), recursive, newfilename)
        return

    def quit(self):
        """
        Close the FTP connection
        """
        retval = super().quit()
        if retval:
            LOGGER.info(retval)

    def size(self, filename):
        """
        Retrieve file size of a file

        :param str filename: Filename to get size info

        """
        flsize = super().size(filename)
        if flsize is None:
            # FTP.size() returns None on failure, not an exception
            LOGGER.warning(f"Remote size failed: {filename}")
        return flsize

    def cwd(self, directory):
        """
        Change to the given directory

        :param str directory: Path on the remote server
        """
        self.g_pwd = None  # Reset the cached present directory
        if self.registered:
            self.resetDirEntry()
        if directory == '':
            LOGGER.warn(f"WHY? changing to current directory")
        try:
            super().cwd(directory)
            LOGGER.debug(f"cd to {directory}")
        except:
            LOGGER.exception(f"Failed to change directory: {directory}")

    def pwd(self):
        """
        Return the present working directory on the server
        connection

        """
        if self.registered:
            retval = '.'
        elif self.g_pwd and self.g_use_pwd:
            retval = self.g_pwd
        else:
            retval = super().pwd()
            self.g_pwd = retval
            if not retval:
                LOGGER.warning(f"PWD command failed")
        LOGGER.debug(f"PWD = {retval}")
        return retval

    def dirlist(self, directory, recursive=False):
        dirlist = []
        super().retrlines('LIST', dirlist.append)
        if len(dirlist) > 1:
            [LOGGER.debug(d) for d in dirlist]
            if recursive:
                for d in dirlist:
                    if d.startswith('d'):
                        subdir = d.split(' ')[-1]
                        self.dirlist(os.path.join(directory, subdir))
        else:
            LOGGER.warn(f"{directory} is empty")

        return dirlist

    def cacheDirList(self, directory=None):
        if directory is None:
            directory = self.pwd()
        dirlist = []
        super().retrlines('LIST', dirlist.append)
        if len(dirlist) > 1:
            LOGGER.info(f"Caching directory listing for {directory}")
            for entry in dirlist:
                filename = FileName(entry)[0]
                self.setDirEntry(directory, filename, entry)
        else:
            if self.g_dir_fail_bail < 3:
                LOGGER.warning((f"Directory {directory} is empty "
                                "or does not exist"))
                self.g_dir_fail_bail += 1
            else:
                LOGGER.exception((f"Directory {directory} is empty "
                                  "or does not exist"))
                sys.exit()

        return dirlist

    def interpretScriptLine(self, line):
        """
        Interpret a line from an FTP script file and translate it to the
        appropriate method on an FTP connection.

        :param str cmd: FTP command
        :param args: Optional arguments to pass to the command.

        """
        if line is not None:
            line = line.split("#")[0]
            myargs = line.split(" ")
            if myargs:
                cmd = myargs.pop(0)
            else:
                return

            if re.match("^host$", cmd):
                self.hostname = myargs[0]
            elif re.match("^port$", cmd):
                self.port = myargs[0]
            elif re.match("^options$", cmd):
                self.options = ' '.join(myargs)
            elif re.match("^connect$", cmd, re.I):
                super(_FTP, self).__init__(self.hostname, self.options)
            elif re.match("^user$", cmd):
                self.username = myargs[0]
            elif re.match("^password$", cmd):
                self.userpass = myargs[0]
            elif re.match("^login$", cmd, re.I):
                self.login(self.username, self.userpass)
            elif re.match("^ascii$", cmd, re.I):
                self.gascii = True
                self.gbinary = False
            elif re.match("^binary$", cmd, re.I):
                self.gbinary = True
                self.gascii = False
            elif re.match("^cd$", cmd, re.I):
                self.cwd(myargs[0])
            elif re.match("^size$", cmd, re.I):
                self.size(myargs[0])

            elif re.match("^get$", cmd, re.I):
                self.get(myargs[0])
            elif re.match("^mget$", cmd, re.I):
                self.mget(myargs[0])

            elif re.match("^quit$", cmd, re.I):
                self.quit()
            elif re.match("^bye$", cmd, re.I):
                self.quit()


def fileMatch(pattern, filename, matchcase=True):
    match = False
    regex = fnmatch.translate(pattern)
    if matchcase:
        if re.match(regex, filename, re.I):
            match = True
    else:
        if re.match(regex, filename):
            match = True
    return match


def FileName(entry):
    """
    Get a file name from a directory entry
    e.g.:
    d---------   1 owner    group               0 Apr 28 23:24 sub1
    returns ( 'sub1', 'd' );

    ----------   1 owner    group              31 Apr 28 23:24 F432213.pgp
    returns ( 'F432213.pgp', 'f' )

    :param str entry: A directory listing entry.
    """
    if entry.startswith('d'):
        entrytype = 'd'
    elif entry.startswith('-'):
        entrytype = 'f'
    elif re.match(r"^\d{4,4}\-\d{2,2}\-\d{2,2}", entry):
        if re.match(r"\<DIR\>", entry):
            entrytype = 'd'
        else:
            entrytype = 'f'
    filedetails = entry.split(' ')
    filename = filedetails[-1]
    return (filename, entrytype)
