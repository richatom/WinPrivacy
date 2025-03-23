@echo off
nuitka --onefile --standalone --enable-plugin=pyqt5 --remove-output --windows-console-mode=disable --windows-uac-admin --output-dir=dist --follow-imports ^
--windows-icon-from-ico=media/ICON.ico ^
--include-data-files="media/ChakraPetch-Regular.ttf=ChakraPetch-Regular.ttf" ^
--include-data-files="configs/barebones.json=barebones.json" ^
init.py
pause
