import os
import logging
import configparser
from ue.platform_base import UePlatformBase
from ue import path as ue_path

SH_EXTENSION = ".sh"
EPIC_CONFIG_PATH = ".config/Epic/"
UE_DIR_NAME = "UnrealEngine"
UE_CONFIG_NAME = "Install.ini"
INSTALLATIONS_SECTION = "Installations"

class UePlatformLinux(UePlatformBase):
    def is_build_exe_file(self, filePath):
        return filePath.endswith(SH_EXTENSION)

    def get_user_home_path(self):
        return os.path.normpath("C:/ProgramData/Epic")

    def enumerate_engine_installations(self):
        engineInstallations = {}
        uniqueDirectories = []

        userHomeDir = os.path.expanduser("~")
        logging.debug("User directory: " + str(userHomeDir))

        epicConfigDir = os.path.join(userHomeDir, EPIC_CONFIG_PATH)
        ueConfigPath = os.path.join(epicConfigDir, UE_DIR_NAME, UE_CONFIG_NAME)
        logging.debug("Config: " + str(ueConfigPath))

        config = configparser.ConfigParser()
        config.read(ueConfigPath)

        try:
            installationsSection = config[INSTALLATIONS_SECTION]
            for name in installationsSection:
                installLocation = os.path.normpath(installationsSection[name])
                if ue_path.is_valid_engine_root_directory(installLocation):
                    if installLocation in uniqueDirectories:
                        logging.warning(installLocation + " is duplicated, name " + (name))
                    else:
                        uniqueDirectories.append(installLocation)
                        engineInstallations[name] = installLocation
                else:
                    logging.warning(installLocation + " is not a valid engine root directory")
        except Exception as e:
            logging.warning("Exception while trying to parse config file '" + ueConfigPath + "': " + str(e))

        logging.debug("EngineInstallations: " + str(engineInstallations))

        return engineInstallations
