import os
from os.path import isdir, dirname, realpath, join as pjoin
from configparser import ConfigParser
import argparse
import sftpclient

from files import flStartLog

import logging
LOGGER = logging.getLogger()


def main():
    p = argparse.ArgumentParser()

    p.add_argument('-c', '--config_file',
                   help="Configuration file")
    p.add_argument('-v', '--verbose',
                   help="Verbose output",
                   action='store_true')

    args = p.parse_args()
    configFile = args.config_file
    verbose = args.verbose
    config = ConfigParser()
    config.read(configFile)

    logFile = config.get('Logging', 'LogFile')
    logdir = dirname(realpath(logFile))

    # if log file directory does not exist, create it
    if not isdir(logdir):
        try:
            os.makedirs(logdir)
        except OSError:
            logFile = pjoin(os.getcwd(), 'fetch.log')

    logLevel = config.get('Logging', 'LogLevel', fallback='INFO')
    verbose = config.getboolean('Logging', 'Verbose', fallback=False)
    datestamp = config.getboolean('Logging', 'Datestamp', fallback=False)
    if args.verbose:
        verbose = True
    LOGGER = flStartLog(logFile, logLevel, verbose, datestamp)

    destDir = config.get('Files', 'Destination')
    if not isdir(destDir):
        try:
            LOGGER.debug(f"Creating {destDir}")
            os.makedirs(destDir)
        except OSError as errmsg:
            LOGGER.exception(f"Cannot create {destDir}")
            LOGGER.exception(errmsg)
    os.chdir(destDir)
    ftpScript = config.get('Files', 'FTPScript')
    run(config, ftpScript)


def run(config, script):
    """
    Run a fetch script
    """

    LOGGER.info(f"Running FTP script: {script}")
    SFTP = sftpclient._SFTP(config)

    with open(script, 'r') as fh:
        for line in fh:
            LOGGER.debug(f"{line}")
            SFTP.interpretScriptLine(line.rstrip())
    LOGGER.info("Finished FTP script")


main()
