"""
:mod:`process` -- control processing of files
=============================================

.. module:: process
    :synopsis: Provides functions to control processing of files. The
               module records details of each file processed in a text file,
               which can then be looked up at a later time to determin if a
               file has previously been processed. It uses the MD5 checksum
               value of the file as the primary indicator of modifications to
               a file.

.. moduleauthor:: Craig Arthur <craig.arthur@ga.gov.au>

"""

import os
from os.path import join as pjoin
import logging
import configparser
import shutil
import glob

from files import flGetStat, flModDate

LOGGER = logging.getLogger(__name__)

GLOBAL_DATFILE = None
GLOBAL_CONFIGFILE = None
GLOBAL_PROCFILES = {}
GLOBAL_ARCHDIR = ""
GLOBAL_DATEFMT = "%Y%m%d%H%M"
GLOBAL_TIMESTAMP = True


def pInit(configFile):

    config = configparser.ConfigParser(
        allow_no_value=True, interpolation=configparser.ExtendedInterpolation()
    )
    config.optionxform = str
    config.read(configFile)
    pConfigFile(configFile)
    pDatFileName(config.get("Files", "DatFile"))
    pGetProcessedFiles(GLOBAL_DATFILE)
    pArchiveDir(config.get("Files", "ArchiveDir"))
    pArchiveDateFormat(
        config.get("Files", "ArchiveDateFormat", fallback=GLOBAL_DATEFMT)
    )


def pConfigFile(configFile=None):
    """
    Get or set the configuration filename

    :param str configFile: Path to the configuration file

    :returns: the globally-set value for the configuration file.
    """

    global GLOBAL_CONFIGFILE
    if configFile:
        GLOBAL_CONFIGFILE = configFile
    retval = GLOBAL_CONFIGFILE
    return retval


def pDatFileName(datFileName=None):
    """
    Get or set the dat file that holds the list of previously-processed files

    :param str datFileName: Path to the dat file

    :returns: the globally-set value of the dat file path
    """

    global GLOBAL_DATFILE
    rc = 0
    if datFileName:
        GLOBAL_DATFILE = datFileName
    retval = GLOBAL_DATFILE
    return retval


def pSetProcessedEntry(directory, filename, attr, value):
    """
    Update the attribute of the given file with the given value.

    :param str directory: Base directory of the file.
    :param str filename: File name.
    :param str attr: Name of the file attr to be updated.
    :param str value: Attribute value.

    """

    global GLOBAL_PROCFILES
    if directory in GLOBAL_PROCFILES:
        if filename in GLOBAL_PROCFILES[directory]:
            if attr in GLOBAL_PROCFILES[directory][filename]:
                GLOBAL_PROCFILES[directory][filename][attr] = value
            else:
                GLOBAL_PROCFILES[directory][filename].update({attr: value})
        else:
            GLOBAL_PROCFILES[directory].update({filename: {attr: value}})
    else:
        GLOBAL_PROCFILES.update({directory: {filename: {attr: value}}})


def pGetProcessedEntry(directory, filename, attr):
    """
    Retrieve the value of an attribute for a file from the
    GLOBAL_PROCFILES dictionary.

    :param str directory: Path name of the file.
    :param str filename: File name to retrieve the details of.
    :param str attr: Attribute to retrieve.

    :returns: Attribute value

    """
    LOGGER.debug(f"Checking processed files for {filename} with {attr}")
    try:
        value = GLOBAL_PROCFILES[directory][filename][attr]
        rc = value
    except KeyError:
        rc = 0
    return rc


def pGetProcessedFiles(datFile=None):
    """
    Retrieve a list of processed files from a dat file. This will also
    set the global `GLOBAL_DATFILE`.

    :param str datFileName: Name of a data file to read from.

    :returns: True if successfully read the data file, False otherwise.
    :rtype: bool

    """
    LOGGER.debug("Retrieving previously processed files")
    global GLOBAL_DATFILE
    rc = 0
    if datFile:
        GLOBAL_DATFILE = datFile
        try:
            fh = open(datFile)

        except IOError:
            LOGGER.warning(f"Couldn't open dat file {datFile}")
            return rc
        else:
            LOGGER.debug(f"Getting previously-processed files from {datFile}")
            for line in fh:
                line.rstrip("\n")
                directory, filename, moddate, md5sum = line.split("|")
                pSetProcessedEntry(directory, filename, "moddate", moddate.rstrip("\n"))  # noqa E501
                pSetProcessedEntry(directory, filename, "md5sum", md5sum.rstrip("\n"))  # noqa E501
            rc = 1
            fh.close()

    else:
        LOGGER.info("No dat file name provided - all files will be processed")
        return rc

    return rc


def pWriteProcessedFile(filename):
    """
    Write the various attributes of the given file to `GLOBAL_DATFILE`

    :param str filename: Name of file that has been processed.

    :returns: True if the attributes of the file are successfully
              stored in GLOBAL_PROCFILES and written to GLOBAL_DATFILE, False
              otherwise.
    :rtype: bool

    """
    global GLOBAL_DATFILE
    rc = 0
    if GLOBAL_DATFILE:
        directory, fname, md5sum, moddate = flGetStat(filename)
        try:
            LOGGER.debug(f"Opening dat file {GLOBAL_DATFILE} for writing")
            fh = open(GLOBAL_DATFILE, "a")
        except IOError:
            LOGGER.info(f"Cannot open {GLOBAL_DATFILE}")

        else:
            pSetProcessedEntry(directory, fname, "md5sum", md5sum)
            pSetProcessedEntry(directory, fname, "moddate", moddate)
            fh.write("|".join([directory, fname, moddate, md5sum]) + "\n")
            fh.close()
            rc = 1
    else:
        LOGGER.warning(
            ("Dat file name not provided. " f"Can't record {filename} as processed.")  # noqa E501
        )

    return rc


def pDeleteDatFile():
    """
    Delete the existing data file - defined in the `GLOBAL_DATFILE` variable
    (list of previously-processed files).

    :return: True if existing dat file successfully deleted,
             False otherwise
    :rtype: bool

    """

    rc = 0
    if os.unlink(GLOBAL_DATFILE):
        rc = 1
    else:
        LOGGER.warning(f"Cannot remove dat file {GLOBAL_DATFILE}")
    return rc


def pAlreadyProcessed(directory, filename, attribute, value):
    """
    Determine if a file has already been processed (i.e. it is stored in
    GLOBAL_PROCFILES)

    :param str directory: Base path of the file being checked.
    :param str filename: Name of the file.
    :param str attribute: Attribute name to be checked.
    :param str value: Value of the attribute to be tested.

    :return: True if the value matches that stored in GLOBAL_PROCFILES,
             False otherwise.
    :rtype: boolean

    """
    global GLOBAL_DATFILE
    rc = False
    if pGetProcessedEntry(directory, filename, attribute) == value:
        rc = True
    else:
        rc = False
    return rc


def pArchiveDir(archive_dir=None):
    """
    Set or get the archive directory. If setting the directory, its
    existence is checked and the directory is created.

    :param str archive_dir: Archive directory (if setting it).

    :return: The archive directory.
    :rtype: str

    :raises OSError: if the directory cannot be created

    """
    global GLOBAL_ARCHDIR

    if archive_dir:
        GLOBAL_ARCHDIR = archive_dir
        GLOBAL_ARCHDIR.rstrip("/\\")
        if not os.path.isdir(GLOBAL_ARCHDIR):
            try:
                os.makedirs(GLOBAL_ARCHDIR)
            except OSError:
                LOGGER.exception(f"Cannot create {GLOBAL_ARCHDIR}")
                raise OSError

    rc = GLOBAL_ARCHDIR

    return rc


def pArchiveDateFormat(date_format=None):
    """
    Set or get archive date format. Archived files can optionally have
    a date string inserted into the filename to retain all files with
    the same name, but different timestamps.

    :param str date_format: archive date format (if setting it)

    :return: archive date format
    :rtype: str

    """
    global GLOBAL_DATEFMT
    if date_format:
        GLOBAL_DATEFMT = date_format
    rc = GLOBAL_DATEFMT
    return rc


def pArchiveTimestamp(timestamp=False):
    """
    Set or get archive timstamp flag. If the flag is `True`, then
    files that are to be archived will have a timestamp inserted into
    the file name.

    :param bool timestamp: `True` or `False` (if setting it)

    :return: The value of `GLOBAL_TIMESTAMP`
    :rtype: bool

    """
    global GLOBAL_TIMESTAMP
    if timestamp:
        GLOBAL_TIMESTAMP = timestamp
    rc = GLOBAL_TIMESTAMP
    return rc


def pMoveFile(origin, destination):
    """
    Move a single file to an archive directory.

    :param str origin: Full path of the file to be moved.
    :param str destination: Full path of the file destination.

    :return: `True` if the file is successfully moved, `False` otherwise.
    :rtype: bool

    """
    try:
        shutil.move(origin, destination)
    except OSError as excmsg:
        LOGGER.warning(f"Error moving {origin} to {destination}")
        LOGGER.warning(excmsg)
        rc = 0
    else:
        LOGGER.debug(f"{origin} moved to {destination}")
        rc = 1

    return rc


def pArchiveFile(filename):
    """
    Move the file to the archive directory (if specified), inserting a
    timestamp in the name.

    :param str filename: Full path of the file to be archived.

    :return: `True` if the file is successfully moved, `False` otherwise.
    :rtype: bool

    """
    path, ext = os.path.splitext(filename)
    path, base = os.path.split(path)
    archive_dir = pArchiveDir()
    LOGGER.debug(f"Archiving {filename} to {archive_dir}")
    ext = ext.lstrip(".")
    if archive_dir:
        if os.path.isdir(archive_dir):
            pass
        else:
            try:
                os.makedirs(archive_dir)
            except OSError:
                LOGGER.critcal(f"Cannot create {archive_dir}")
                raise

    if pArchiveTimestamp():
        archive_date = flModDate(filename, GLOBAL_DATEFMT)
        archive_file_name = pjoin(archive_dir, f"{base}.{archive_date}.{ext}")
    else:
        archive_file_name = pjoin(archive_dir, f"{base}.{ext}")

    rc = pMoveFile(filename, archive_file_name)
    return rc


def pExpandFileSpec(config, spec, category):
    """
    Given a file specification and a category, list all files that match the
    spec and add them to the :dict:`g_files` dict. The `category` variable
    corresponds to a section in the configuration file that includes an item
    called 'OriginDir'. The given `spec` is joined to the `category`'s
    'OriginDir' and all matching files are stored in a list in
    :dict:`g_files` under the `category` key.

    :param config: `ConfigParser` object
    :param str spec: A file specification. e.g. '*.*' or 'IDW27*.txt'
    :param str category: A category that has a section in the source
                         configuration file
    """
    global GLOBAL_PROCFILES
    if category not in GLOBAL_PROCFILES:
        GLOBAL_PROCFILES[category] = []

    origindir = config.get(
        category, "OriginDir", fallback=config.get("Defaults", "OriginDir")
    )
    spec = pjoin(origindir, spec)
    files = glob.glob(spec)
    LOGGER.info(f"{len(files)} {spec} files to be processed")
    for file in files:
        if os.stat(file).st_size > 0:
            if file not in GLOBAL_PROCFILES[category]:
                GLOBAL_PROCFILES[category].append(file)


def pExpandFileSpecs(config, specs, category):
    for spec in specs:
        pExpandFileSpec(config, spec, category)
