::Everything here is entirely decorative
@echo off
set version=PyBot V0.4
title -= %version% =-
color 02
mode con cols=68

::Runs the actual code
python main.py %version%
::if the code stops unexpectedly, something bad probably happened...
@echo Something went wrong here...
pause
