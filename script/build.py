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

DEFAULT_TARGET = "Editor"
DEFAULT_CONFIG = "Development"
DEFAULT_PLATFORM = "Win64"

DISABLE_UNITY_BUILD_ARG = "-DisableUnity"
NO_PCH_ARG = "-NoPCH"
NO_SHARED_PCH_ARG = "-NoSharedPCH"

def get_real_arg_values_list(argValue, allValue, dbgDescription):
    if type(argValue) is list:
        if len(argValue) == 1 and argValue[0].lower() == "all":
            valuesList = allValue
        else:
            valuesList = argValue
    elif type(argValue) == str:
        if argValue.lower() == "all":
            valuesList = allValue
        else:
            valuesList = [argValue]
    
    if valuesList is None:
        logging.error("Wrong type " + str(dbgDescription) + " arg type: " + str(type(argValue)) + " " + str(argValue))
    
    return valuesList


class ProjectBuilder:
    def run(self):
        initResult = self.init()
        if initResult:
            buildFilePath, projectFilePath, targetArg, configArg, platformArg = initResult
            self.run_build(buildFilePath, projectFilePath, targetArg, configArg, platformArg)

    def init(self):
        sourceArg, targetArg, configArg, platformArg = self.process_args()
        logging.debug("Input SourcePath: " + str(sourceArg))
        sourcePath = ue_path.get_project_root_path_from_path(sourceArg)
        logging.debug("Actual SourcePath: " + str(sourcePath))

        if os.path.isdir(sourcePath):
            projectFilePath = ue_path.get_project_file_path_from_repo_path(sourcePath)
            logging.debug("ProjectFilePath: " + str(projectFilePath))
            if projectFilePath and os.path.isfile(projectFilePath):
                enginePath = ue_path.get_engine_root_path(projectFilePath)
                logging.debug("EnginePath: " + str(enginePath))
                if enginePath and os.path.isdir(enginePath):
                    buildFilePath = os.path.normpath(os.path.join(enginePath, ue_path.get_relative_build_file_path()))
                    logging.debug("BuildFilePath: " + str(buildFilePath))
                    if buildFilePath and os.path.isfile(buildFilePath):
                        return buildFilePath, projectFilePath, targetArg, configArg, platformArg
                    else:
                        logging.warning("BuildFilePath is invalid: " + str(buildFilePath))
                else:
                    logging.warning("EnginePath is invalid: " + str(enginePath))
            else:
                logging.warning("ProjectFilePath is invalid: " + str(projectFilePath))
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
        parser.add_argument("-t", "--target", dest="target", nargs='+', default = DEFAULT_TARGET,
                            help="targets[s] to build. Use inspect script to find available targets. Use 'all' to build all available targets.", 
                            metavar="TARGET")
        parser.add_argument("-c", "--config", dest="config", nargs='+', default = DEFAULT_CONFIG,
                            help=("configuration type from " + str(ue_proj.ALL_CONFIGURATIONS)), metavar="CONFIG")
        parser.add_argument("-p", "--platform", dest="platform", nargs='+', default = DEFAULT_PLATFORM,
                            help=("platform type from " + str(ue_proj.ALL_PLATFORMS)), metavar="PLATFORM")
        parser.add_argument("-def", "--definitions", dest="definitions", nargs='+',
                            help="Definition for compiler.", 
                            metavar="DEFINITIONS")
        parser.add_argument("-nu", "--nonunity",
                            action="store_true", dest="nonUnity", default=False,
                            help="non-unity build")
        parser.add_argument("-npch", "--noprecompiledheaders",
                            action="store_true", dest="noPrecompiledHeaders", default=False,
                            help="not use precompiled headers")

        parsedArgs = parser.parse_args()
        self.onlyDebug = cm.process_parsed_args(parsedArgs)
        self.nonUnity = parsedArgs.nonUnity
        self.noPrecompiledHeaders = parsedArgs.noPrecompiledHeaders
        self.definitions = parsedArgs.definitions

        logging.debug("Parsing arguments: '" + ' '.join(sys.argv[1:]) + "'")
        logging.debug("Result is: " + str(parsedArgs))

        if not parsedArgs.source:
            parsedArgs.source = parsedArgs.shellsource

        return parsedArgs.source, parsedArgs.target, parsedArgs.config, parsedArgs.platform

    def get_target_arg(projectName, target):
        targetArg = ue_proj.create_build_name(projectName, target)
        logging.debug("Target arg: " + str(targetArg))
        return targetArg

    def run_build(self, buildFilePath, projectFilePath, targetArg, configArg, platformArg):
        logging.debug("Run build: " + str([buildFilePath, projectFilePath, targetArg, configArg, platformArg, self.onlyDebug]))
        projectName = ue_path.get_project_name_from_project_file_path(projectFilePath)
        projectPath = os.path.dirname(projectFilePath)

        targets = get_real_arg_values_list(targetArg, ue_proj.get_build_targets(projectPath), "target")
        if not targets:
            return

        configurations = get_real_arg_values_list(configArg, ue_proj.ALL_CONFIGURATIONS, "configuration")
        if not configurations:
            return

        platforms = get_real_arg_values_list(platformArg, ue_proj.ALL_PLATFORMS, "platform")
        if not platforms:
            return

        logging.info("\nBuild platforms: " + str(platforms))
        logging.info("Build configurations: " + str(configurations))
        logging.info("Build targets: " + str(targets) + "\n")

        for platform in platforms:
            logging.info("\n################################### Building " + platform + " platform ###################################\n")
            for config in configurations:
                for target in targets:
                    self.run_single_build(buildFilePath, projectFilePath, projectName, config, target, platform)

    def run_single_build(self, buildFilePath, projectFilePath, projectName, config, target, platform):
        logging.info("\n----------------------------------- Building " + platform + "_" + config + "_" + target.capitalize() + " -----------------------------------\n")
        buildTarget = ProjectBuilder.get_target_arg(projectName, target);

        command = [buildFilePath, buildTarget, platform, config, projectFilePath]

        if self.definitions:
            command.append("-define:" + str(' '.join(self.definitions)))

        if self.nonUnity:
            command.append(DISABLE_UNITY_BUILD_ARG)

        if self.noPrecompiledHeaders:
            command.append(NO_SHARED_PCH_ARG)
            command.append(NO_PCH_ARG)

        logging.info("Runnig command: " + str(command))
        if not self.onlyDebug:
            p = sp.Popen(command)
            stdout, stderr = p.communicate()

def main():
    print("Build Unreal Engine project")
    builder = ProjectBuilder()
    builder.run()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted by user')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)