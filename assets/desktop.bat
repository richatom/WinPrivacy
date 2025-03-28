@echo off
setlocal

set "MEDIAFIRE_URL=https://www.mediafire.com/folder/p5v9r9a1gxa9y/desktop"

for /f "tokens=2 delims=:" %%a in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v Desktop ^| findstr Desktop') do set "DESKTOP_PATH=%%a"
set "DESKTOP_PATH=%DESKTOP_PATH:\=\\%"

:: Run the Python script in Command Prompt
start cmd /k "python mediafire.py %MEDIAFIRE_URL% -o "%DESKTOP_PATH%" -t 20"

endlocal
