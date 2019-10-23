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
from ue import platform as pfm


class UnrealInfo:
    def run(self):
        self.init()
        self.info()

    def init(self):
        sourcePath = self.process_args()

    def process_args(self):
        parser = ArgumentParser()
        cm.init_arg_parser(parser)
        parsedArgs = parser.parse_args()
        self.onlyDebug = cm.process_parsed_args(parsedArgs)

        logging.debug("Parsing arguments: '" + ' '.join(sys.argv[1:]) + "'")
        logging.debug("Result is: " + str(parsedArgs))

    def info(self):
        platformInterface = pfm.get_current_platform_interface()
        if not platformInterface:
            logging.error("Platform interface is None")
            return

        launcherEngineInstallations = platformInterface.get_launcher_engine_installations()
        if not type(launcherEngineInstallations) is dict:
            logging.error("Wrong launcher engine installations data:", str(get_launcher_engine_installations))
            return

        if launcherEngineInstallations:
            logging.info("Launcher engine installations:")
            for identifier, rootDir in launcherEngineInstallations.items():
                logging.info("\tId: '" + str(identifier) + "'. Root dir: '" + str(rootDir) + "'")

        sourceEngineInstallations = platformInterface.get_source_engine_installations()
        if not type(sourceEngineInstallations) is dict:
            logging.error("Wrong source engine installations data:", str(get_source_engine_installations))
            return

        if sourceEngineInstallations:
            logging.info("Source engine installations:")
            for identifier, rootDir in sourceEngineInstallations.items():
                logging.info("\tId: '" + str(identifier) + "'. Root dir: '" + str(rootDir) + "'")

def main():
    print("Info about Unreal Engine installations in system")
    unrealInfo = UnrealInfo()
    unrealInfo.run()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted by user')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)