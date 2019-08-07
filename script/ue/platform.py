import os
import sys
import logging
import platform

def get_platform_interface(uePlatform):
    if uePlatform  == 'Linux':
        from ue.platform_linux import UePlatformLinux
        return UePlatformLinux()
    elif uePlatform == 'Windows':
        from ue.platform_windows import UePlatformWindows
        return UePlatformWindows()

def get_current_platform_interface():
    return get_platform_interface(platform.system())

def get_all_platform_interfaces():
    return {
        'Linux': get_platform_interface('Linux'),
        'Windows': get_platform_interface('Windows'),
    }
