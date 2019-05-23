import os
import sys
import logging
import platform
import json
from ue import platform as pfm
from ue import path as ue_path

UPROJECT_EXTENSION = ".uproject"

ALL_APPLICATIONS = ["Editor", "Game", "Client", "Server"]
APP_BIULD_SUFFUX = {
    "Editor": "Editor", 
    "Game": "", 
    "Client": "Client",
    "Server": "Server"
}

ALL_CONFIGURATIONS = ["Debug", "Development", "Test", "Shipping"]
ALL_PLATFORMS = ["Win64", "Linux", "Mac"]

# Return [project name, application name] if possible, else None
def split_build_name(buildName):
    for app, suffix in APP_BIULD_SUFFUX.items():
        if buildName.lower().endswith(suffix.lower()):
            projectName = buildName
            if len(suffix):
                projectName = buildName[:-len(suffix)]
            return [projectName, app]

def get_app_from_build_name(buildName, projectName):
    suffix = buildName[len(projectName):]
    try:
        reverceDict = {v: k for k, v in APP_BIULD_SUFFUX.items()}
        return reverceDict[suffix]
    except KeyError:
        logging.warning("Unknown suffix: " + str(suffix))
        return suffix

# Get build name for project name and application name
def create_build_name(projectName, appName):
    if appName.lower() == "game":
        return projectName
    else:
        return projectName + appName.capitalize()

def get_project_build_apps(projectPath):
    projectName = ue_path.get_project_name_from_path(projectPath)
    if projectName:
        targetFiles = ue_path.get_project_target_files(projectPath)
        logging.debug("Target files: " + str(targetFiles))
        return [get_app_from_build_name(tf[:-len(ue_path.TARGET_FILE_ENDING)], projectName) for tf in targetFiles]
