""" Import necessary modules for the program to work """
import sys
import os
import ctypes
import subprocess
import threading
import logging
import time
import platform
import winreg
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
# Talon components
from components.defender_check import DefenderCheck
from components import debloat_windows
from components import windows_check



""" Establish the version of Talon """
TALON_VERSION = "1.0.0"



""" Check for developer mode flag """
developer_mode = 1 if "--developer-mode" in sys.argv else 0



""" Set up the log file """
LOG_FILE = "talon.txt"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)



""" Utility function to obtain information about Windows """
def get_windows_info():
    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        key = winreg.OpenKey(reg, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
        build_number = int(winreg.QueryValueEx(key, "CurrentBuildNumber")[0])
        product_name = winreg.QueryValueEx(key, "ProductName")[0]
        display_version = winreg.QueryValueEx(key, "DisplayVersion")[0]
        if build_number >= 22000: # Windows 11 builds start from 22000
            os_version = "Windows 11"
        else:
            os_version = "Windows 10"
        return {
            'version': os_version,
            'build': build_number,
            'product_name': product_name,
            'display_version': display_version
        }
    except Exception as e:
        logging.error(f"Error getting Windows information: {e}")
        return None



""" Utility function to check if the program is being ran as administrator """
def is_running_as_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        logging.error(f"Error checking admin privileges: {e}")
        return False



""" If the program is not being ran as administrator, elevate """
def restart_as_admin():
    try:
        script = sys.argv[0]
        params = ' '.join(sys.argv[1:])
        logging.info("Restarting with admin privileges...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
        sys.exit()
    except Exception as e:
        logging.error(f"Error restarting as admin: {e}")



""" Main function to begin Talon installation """
def main():
    logging.info("Starting Talon Installer")
    if developer_mode:
        logging.warn(f"RUNNING IN DEVELOPER MODE!")
    logging.info(f"Talon Version: {TALON_VERSION}")
    windows_info = get_windows_info()
    if windows_info:
        logging.info(f"Windows Version: {windows_info['product_name']}")
        logging.info(f"Build Number: {windows_info['build']}")
        logging.info(f"Display Version: {windows_info['display_version']}")
    app = QApplication(sys.argv)
    if not is_running_as_admin():
        logging.warning("Program is not running as admin. Restarting with admin rights...")
        restart_as_admin()
    try:
        logging.info("Starting Defender check...")
        defender_check_window = DefenderCheck()
        defender_check_window.defender_disabled_signal.connect(defender_check_window.close)
        defender_check_window.show()
        while defender_check_window.isVisible():
            app.processEvents()
        logging.info("Defender is disabled, proceeding with the rest of the program.")
    except Exception as e:
        logging.error(f"Error during Defender check: {e}")
    selected_browser = None
    try:
        logging.info("Running Windows 11 and fresh install check...")
        windows_check.check_system()
        logging.info("System check passed.")
    except Exception as e:
        logging.error(f"System check failed: {e}")

    """ Run the installation process """
    def perform_installation():
        try:
            logging.info("Applying Windows registry modifications and customizations...")
            debloat_windows.apply_registry_changes()
            logging.info("Debloat and customization complete.")
        except Exception as e:
            logging.error(f"Error applying registry changes: {e}")
        logging.info("All installations and configurations completed.")
        logging.info("Installation complete. Please restart your system")
        debloat_windows.finalize_installation()

    try:
        logging.info("Starting installation process in a separate thread...")
        install_thread = threading.Thread(target=perform_installation)
        install_thread.start()
        while install_thread.is_alive():
            app.processEvents()
            time.sleep(0.05)            
    except Exception as e:
        logging.error(f"Error starting installation thread: {e}")
    app.exec_()



""" Start the program """
if __name__ == "__main__":
    main()
