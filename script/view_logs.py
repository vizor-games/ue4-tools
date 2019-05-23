import re
import os
import sys
from time import gmtime, strftime
import subprocess as sp
from argparse import ArgumentParser
import logging
import common as cm
from ue import path as ue_path
from ue import project as ue_proj

cm.addParentDirToSysPath(__file__)
import config as cfg


LOG_EXTENSION = ".log"
ProcessedLogLabel = "_processed"


def get_log_path_from_dir(somePath):
    logFilePath = None
    projectName = None
    logsPath = None
    projectRootPath = ue_path.get_project_root_path_from_path(somePath)
    if projectRootPath:
        logging.debug("Found UE project root directory, using it '" + projectRootPath + "'");
        projectName = ue_path.get_project_name_from_path(projectRootPath)
        logsPath = os.path.join(projectRootPath, ue_path.LOGS_PATH);
    else:
        buildRootPath = ue_path.get_build_root_path_from_path(somePath)
        if buildRootPath:
            logging.debug("Found UE build root directory, using it '" + buildRootPath + "'");
            projectName = ue_proj.split_build_name(ue_path.get_build_name_from_path(buildRootPath))[0]
            logsPath = os.path.join(buildRootPath, projectName, ue_path.LOGS_PATH);

    if projectName is not None:
        logFileName = projectName + LOG_EXTENSION
        logFilePath = os.path.join(logsPath, logFileName)

    return logFilePath


def get_log_path(logPath):
    logging.debug("Getting log file from '" + str(logPath) + "'")
    logFilePath = None
    dirPath = None

    if logPath is not None:
        if os.path.isfile(logPath):
            logging.debug("Source path '" + logPath + "' is file")
            logFilePath = logPath
        elif os.path.isdir(logPath):
            logging.debug("Source path '" + logPath + "' is dir")
            dirPath= logPath

    if logFilePath is None:
        if dirPath is not None:
            logging.debug("Trying to deduce log file from directory'" + dirPath + "'");
        else:
            dirPath = os.getcwd();
            logging.debug("Source path is invalid, trying to deduce log file from script location'" + dirPath + "'");
        logFilePath = get_log_path_from_dir(dirPath)

    if logFilePath is not None:
        if os.path.isfile(logFilePath):
            logging.info("Working with log file '" + logFilePath + "'")
        else:
            logging.info("Log file is absent '" + logFilePath + "'")
    else:
        logging.error("Could not deduce log file from provided source '" + logPath + "' or current path.")

    return logFilePath

def apply_rule(pattern, repl, string, count=0, flags=0):
    logging.info("Changing " + "%r"%pattern + " to " + "%r"%repl + "")
    return re.sub(pattern, repl, string, count, flags)

def filter_rule_to_config(pattern, repl, flags=0):
    return { 'pattern': pattern, 'repl': repl, 'flags': flags }

def filter_rule_from_config(filterRuleConfig):
    logging.debug("Rule:" + str(filterRuleConfig))
    return filterRuleConfig['pattern'], filterRuleConfig['repl'], filterRuleConfig['flags']

def filter_clean_category(logCategory):
    return filter_rule_to_config('.*' + logCategory +': ', '', re.M)

def filter_remove_category(logCategory):
    return filter_rule_to_config('.*' + logCategory + ': .*\n', '', re.M)

def filter_remove_lines_with(someText):
    return filter_rule_to_config('.*' + someText + '.*\n', '', re.M)

def filter_remove_data_before_category(logCategory):
    return filter_rule_to_config('.*' + logCategory + ': ', logCategory + ': ', re.M)

def process_log_file(FilePath):
    with open (FilePath, 'r' ) as f:
        content = f.read()

    try:
        for rule in cfg.ViewLogs.FILTER_RULES:
            pattern, repl, flags = filter_rule_from_config(rule)
            content = apply_rule(pattern, repl, content, flags = flags)
    except AttributeError:
        logging.warning("Error when applying rules. Wrong ViewLogs.FILTER_RULES in config?")
    
    return content

def save_processed_log(processedLogContents, savePath):
    if processedLogContents is not None:
        fileName = "_Processed_" + strftime("%Y.%m.%d-%H.%M.%S", gmtime()) + ".log"
        filePath = os.path.join(savePath, fileName)
        print ("Saving log to '" + filePath + "'")

        with open (filePath, 'w' ) as f:
            f.write(processedLogContents)
        return filePath

def get_log_editor_path():
    try:
        logEditorPath = cfg.ViewLogs.EDITOR_PATH
        logging.debug("Editor path: " + str(logEditorPath))

        if os.path.isfile(logEditorPath):
            return logEditorPath
        else:
            logging.warning("Editor with given path does not exist: '" + logEditorPath + "'")
    except AttributeError:
        logging.warning("Error when accessing ViewLogs.EDITOR_PATH attribute from config.")


class LogViewer:
    def run(self):
        filePath = self.init()
        if filePath:
            processedFileContents = process_log_file(filePath)
            logEditorPath = get_log_editor_path()
            if not self.onlyDebug:
                processedFilePath = save_processed_log(processedFileContents, os.path.dirname(filePath))
                if logEditorPath:
                    sp.Popen([logEditorPath, processedFilePath])
                else:
                    logging.info("Unable to run editor.")

    def init(self):
        sourcePath = self.process_args()
        logging.debug("SourcePath: " + str(sourcePath))
        filePath = get_log_path(sourcePath)
        if filePath and os.path.isfile(filePath):
            return filePath

    def process_args(self):
        parser = ArgumentParser()
        cm.init_arg_parser(parser)
        parser.add_argument("shellsource",
                            help="directory inside of UE project or build, set by calling shell script", metavar="SHELL_SOURCE")
        parser.add_argument("-s", "--source", dest="source",
                            help="directory inside of UE project or build, set by user, overrides value of 'shellsource' aurgument", 
                            metavar="SOURCE")

        parsedArgs = parser.parse_args()
        self.onlyDebug = cm.process_parsed_args(parsedArgs)

        logging.debug("Parsing arguments: '" + ' '.join(sys.argv[1:]) + "'")
        logging.debug("Result is: " + str(parsedArgs))

        if not parsedArgs.source:
            parsedArgs.source = parsedArgs.shellsource

        return parsedArgs.source

def main():
    print("View logs for Unreal Engine")
    logViewer = LogViewer()
    logViewer.run()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted by user')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)