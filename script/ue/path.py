import os
import sys
import logging
import platform
import json
from ue import platform as ue_pfm
from ue import project

SOURCE_PATH = "Source"
LOGS_PATH = "Saved/Logs"
TARGET_FILE_ENDING = ".Target.cs"

ENGINE_DIR = "Engine"
ENGINE_SOURCE_DIR = os.path.join(ENGINE_DIR, "Source")
ENGINE_SOURCE_RUNTIME_DIR = os.path.join(ENGINE_DIR, "Source")
VERSION_FILE_PATH = "Engine/Source/Runtime/Launch/Resources/Version.h"

def get_engine_root_dir_from_identifier(identifier):
    platformInterface = ue_pfm.get_current_platform_interface()
    if not platformInterface:
        logging.error("Platform interface is None")
        return None

    logging.debug("identifier: " + str(identifier))
    engineInstallations = platformInterface.get_all_engine_installations()
    return engineInstallations.get(identifier)

def get_engine_identifier_from_root_dir(inRootDir):
    platformInterface = ue_pfm.get_current_platform_interface()
    if not platformInterface:
        logging.error("Platform interface is None")
        return None

    logging.debug("inRootDir: " + str(identifier))
    engineInstallations = platformInterface.get_all_engine_installations()
    for identifier, rootDir in engineInstallations.items():
        if inRootDir == rootDir:
            return identifier

def is_valid_engine_root_directory(engineRoot):
    binariesDir = os.path.normpath(os.path.join(engineRoot, 'Engine/Binaries'))
    hasBinariesDir = os.path.isdir(binariesDir)
    if not hasBinariesDir:
        logging.debug(engineRoot + " is not a valid engine root directory because " + binariesDir + " is absent")
    
    buildDir = os.path.normpath(os.path.join(engineRoot, "Engine/Build"))
    hasBuildDir = os.path.isdir(buildDir)
    if not buildDir:
        logging.debug(engineRoot + " is not a valid engine root directory because " + buildDir + " is absent")

    return hasBinariesDir and hasBuildDir

def get_project_name_from_project_file_path(filePath):
    if filePath.endswith(project.UPROJECT_EXTENSION):
        return os.path.splitext(os.path.basename(filePath))[0]

def get_engine_version_from_root_dir(engineRoot):
    fullVersionFilePath = os.path.join(engineRoot, VERSION_FILE_PATH)
    versionMajor = None
    versionMinor = None
    versionPatch = None
    if os.path.isfile(fullVersionFilePath):
        with open(fullVersionFilePath) as f:
            datafile = f.readlines()
            for line in datafile:
                # Just hack instead of c++ preprocessor
                if versionMajor is None and '#define' in line and 'ENGINE_MAJOR_VERSION' in line:
                    versionMajor = [s for s in line.split() if s.isdigit()][-1]
                if versionMinor is None and '#define' in line and 'ENGINE_MINOR_VERSION' in line:
                    versionMinor = [s for s in line.split() if s.isdigit()][-1]
                if versionPatch is None and '#define' in line and 'ENGINE_PATCH_VERSION' in line:
                    versionPatch = [s for s in line.split() if s.isdigit()][-1]
    return versionMajor, versionMinor, versionPatch

def is_valid_uproject_file(filePath):
    #logging.debug("is_valid_uproject_file " + filePath + " " + str(get_project_name_from_project_file_path(filePath)))
    return get_project_name_from_project_file_path(filePath) is not None

def get_project_name_from_path(somePath):
    if os.path.isfile(somePath):
        return get_project_name_from_project_file_path(somePath)
    elif os.path.isdir(somePath):
        projectFileName = get_project_file_name_from_repo_path(somePath)
        if projectFileName:
            return os.path.splitext(projectFileName)[0]

def is_valid_project_root_directory(somePath):
    #logging.debug("is_valid_project_root_directory " + somePath)
    uprojectFileName = get_project_file_name_from_repo_path(somePath)
    return (uprojectFileName != None)

def get_project_file_name_from_repo_path(projectPath):
    for fileName in get_files(projectPath):
        if is_valid_uproject_file(fileName):
            return fileName

def get_project_file_path_from_repo_path(projectPath):
    fileName = get_project_file_name_from_repo_path(projectPath)
    if fileName:
        return os.path.join(projectPath, fileName)

def get_project_root_path_from_path(somePath):
    currentPath = os.path.abspath(somePath)
    while True:
        #logging.debug("get_project_root_path_from_path " + currentPath)
        if is_valid_project_root_directory(currentPath):
            return currentPath
        prevPath = currentPath
        currentPath = os.path.abspath(os.path.join(currentPath, os.pardir))
        if prevPath == currentPath:
            break

def is_build_exe_file(filePath, platform=None):
    if not filePath:
        return False

    if platform:
        platformInterfaces = [platform]
    else:
        platformInterfaces = list(ue_pfm.get_all_platform_interfaces().values())
        if not platformInterfaces:
            logging.error("No platform interfaces")
            return False

    return any(pi.is_build_exe_file(filePath) for pi in platformInterfaces)

def get_build_name_from_path(somePath, platform=None):
    engineBinariesDir = os.path.normpath(os.path.join(somePath, 'Engine/Binaries'))
    childDirs = get_child_dirs(somePath)
    if os.path.isdir(engineBinariesDir):
        for fileName in [fn for fn in get_files(somePath) if is_build_exe_file(fn, platform)]:
            fileNameNoExt = os.path.splitext(os.path.basename(fileName))[0]
            projectName = project.split_build_name(fileNameNoExt)[0]
            if projectName in childDirs:
                if all((dir in get_child_dirs(os.path.join(somePath, projectName))) for dir in ['Binaries', 'Content']):
                    return fileNameNoExt

def is_valid_build_root_directory(somePath, platform=None):
    return get_build_name_from_path(somePath, platform)

def get_build_root_path_from_path(somePath, platform=None):
    currentPath = os.path.abspath(somePath)
    while True:
        if is_valid_build_root_directory(currentPath, platform):
            return currentPath
        prevPath = currentPath
        currentPath = os.path.abspath(os.path.join(currentPath, os.pardir))
        if prevPath == currentPath:
            break

def get_engine_id(projectFile):
    #EngineAssociation": "4.20"
    with open(projectFile) as projectCfg:
        data = json.load(projectCfg)
        if 'EngineAssociation' in data:
            return data['EngineAssociation']

def get_engine_root_path(projectFile):
    #return "e:/projects/Unreal/4_20"
    #return "e:/prog/Epic/UE_4.20"
    engineId = get_engine_id(projectFile)
    if engineId:
        return get_engine_root_dir_from_identifier(engineId)

def get_engine_engine_path(projectFile):
    #return "e:/projects/Unreal/4_20/Engine"
    #return "e:/prog/Epic/UE_4.20/Engine"
    engineRootPath = get_engine_root_path(projectFile)
    if os.path.isdir(engineRootPath):
        return os.path.join(engineRootPath, ENGINE_DIR)
def get_project_target_files(projectPath):
    sourcePath = os.path.abspath(os.path.join(projectPath, SOURCE_PATH))
    if os.path.isdir(sourcePath):
        return [fn for fn in get_files(sourcePath) if fn.endswith(TARGET_FILE_ENDING)]

def get_child_dirs(somePath):
    return [dir for dir in os.listdir(somePath) if os.path.isdir(os.path.join(somePath, dir))]

def get_files(somePath):
    return [fileName for fileName in os.listdir(somePath) if os.path.isfile(os.path.join(somePath, fileName))]

def get_relative_build_file_path():
    platformInterface = ue_pfm.get_current_platform_interface()
    if not platformInterface:
        logging.error("Platform interface is None")
        return None

    return platformInterface.get_relative_build_file_path()