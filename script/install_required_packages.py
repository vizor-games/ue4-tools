import os
import sys
import logging
import platform
import pip
import subprocess as sp


def installPackage(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        from pip._internal import main as pipmain
        pipmain(['install', 'package-name'])


def main():
    if platform.system() == 'Linux':
        pass
    elif platform.system() == 'Windows':
        installPackage('pypiwin32')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted by user')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)