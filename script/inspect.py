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
from ue import context as ue_context


class Inspector:
    def run(self):
        sourcePath, settings = self.init()
        if sourcePath:
            self.inspect(sourcePath, settings)

    def init(self):
        sourcePath, settings = self.process_args()
        logging.debug("Input SourcePath: " + str(sourcePath))
        if os.path.isdir(sourcePath):
            return sourcePath, settings
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

        return parsedArgs.source, parsedArgs

    def inspect(self, sourcePath, settings):
        context = ue_context.get_context_interface(sourcePath)
        if context:
            context.inspect(settings)
        else:
            logging.warning("No context found for the path " + str(sourcePath))

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