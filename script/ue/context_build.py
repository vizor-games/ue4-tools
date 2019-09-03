import os
import logging
from ue import path as ue_path
from ue.context_base import UeContextBase

class UeContextBuild(UeContextBase):
    def is_root_dir(somePath):
        return ue_path.is_valid_build_root_directory(somePath)

    def get_root_path(somePath):
        return UeContextBuild._get_root_path(somePath, UeContextBuild.is_root_dir)

    def construct(somePath):
        rootPath = UeContextBuild.get_root_path(somePath)
        if rootPath is not None:
            return UeContextBuild(rootPath)

    def getName(self):
        return "build"

    def inspect(self, settings):
        buildName = ue_path.get_build_name_from_path(buildRootPath)
        projectName, target = ue_proj.split_build_name(buildName)
        logging.info("ProjectName: " + str(projectName))
        logging.info("Target: " + str(target))

    def build(self, settings):
        raise NotImplementedError()

    def view_logs(self, settings):
        raise NotImplementedError()