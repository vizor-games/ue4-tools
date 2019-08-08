import os
import sys
import logging
import platform
import json
from ue import platform as pfm
from ue import path as ue_path

UPROJECT_EXTENSION = ".uproject"

ALL_TARGETS = ["Editor", "Game", "Client", "Server"]
TARGET_BIULD_SUFFUX = {
    "Editor": "Editor", 
    "Game": "", 
    "Client": "Client",
    "Server": "Server"
}

ALL_CONFIGURATIONS = ["Debug", "Development", "Test", "Shipping"]
ALL_PLATFORMS = ["Win64", "Linux", "Mac"]

# Return [project name, target name] if possible, else None
def split_build_name(buildName):
    for taget, suffix in TARGET_BIULD_SUFFUX.items():
        if buildName.lower().endswith(suffix.lower()):
            projectName = buildName
            if len(suffix):
                projectName = buildName[:-len(suffix)]
            return [projectName, taget]

def get_target_from_build_name(buildName, projectName):
    suffix = buildName[len(projectName):]
    try:
        reverceDict = {v: k for k, v in TARGET_BIULD_SUFFUX.items()}
        return reverceDict[suffix]
    except KeyError:
        logging.warning("Unknown suffix: " + str(suffix))
        return suffix

# Get build name for project name and target name
def create_build_name(projectName, targetName):
    if targetName.lower() == "game":
        return projectName
    else:
        return projectName + targetName.capitalize()

def project_has_build_target(projectPath, buildTargetName):
    buildTargets = get_project_build_targets(projectPath)
    return (buildTargetName in buildTargets)

def get_project_build_targets(projectPath):
    projectName = ue_path.get_project_name_from_path(projectPath)
    if projectName:
        targetFiles = ue_path.get_project_target_files(projectPath)
        logging.debug("Target files: " + str(targetFiles))
        return [get_target_from_build_name(tf[:-len(ue_path.TARGET_FILE_ENDING)], projectName) for tf in targetFiles]
