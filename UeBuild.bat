@echo off

rem Build Unreal Engine project script
python %~dp0\script\build.py %cd% %*
