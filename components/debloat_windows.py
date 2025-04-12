""" Import necessary modules for the program to work """
import sys
import ctypes
import os
import tempfile
import subprocess
import requests
import winreg
import shutil
import time
import logging
import json
import urllib
import urllib3
import urllib.request
import time

""" Set up the log file """
LOG_FILE = "talon.txt"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)



""" Utility function to log outputs """
def log(message):
    logging.info(message)
    print(message)


""" Utility function to check if the program is running as administrator """
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False



""" If the program is not running as administrator, attempt to elevate """
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit(0)



""" Apply modifications done via the Windows registry """
def apply_registry_changes():
    log("Applying registry changes...")
    try:
        registry_modifications = [
            # Visual changes
            (winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "TaskbarAl", winreg.REG_DWORD, 0), # Align taskbar to the left
            (winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize", "AppsUseLightTheme", winreg.REG_DWORD, 0), # Set Windows apps to dark theme
            (winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize", "SystemUsesLightTheme", winreg.REG_DWORD, 0), # Set Windows to dark theme
            (winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR", "AppCaptureEnabled", winreg.REG_DWORD, 0), #Fix the  Get an app for 'ms-gamingoverlay' popup
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\PolicyManager\\default\\ApplicationManagement\\AllowGameDVR", "Value", winreg.REG_DWORD, 0), # Disable Game DVR (Reduces FPS Drops)
            (winreg.HKEY_CURRENT_USER, r"Control Panel\\Desktop", "MenuShowDelay", winreg.REG_SZ, "0"),# Reduce menu delay for snappier UI
            (winreg.HKEY_CURRENT_USER, r"Control Panel\\Desktop\\WindowMetrics", "MinAnimate", winreg.REG_DWORD, 0),# Disable minimize/maximize animations
            (winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "ExtendedUIHoverTime", winreg.REG_DWORD, 1),# Reduce hover time for tooltips and UI elements
            (winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "HideFileExt", winreg.REG_DWORD, 0),# Show file extensions in Explorer (useful for security and organization)
        ]
        for root_key, key_path, value_name, value_type, value in registry_modifications:
            try:
                with winreg.CreateKeyEx(root_key, key_path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, value_name, 0, value_type, value)
                    log(f"Applied {value_name} to {key_path}")
            except Exception as e:
                log(f"Failed to modify {value_name} in {key_path}: {e}")
        log("Registry changes applied successfully.")
        subprocess.run(["taskkill", "/F", "/IM", "explorer.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["start", "explorer.exe"], shell=True)
        log("Explorer restarted to apply registry changes.")
        run_edge_vanisher()
        log("Edge Vanisher started successfully")
        
    except Exception as e:
        log(f"Error applying registry changes: {e}")



""" Run a script to remove Edge, and prevent reinstallation """
def run_edge_vanisher():
    log("Starting Edge Vanisher script execution...")
    try:
        script_url = "https://raw.githubusercontent.com/richatom/WinPrivacy/refs/heads/main/assets/uninstallers/edge_vanisher.ps1"
        temp_dir = tempfile.gettempdir()
        script_path = os.path.join(temp_dir, "edge_vanisher.ps1")
        log(f"Attempting to download Edge Vanisher script from: {script_url}")
        log(f"Target script path: {script_path}")
        
        response = requests.get(script_url)
        log(f"Download response status code: {response.status_code}")
        
        with open(script_path, "wb") as file:
            file.write(response.content)
        log("Edge Vanisher script successfully saved to disk")
        
        powershell_command = (
            f"Set-ExecutionPolicy Bypass -Scope Process -Force; "
            f"& '{script_path}'; exit" 
        )
        log(f"Executing PowerShell command: {powershell_command}")
        
        process = subprocess.run(
            ["powershell", "-Command", powershell_command],
            capture_output=True,
            text=True
        )
        
        if process.returncode == 0:
            log("Edge Vanisher execution completed successfully")
            log(f"Process output: {process.stdout}")
            run_oouninstall()
        else:
            log(f"Edge Vanisher execution failed with return code: {process.returncode}")
            log(f"Process error: {process.stderr}")
            
    except requests.exceptions.RequestException as e:
        log(f"Network error during Edge Vanisher script download: {str(e)}")
    except IOError as e:
        log(f"File I/O error while saving Edge Vanisher script: {str(e)}")
    except Exception as e:
        log(f"Unexpected error during Edge Vanisher execution: {str(e)}")



""" Run a script to remove OneDrive and Outlook """
def run_oouninstall():
    log("Starting Office Online uninstallation process...")
    try:
        script_url = "https://raw.githubusercontent.com/richatom/WinPrivacy/refs/heads/main/assets/uninstallers/uninstall_oo.ps1"
        temp_dir = tempfile.gettempdir()
        script_path = os.path.join(temp_dir, "uninstall_oo.ps1")
        log(f"Attempting to download OO uninstall script from: {script_url}")
        log(f"Target script path: {script_path}")
        
        response = requests.get(script_url)
        log(f"Download response status code: {response.status_code}")
        
        with open(script_path, "wb") as file:
            file.write(response.content)
        log("OO uninstall script successfully saved to disk")
        
        powershell_command = f"Set-ExecutionPolicy Bypass -Scope Process -Force; & '{script_path}'"
        log(f"Executing PowerShell command: {powershell_command}")
        
        process = subprocess.run(
            ["powershell", "-Command", powershell_command],
            capture_output=True,
            text=True
        )
        
        if process.returncode == 0:
            log("Office Online uninstallation completed successfully")
            log(f"Process stdout: {process.stdout}")
            run_tweaks()
        else:
            log(f"Office Online uninstallation failed with return code: {process.returncode}")
            log(f"Process stderr: {process.stderr}")
            log(f"Process stdout: {process.stdout}")
            
    except Exception as e:
        log(f"Unexpected error during OO uninstallation: {str(e)}")



""" Run ChrisTitusTech's WinUtil to debloat the system"""
def run_tweaks():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    if not is_admin():
        log("Must be run as an administrator.")
        sys.exit(1)

    try:
        if hasattr(sys, "_MEIPASS"):
            json_path = os.path.join(sys._MEIPASS, "barebones.json")
        else:
            json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "barebones.json"))

        log(f"Using config from: {json_path}")

        temp_dir = tempfile.gettempdir()
        log_file = os.path.join(temp_dir, "cttwinutil.log")

        command = [
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            f"$ErrorActionPreference = 'SilentlyContinue'; " +
            f"iex \"& {{ $(irm christitus.com/win) }} -Config '{json_path}' -Run\" *>&1 | " +
            "Tee-Object -FilePath '" + log_file + "'"
        ]
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        while True:
            output = process.stdout.readline()
            if output:
                output = output.strip()
                log(f"CTT Output: {output}")
                if "Tweaks are Finished" in output:
                    log("Detected completion message. Terminating...")

                    subprocess.run(
                        ["powershell", "-Command", "Stop-Process -Name powershell -Force"],
                        capture_output=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )

                    run_powerplan()
                    os._exit(0)
            
            if process.poll() is not None:
                run_powerplan()
                os._exit(1)

        return False

    except Exception as e:
        log(f"Error: {str(e)}")
        os._exit(1)

def run_powerplan():
    log('Starting powerplan setup')
    url = "https://raw.githubusercontent.com/richatom/WinPrivacy/refs/heads/main/assets/powerplan.pow"
    temp_dir = tempfile.gettempdir()
    local_path = os.path.join(temp_dir, "powerplan.pow")

    try:
        log(f"Downloading power plan from {url}...")
        urllib.request.urlretrieve(url, local_path)
        log(f"Downloaded to {local_path}")

        log("Importing power plan...")
        import_result = subprocess.run(["powercfg", "/import", local_path], capture_output=True, text=True, shell=True)
        if import_result.returncode != 0:
            log(f"Failed to import power plan: {import_result.stderr.strip()}")

        log("Fetching list of power plans...")
        list_result = subprocess.run(["powercfg", "/list"], capture_output=True, text=True, shell=True)
        if list_result.returncode != 0:
            log(f"Failed to list power plans: {list_result.stderr.strip()}")

        lines = list_result.stdout.splitlines()
        for line in lines:
            if "powerplan" in line.lower():  # Adjust this if needed
                guid = line.strip().split(":")[1].split("(")[0].strip()
                log(f"Setting active power plan: {guid}")
                subprocess.run(["powercfg", "/setactive", guid], shell=True)
                log("Power plan activated.")
                waterfoxdownload()
    except Exception as e:
        log(f"An error occurred: {str(e)}")

def waterfoxdownload():
    url = "https://raw.githubusercontent.com/richatom/WinPrivacy/refs/heads/main/assets/waterfox.ps1"
    temp_dir = tempfile.gettempdir()
    script_path = os.path.join(temp_dir, "waterfox.ps1")

    try:
        log(f"Downloading PowerShell script from: {url}")
        response = requests.get(url)
        response.raise_for_status()
        with open(script_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        log(f"Script saved to: {script_path}")

        log("Running PowerShell script...")
        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path],
            capture_output=True, text=True
        )

        # Output results
        log("Output:")
        log(result.stdout)
        log("Errors:")
        log(result.stderr)
        run_privacy_script()

    except Exception as e:
        log(f"An error occurred: {e}")

def run_privacy_script():
    script_url='https://raw.githubusercontent.com/richatom/WinPrivacy/refs/heads/main/assets/uninstallers/privacy-script.bat'
    tempdir=tempfile.gettempdir()
    script_path=os.path.join(tempdir, 'privacy-script.bat')
    try:
        response=requests.get(script_url)
        log(f'Getting privacy script from: {script_url}')
        response.raise_for_status()
        log(f'running privacy script')

        with open(script_path, "wb") as f:
            f.write(response.content)
        process=subprocess.Popen(['cmd.exe', '/C', script_path], 
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        )
        while True:
            output = process.stdout.readline()
            if output == output.strip():
                log(f'PS Output: {output}')
                if 'Tweaks are Finished' in output:
                    log(f'Privacy Script are finished: running desktop scripts')
                    desktopFolder()
            if process.poll() is not None:
                desktopFolder()
    except Exception as e:
        log(f'An error occurred: {e}')
    
def desktopFolder():
    script_url='https://raw.githubusercontent.com/richatom/WinPrivacy/refs/heads/main/assets/desktopUtilites.ps1'
    temp_dir=tempfile.gettempdir
    script_path=os.path.join(temp_dir, 'desktopUtilities.ps1')
    try:
        log(f'Attempting to get folders from: {script_url}')
        log(f'Target script path: {script_url}')
        response=requests.get(script_url)
        log(f'Download response status code: {response.status_code}')
        with open(script_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        log('Desktop utilities succesfully saved to disk')
        log(f'Excecuting desktop utilites: {script_path}')
        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path],
            capture_output=True, text=True)

        if process.returncode == 0:
            log('Script executed sucessfully') 
            log(f"Process stdout: {process.stdout}")
            log(f'Doing the final changes')
            log("Finalizing installation...")
        else:
            log(f"Desktop Utilites script execution failed with return code: {process.returncode}")
            log(f"Process stderr: {process.stderr}")
            log(f"Process stdout: {process.stdout}")
    except Exception as e:
        log(f"An error occurred: {str(e)}")

""" Finalize installation"""
def finalize_installation():
    log("Installation complete. Please restart your system")
""" Run the program """
if __name__ == "__main__":
    apply_registry_changes()
