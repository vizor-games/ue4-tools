import re
import os
import sys
from time import gmtime, strftime
import subprocess as sp
from argparse import ArgumentParser
import logging
import json
import common as cm
from ue import path as ue_path
from ue import project as ue_proj


class Inspector:
    def run(self):
        initResult = self.init()
        if initResult:
            sourcePath = initResult
            self.inspect(sourcePath)

    def init(self):
        sourcePath = self.process_args()
        logging.debug("Input SourcePath: " + str(sourcePath))
        if os.path.isdir(sourcePath):
            return sourcePath
        else:
            logging.warning("SourcePath is invalid: " + str(sourcePath))

    def process_args(self):
        parser = ArgumentParser()
        cm.init_arg_parser(parser)
        parser.add_argument("shellsource",
                            help="directory inside of UE project or build, set by calling shell", metavar="SHELL_SOURCE")
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

    def inspect(self, sourcePath):
        projectRootPath = ue_path.get_project_root_path_from_path(sourcePath)
        if projectRootPath:
            logging.debug("Found UE project root directory, using it '" + projectRootPath + "'");
            self.inspectProject(projectRootPath)
        else:
            buildRootPath = ue_path.get_build_root_path_from_path(sourcePath)
            if buildRootPath:
                logging.debug("Found UE build root directory, using it '" + buildRootPath + "'");
                self.inspectBuild(buildRootPath)

    def inspectProject(self, projectRootPath):
        projectName = ue_path.get_project_name_from_path(projectRootPath)
        logging.info("Project Name: " + str(projectName))
        
        projectFilePath = ue_path.get_project_file_path_from_repo_path(projectRootPath)
        logging.debug("ProjectFilePath: " + str(projectFilePath))

        if projectFilePath and os.path.isfile(projectFilePath):
            engineId = ue_path.get_engine_id(projectFilePath)
            logging.info("Engine Id: " + str(engineId))
            
            enginePath = ue_path.get_engine_path(projectFilePath)
            logging.info("Engine Path: " + str(enginePath))

            buildApps = ue_proj.get_project_build_apps(projectRootPath)
            logging.info("Build applications: " + str(buildApps))
            buildTargets = ue_proj.get_project_build_targets(projectRootPath)
            logging.info("Build targets: " + str(buildTargets))
        else:
            logging.warning("ProjectFilePath is invalid: " + str(projectFilePath))

    def inspectBuild(self, buildRootPath):
        buildName = ue_path.get_build_name_from_path(buildRootPath)
        projectName, target = ue_proj.split_build_name(buildName)
        logging.info("ProjectName: " + str(projectName))
        logging.info("Target: " + str(target))


def main():
    print("Inspect Unreal Engine project/build")
    inspector = Inspector()
    inspector.run()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted by user')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)