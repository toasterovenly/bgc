@echo off
if "%1"=="" goto errmsg

python bgc.py %1
clip < output\collection_%1.csv
goto end

:errmsg
@echo please supply a username argument

:end
