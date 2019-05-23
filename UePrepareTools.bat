@echo off

rem echo %cd%
rem echo %~dp0

rem https://stackoverflow.com/a/41379378
rem append user path
set Key="HKCU\Environment"
for /F "usebackq tokens=2*" %%A IN (`REG QUERY %Key% /v PATH`) DO Set CurrPath=%%B
echo %CurrPath% > user_path_bak.txt
echo "!!!WARNING!!! your user PATH will be updated, backup saved to user_path_bak.txt"
setx path "%CurrPath%";%~dp0

python %~dp0\script\install_required_packages.py %*
