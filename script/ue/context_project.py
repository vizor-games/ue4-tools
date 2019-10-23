import os
import logging
from ue import path as ue_path
from ue import project as ue_proj
from ue.context_base import UeContextBase
from ue.context_engine import UeContextEngine

class UeContextProject(UeContextBase):
    def is_root_dir(somePath):
        return ue_path.is_valid_project_root_directory(somePath)

    def get_root_path(somePath):
        return UeContextProject._get_root_path(somePath, UeContextProject.is_root_dir)

    def construct(somePath):
        rootPath = UeContextProject.get_root_path(somePath)
        if rootPath is not None:
            return UeContextProject(rootPath)

    def getName(self):
        return "project"

    def inspect(self, settings):
        projectName = ue_path.get_project_name_from_path(self.rootPath)
        logging.info("Project Name: " + str(projectName))
        
        projectFilePath = ue_path.get_project_file_path_from_repo_path(self.rootPath)
        logging.debug("ProjectFilePath: " + str(projectFilePath))

        if projectFilePath and os.path.isfile(projectFilePath):
            engineId = ue_path.get_engine_id(projectFilePath)
            logging.info("Engine Id: " + str(engineId))
            
            enginePath = ue_path.get_engine_root_path(projectFilePath)
            logging.info("Engine Path: " + str(enginePath))

            if enginePath:
                contextEngine = UeContextEngine.construct(enginePath)
                contextEngine.inspect(settings)

            buildTargets = ue_proj.get_build_targets(self.rootPath)
            logging.info("Build targets: " + str(buildTargets))

            if settings.plugins or settings.projectPlugins or settings.allPlugins:

                plugins = ue_proj.get_project_plugins(self.rootPath)

                enabledPluginNames = [pluginName for pluginName in plugins if plugins[pluginName]['Enabled'] == True]
                if enabledPluginNames:
                    logging.info("Enabled plugins:")
                    for pluginName in enabledPluginNames:
                        pluginInfo = plugins[pluginName]
                        dbgStr = "   " + pluginName
                        if pluginInfo['Source'] == 'Engine':
                            dbgStr += " (Engine)"
                        logging.info(dbgStr)

                disabledPluginNames = [pluginName for pluginName in plugins if plugins[pluginName]['Enabled'] == False]
                if disabledPluginNames and (settings.projectPlugins or settings.allPlugins):
                    logging.info("Available plugins:")
                    for pluginName in disabledPluginNames:
                        pluginInfo = plugins[pluginName]
                        if settings.allPlugins or pluginInfo.get('InProjectFile'):
                            dbgStr = "   " + pluginName
                            if pluginInfo['Source'] == 'Engine':
                                dbgStr += " (Engine)"
                            logging.info(dbgStr)
        else:
            logging.warning("ProjectFilePath is invalid: " + str(projectFilePath))

    def build(self, settings):
        raise NotImplementedError()

    def view_logs(self, settings):
        raise NotImplementedError()