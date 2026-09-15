@echo off
title NOVAIX GitHub Upload
cd /d "%~dp0"
echo Uploading NOVAIX AI App Builder v1.2.0 to GitHub...
echo Sign in to GitHub if a browser or login window opens.
git push -u origin main
if errorlevel 1 (
  echo.
  echo Upload was not completed. Keep this window open and take a screenshot.
  pause
  exit /b 1
)
echo.
echo GitHub upload completed successfully.
pause
