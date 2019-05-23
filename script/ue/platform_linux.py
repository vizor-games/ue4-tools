import os
import logging
from ue.platform_base import UePlatformBase

SH_EXTENSION = ".sh"

class UePlatformLinux(UePlatformBase):
    def is_build_exe_file(self, filePath):
        return filePath.endswith(SH_EXTENSION)
