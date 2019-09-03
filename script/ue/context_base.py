import os
import logging

class UeContextBase:
    def __init__(self, inRootPath):
        self.rootPath = inRootPath

    def getName(self):
        raise NotImplementedError()

    def inspect(self, settings):
        raise NotImplementedError()

    def build(self, settings):
        raise NotImplementedError()

    def view_logs(self, settings):
        raise NotImplementedError()

    def _get_root_path(somePath, rootDirChecker):
        currentPath = os.path.abspath(somePath)
        while True:
            if rootDirChecker(currentPath):
                return currentPath
            prevPath = currentPath
            currentPath = os.path.abspath(os.path.join(currentPath, os.pardir))
            if prevPath == currentPath:
                break