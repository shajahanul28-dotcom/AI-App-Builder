@echo off
title NOVAIX AI App Builder - Phone Access
cd /d "%~dp0"
echo Keep this window open. Connect the phone and laptop to the same Wi-Fi.
python -m app.server --host 0.0.0.0
if errorlevel 1 pause

