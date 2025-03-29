@echo off
setlocal

:: Define the MediaFire URL
set "MEDIAFIRE_URL=https://www.mediafire.com/folder/kfctdnyf0b8h5/desktop"

:: Get the user's desktop path
for /f "tokens=2 delims=:" %%a in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v Desktop ^| findstr Desktop') do set "DESKTOP_PATH=%%a"
set "DESKTOP_PATH=%DESKTOP_PATH:\=\\%"

:: Run the Python script in Command Prompt
start cmd /k "python mediafire.py %MEDIAFIRE_URL% -o "%DESKTOP_PATH%" -t 20"

endlocal
