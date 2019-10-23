import os
import sys
import logging
import platform
import json
import copy
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

def has_build_target(projectPath, buildTargetName):
    buildTargets = get_build_targets(projectPath)
    return (buildTargetName in buildTargets)

def get_build_targets(projectPath):
    projectName = ue_path.get_project_name_from_path(projectPath)
    if projectName:
        targetFiles = ue_path.get_project_target_files(projectPath)
        logging.debug("Target files: " + str(targetFiles))
        return [get_target_from_build_name(tf[:-len(ue_path.TARGET_FILE_ENDING)], projectName) for tf in targetFiles]

def has_plugin(projectPath, pluginName):
    plugins = get_project_plugins(projectPath, True)
    return (pluginName in plugins)

def is_plugin_enabled(projectPath, pluginName):
    plugins = get_project_plugins(projectPath, False)
    return (pluginName in plugins)

def get_project_plugins(projectPath):
    plugins = get_all_plugins(projectPath)
    return filter_plugins_by_project_file(projectPath, plugins)

def get_all_plugins(projectPath):
    projectPlugins = ue_path.read_plugins_from_directory(ue_path.get_plugins_directory(projectPath))
    enginePlugins = {}
    projectFilePath = ue_path.get_project_file_path_from_repo_path(projectPath)

    if projectFilePath and os.path.isfile(projectFilePath):
        enginePluginsPath = ue_path.get_engine_plugins_path(projectFilePath)
        enginePlugins = ue_path.read_plugins_from_directory(enginePluginsPath)
        logging.debug("enginePlugins:" + str(enginePlugins))

    plugins = {}
    
    for pluginName in projectPlugins:
        plugins[pluginName] = projectPlugins[pluginName]
        # Project plugins are enabled by default
        plugins[pluginName]['Enabled'] = True 
        plugins[pluginName]['Source'] = 'Project'

    for pluginName in enginePlugins:
        if pluginName in plugins:
             logging.warning("Duplicated plugin in project and in engine: " + str(pluginName))
        else:
            plugins[pluginName] = enginePlugins[pluginName]
            plugins[pluginName]['Source'] = 'Engine'

    return plugins

def filter_plugins_by_project_file(projectPath, plugins):
    localPlugins = copy.deepcopy(plugins)
    projectFilePath = ue_path.get_project_file_path_from_repo_path(projectPath)
    
    if projectFilePath and os.path.isfile(projectFilePath):
        data = None
        with open(projectFilePath) as projectCfg:
            data = json.load(projectCfg)

        if data is not None:
            if 'Plugins' in data:
                for plugingData in data['Plugins']:
                    if 'Name' in plugingData:
                        pluginName = plugingData['Name']
                        pluginInfo = localPlugins.get(pluginName)

                        if pluginInfo:
                            pluginInfo['InProjectFile'] = True

                            enabledInProjectFile = False
                            if 'Enabled' in plugingData:
                                if str(plugingData['Enabled']).lower() == 'true':
                                    enabledInProjectFile = True
                                elif str(plugingData['Enabled']).lower() != 'false':
                                    logging.warning("Wrong status for plugin " + pluginName + " in " + projectFilePath)

                            logging.debug("Plugin " + pluginName + " enabled in project file: " + str(enabledInProjectFile))
                            
                            if pluginInfo['Source'] != 'Project' and enabledInProjectFile:
                                pluginInfo['Enabled'] = True
                                logging.debug("Setting enabled plugin " + pluginName)
                            if pluginInfo['Source'] == 'Project' and not enabledInProjectFile:
                                pluginInfo['Enabled'] = False
                                logging.debug("Setting disabled plugin " + pluginName)
                        else:
                            logging.warning("Invalid plugin " + pluginName + " in " + projectFilePath)
    
    return localPlugins
