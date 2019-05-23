import os
import sys
import logging
import platform
import win32api, win32con
from ue.platform_base import UePlatformBase
from ue import path as ue_path

INSTALLATION_SUB_KEY = "SOFTWARE\\Epic Games\\Unreal Engine\\Builds"
EXE_EXTENSION = ".exe"

class UePlatformWindows(UePlatformBase):
    def get_application_settings_path(self):
        return os.path.normpath("C:/ProgramData/Epic")
    
    def get_launcher_settings_path(self):
        return os.path.join(self.get_application_settings_path(), "UnrealEngineLauncher")

    def get_launcher_installations_file_path(self):
        return os.path.join(self.get_launcher_settings_path(), "LauncherInstalled.dat")

    def enumerate_engine_installations(self):
        engineInstallations = self.get_launcher_engine_installations()

        userKeyPath = win32con.HKEY_CURRENT_USER
        regKeyHandle = None
        try:
            regKeyHandle = win32api.RegOpenKeyEx(userKeyPath, INSTALLATION_SUB_KEY, 0, win32con.KEY_READ)
            uniqueDirectories = [item[1] for item in engineInstallations]

            i = 0
            while True:
                try:
                    name, value, type = win32api.RegEnumValue(regKeyHandle, i)
                    logging.debug(str(name))
                    if name and value:
                        installLocation = os.path.normpath(value)
                        if ue_path.is_valid_engine_root_directory(installLocation):
                            if installLocation in uniqueDirectories:
                                logging.warning(installLocation + " is duplicated, name " + (name))
                            else:
                                uniqueDirectories.append(installLocation)
                                engineInstallations[name] = installLocation
                        else:
                            logging.warning(installLocation + " is not a valid engine root directory")
                except Exception as e:
                    logging.debug(str(e))
                    break
                i = i + 1

        except Exception as e:
            logging.warning("Can't open registry key: " + str(userKeyPath) + "/" + str(INSTALLATION_SUB_KEY) + " because of " + str(e))
        finally:
            if regKeyHandle is not None:
                win32api.RegCloseKey(regKeyHandle)
                #regKeyHandle.Close()

        logging.debug("EngineInstallations: " + str(engineInstallations))

        return engineInstallations

    def is_build_exe_file(self, filePath):
        return filePath.endswith(EXE_EXTENSION)