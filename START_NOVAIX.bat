@echo off
title NOVAIX AI App Builder
cd /d "%~dp0"
python -m app.server --host 127.0.0.1
if errorlevel 1 (
  echo.
  echo NOVAIX could not start. Run INSTALL_WINDOWS.ps1 first.
  pause
)

