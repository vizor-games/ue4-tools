import os
import logging
from ue import path as ue_path
from ue.context_base import UeContextBase

class UeContextEngine(UeContextBase):
    def is_root_dir(somePath):
        return ue_path.is_valid_engine_root_directory(somePath)

    def get_root_path(somePath):
        return UeContextEngine._get_root_path(somePath, UeContextEngine.is_root_dir)

    def construct(somePath):
        rootPath = UeContextEngine.get_root_path(somePath)
        if rootPath is not None:
            return UeContextEngine(rootPath)

    def getName(self):
        return "engine"

    def inspect(self, settings):
        versionMajor, versionMinor, versionPatch = ue_path.get_engine_version_from_root_dir(self.rootPath)
        engineVersion = str(versionMajor) + '.' + str(versionMinor) + '.' + str(versionPatch)
        logging.info("Engine version: " + str(engineVersion))

    def build(self, settings):
        raise NotImplementedError()

    def view_logs(self, settings):
        raise NotImplementedError()