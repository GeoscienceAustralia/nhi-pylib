.. role:: bash(code)
    :language: bash

.. role:: python(code)
    :language: python

nhi-pylib - helpful python scripts used in Natural Hazards and Impacts
======================================================================

A collection of helpful scripts to support processing and analysis. Predominantly, these are for teh Atmospheric Hazards team.

Instructions
------------

Clone this repo to your local machine. I have previously installed this to a
_lib_ folder in a workspace folder, but can be anywhere as long as you have
write permissions::

    git clone https://github.com/GeoscienceAustralia/nhi-pylib lib

Add the :bash:`nhi-pylib` path to your :bash:`PYTHONPATH` user environment variable. This is done by going to the Windows Settings and searching for "Edit environment variables for your account". Add or edit the :bash:`PYTHONPATH` variable to include the location of the :bash:`nhi-pylib` directory. **Make sure to append :bash:`python` to the end of the path.** If you have installed the :bash:`nhi-pylib` repo at :bash:`C:\Users\uname\nhi-pylib`, the environment variable must be set to :bash:`C:\Users\uname\nhi-pylib\python`.

What's inside
-------------

* :bash:`dtutils.py`: a bunch of datetime manipulation functions
* :bash:`files.py`: file manipulation functions, including configuration files, log files, file sizes, file versions
* :bash:`ftpclient.py`: A wrapper around the standard :python:`ftplib` library to establish "smart" ftp put/get commands
* :bash:`ftpscriptrunner.py`: Read and parse FTP commands from a text file and execute them using :python:`ftpclient.py`
* :bash:`sftpclient.py`: A wrapper around :python:`pysftp`, a secure FTP implementation - similar to :python:`ftpclient.py`
* :bash:`sftpscriptrunner.py`: Same as :python:`ftpscriptrunner.py`, but for secure FTP connections
* :bash:`metutils.py`: Meteorological functions (conversion between different variables & units, coriolis, etc.)
* :bash:`parallel.py`: base functions that set up a parallel processing environment
* :bash:`process.py`: Provides functions to control processing of files. Records details of each file processed in a text file, which can then be looked up at a later time to determine if a file has previously been processed.

There's a couple of others, but not really working as intended, or have been superceded.

There's no test suite for this codebase. Errors may not be well handled. No guarantee that it will work out of the box. Use at your own risk.
