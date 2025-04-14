@echo off
nuitka --onefile --standalone --enable-plugin=pyqt5 --remove-output --windows-console-mode=disable --windows-uac-admin --output-dir=dist --follow-imports ^
--windows-icon-from-ico=media/ICON.ico ^
--include-data-files="media/ChakraPetch-Regular.ttf=ChakraPetch-Regular.ttf" ^
--include-data-files="configs/barebones.json=barebones.json" ^
--include-data-dir="scripts/Reg_tweaks=scripts/Reg_tweaks" ^
--include-data-dir="scripts/Misc_Tweaks=scripts/Misc_Tweaks" ^
--include-data-dir="assets=assets" ^
--include-data-dir="components=components" ^
--include-data-dir="assets/AtomUtilites=assets/AtomUtilites" ^
--include-data-dir="assets/uninstallers=assets/uninstallers" ^
--include-data-files="assets/desktopUtilites.ps1=assets/desktopUtilites.ps1" ^
--include-data-files="assets/waterfox.ps1=assets/waterfox.ps1" ^
--include-data-files="assets/powerplan.pow=assets/powerplan.pow" ^
init.py
pause
