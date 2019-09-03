import os
import sys
import logging
import platform
from ue.context_project import UeContextProject
from ue.context_build import UeContextBuild
from ue.context_engine import UeContextEngine

def get_context_interface(somePath):
    context = UeContextProject.construct(somePath)
    if context is None:
        context = UeContextBuild.construct(somePath)
        if context is None:
            context = UeContextEngine.construct(somePath)
    
    if context:
        logging.debug("Found Unreal Engine " + context.getName() + " root directory, using it '" + context.rootPath + "'");

    return context
