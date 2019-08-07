import re
import os
import sys
from time import gmtime, strftime
import subprocess as sp
from argparse import ArgumentParser
import logging
import json

ConfigExtension = ".cfg"
LogExtension = ".log"

InstallationsSubKey = "SOFTWARE/Epic Games/Unreal Engine/Builds"

def init_arg_parser(parser):
    parser.add_argument("-d", "--debug",
                        action="store_true", dest="debug", default=False,
                        help="debug or not debug")
    parser.add_argument("-dd", "--onlydebug",
                        action="store_true", dest="onlyDebug", default=False,
                        help="is this only debug run with applying any changes")

# Custom logs formatter
class LogFormatter(logging.Formatter):
    FORMATTERS = {
        logging.CRITICAL : logging.Formatter("!!!PIZDETS!!!: %(module)s: %(lineno)d: %(msg)s"),
        logging.ERROR: logging.Formatter("ERROR: %(module)s: %(lineno)d: %(msg)s"),
        logging.WARNING: logging.Formatter("WARNING: %(module)s: %(lineno)d: %(msg)s"),
        logging.DEBUG: logging.Formatter("DBG: %(module)s: %(lineno)d: %(msg)s"),
        "DEFAULT": logging.Formatter("%(msg)s"),
        "DEFAULT_DEBUG": logging.Formatter("%(module)s: %(lineno)d: %(msg)s"),
    }

    def __init__(self, fmt="%(levelno)s: %(msg)s"):
        logging.Formatter.__init__(self, fmt)

    def format(self, record):
        defaultFormat = self.FORMATTERS['DEFAULT']
        if logging.root.level == logging.DEBUG:
            defaultFormat = self.FORMATTERS['DEFAULT_DEBUG']
        formatter = self.FORMATTERS.get(record.levelno, self.FORMATTERS['DEFAULT'])
        return formatter.format(record)

def process_parsed_args(ParsedArgs):
    fmt = LogFormatter()
    hdlr = logging.StreamHandler(sys.stdout)

    hdlr.setFormatter(fmt)
    logging.root.addHandler(hdlr)
    
    if ParsedArgs.debug or ParsedArgs.onlyDebug:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.INFO)

    return ParsedArgs.onlyDebug

def addParentDirToSysPath(filePath):
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(filePath)), os.pardir)))
