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
    try:
        # Define the URL and the local path for the powerplan file
        powerplan_url = 'https://raw.githubusercontent.com/richatom/WinPrivacy/refs/heads/main/assets/powerplan.pow'
        temp_dir = tempfile.gettempdir()
        powerplan_path = os.path.join(temp_dir, 'powerplan.pow')
        
        # Download the powerplan file
        log(f"Downloading powerplan file from: {powerplan_url}")
        response = requests.get(powerplan_url)
        response.raise_for_status()
        
        with open(powerplan_path, 'wb') as file:
            file.write(response.content)
        
        log(f"Powerplan file downloaded to: {powerplan_path}")
        
        # Apply the powerplan
        log("Applying the powerplan...")
        result = subprocess.run(
            ["powercfg", "-import", powerplan_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            log("Powerplan applied successfully")
            waterfoxdownload()
        else:
            log(f"Failed to apply powerplan with return code: {result.returncode}")
            log(f"Process error: {result.stderr}")
    
    except requests.RequestException as e:
        log(f"Error downloading powerplan file: {str(e)}")
    except subprocess.CalledProcessError as e:
        log(f"Error applying powerplan: {str(e)}")
    except Exception as e:
        log(f"Unexpected error in run_powerplan: {str(e)}")


def waterfoxdownload():
    try:
        log("Installing Waterfox...")
        
        # Defien waterfox installation script
        ps1_command = ['''
Write-Output "Starting Waterfox installation via winget..."

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Output "Winget is not available. Attempting to install..."

    $ProgressPreference = 'SilentlyContinue'
    Write-Output "Installing WinGet PowerShell module from PSGallery..."

    Install-PackageProvider -Name NuGet -Force | Out-Null
    Install-Module -Name Microsoft.WinGet.Client -Force -Repository PSGallery -AllowClobber | Out-Null

    Write-Output "Using Repair-WinGetPackageManager cmdlet to bootstrap WinGet..."
    Repair-WinGetPackageManager
    Write-Output "WinGet installation complete."
}

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Error "Winget installation failed or is still unavailable."
    exit 1
}

Write-Output "Installing Waterfox via winget..."
winget install --id Waterfox.Waterfox --source winget --accept-package-agreements --accept-source-agreements

Write-Output "Waterfox installation completed."
'''
        ]
        
        # Execute waterfox installation script
        for cmd in ps1_command:
            try:
                result = subprocess.run(["powershell.exe", "-Command", cmd], 
                                      check=True, 
                                      capture_output=True, 
                                      text=True)
                log(f"Successfully executed waterfox installation: {cmd}")
            except subprocess.CalledProcessError as e:
                log(f"Error executing waterfox installation: {cmd}: {str(e)}")
            except Exception as e:
                log(f"Unexpected error with waterfox installation: {cmd}: {str(e)}")
        
        log("Waterfox installation completed")
        desktopFolder()
        
    except Exception as e:
        log(f"Error in waterfox installation: {str(e)}")
        desktopFolder()  # Continue with desktop folder even if waterfox installation fails

def desktopFolder():
    script_url='https://raw.githubusercontent.com/richatom/WinPrivacy/refs/heads/main/assets/desktopUtilites.ps1'
    temp_dir=tempfile.gettempdir()
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

        if result.returncode == 0:
            log('Script executed successfully')
            log('Doing the final changes')
            log(f"Process stdout: {result.stdout}")
            log(f'finalizing installation')
            custom_scripts_tweaks()
        else:
            log("Finalizing installation...")
            log(f"Process stderr: {result.stderr}")
            log(f"Desktop Utilities script execution failed with return code: {result.returncode}")
            log(f"Process stdout: {result.stdout}")
    except Exception as e:
        log(f"An error occurred: {str(e)}")

def custom_scripts_tweaks():
    log('Preparing to run miscellaneous scripts')
    log('Running registry modifications')
    registry_mods()

def registry_mods():
    try:
        log("Applying registry modifications...")
        
        # Define all registry modifications
        registry_changes = [
            # Show Quick Access
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer", "HubMode", winreg.REG_SZ, "-"),
            
            # Remove all folders in This PC
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace", None, None, None),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{088e3905-0323-4b02-9826-5d99428e115f}", None, None, None),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{24ad3ad4-a569-4530-98e1-ab02f9417aa8}", None, None, None),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{3dfdf296-dbec-4fb4-81d1-6a3438bcf4de}", None, None, None),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{d3162b92-9365-467a-956b-92703aca08af}", None, None, None),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{f86fa3ab-70d2-4fc7-9c99-fcbf05467f3a}", None, None, None),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{A0953C92-50DC-43bf-BE83-3742FED03C9C}", None, None, None),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}", None, None, None),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{A8CDFF1C-4878-43be-B5FD-F8091C1C60D0}", None, None, None),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{374DE290-123F-4565-9164-39C4925E467B}", None, None, None),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{1CF1260C-4DD0-4ebb-811F-33C572699FDE}", None, None, None),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{3ADD1653-EB32-4cb0-BBD7-DFA0ABB5ACCA}", None, None, None),
            
            # Remove Terminals Context Menu
            (winreg.HKEY_CLASSES_ROOT, r"Directory\Background\shell\OpenInTerminal", None, None, None),
            (winreg.HKEY_CLASSES_ROOT, r"Directory\Background\shell\OpenInTerminalAdmin", None, None, None),
            
            # Show Lock Screen
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\Personalization", "NoLockScreen", winreg.REG_DWORD, 0),
            
            # Remove Run With Priority In Context Menu
            (winreg.HKEY_CLASSES_ROOT, r"*\shell\runas", None, None, None),
            
            # Remove Security Tray from Startup
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run", "SecurityHealth", winreg.REG_BINARY, bytes([0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])),
            
            # Remove Take Ownership to Context Menu
            (winreg.HKEY_CLASSES_ROOT, r"*\shell\runas", None, None, None),
            (winreg.HKEY_CLASSES_ROOT, r"Directory\shell\runas", None, None, None),
            
            # Modern Volume Flyout
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarMn", winreg.REG_DWORD, 0),
            
            # Old Context Menu
            (winreg.HKEY_CURRENT_USER, r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32", None, None, None),
            
            # Remove Extract
            (winreg.HKEY_CLASSES_ROOT, r"*\shell\extract", None, None, None),
            (winreg.HKEY_CLASSES_ROOT, r"Directory\shell\extract", None, None, None),
            
            # Remove Idle Toggle in Desktop Context Menu
            (winreg.HKEY_CLASSES_ROOT, r"DesktopBackground\Shell\IdleToggle", None, None, None),
            
            # Hide App and Browser Control
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer", "HideSCAHealth", winreg.REG_DWORD, 1),
            
            # Modern AltTab
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer", "AltTabSettings", winreg.REG_DWORD, 1),
            
            # Modern Battery Flyout
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarMn", winreg.REG_DWORD, 0),
            
            # Modern Date and Time Flyout
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarMn", winreg.REG_DWORD, 0),
            
            # Enable Automatic Folder Discovery
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "DisableThumbnailCache", winreg.REG_DWORD, 0),
            
            # Enable System Restore
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore", "DisableSR", winreg.REG_DWORD, 0),
            
            # Disable Windows Spotlight
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "RotatingLockScreenEnabled", winreg.REG_DWORD, 0),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "RotatingLockScreenOverlayEnabled", winreg.REG_DWORD, 0),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SubscribedContent-338387Enabled", winreg.REG_DWORD, 0),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SubscribedContent-338388Enabled", winreg.REG_DWORD, 0),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SubscribedContent-338389Enabled", winreg.REG_DWORD, 0),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SubscribedContent-338393Enabled", winreg.REG_DWORD, 0),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SubscribedContent-353694Enabled", winreg.REG_DWORD, 0),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SubscribedContent-353696Enabled", winreg.REG_DWORD, 0),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SubscribedContentEnabled", winreg.REG_DWORD, 0),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SystemPaneSuggestionsEnabled", winreg.REG_DWORD, 0),
            
            # Disallow Edge Swipe
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ImmersiveShell", "EdgeUIConfig", winreg.REG_DWORD, 0),
            
            # Enable App Icons on Thumbnails
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer", "TaskbarSmallIcons", winreg.REG_DWORD, 0),
            
            # Disable Shortcut Text
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer", "link", winreg.REG_BINARY, bytes([0x00, 0x00, 0x00, 0x00])),
            
            # Disable Store App Archiving
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Appx\AppxAllUserStore\Settings", "AllowArchiving", winreg.REG_DWORD, 0),
            
            # Disable Update Notifications
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update", "AUOptions", winreg.REG_DWORD, 1),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update", "NoAutoUpdate", winreg.REG_DWORD, 1),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update", "NoAutoRebootWithLoggedOnUsers", winreg.REG_DWORD, 1),
            
            # Disable Verbose Messages
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", "VerboseStatus", winreg.REG_DWORD, 0),
            
            # Disable FTH
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "FeatureSettingsOverride", winreg.REG_DWORD, 0),
            
            # Disable Give Access To Menu
            (winreg.HKEY_CLASSES_ROOT, r"*\shell\Sharing", None, None, None),
            (winreg.HKEY_CLASSES_ROOT, r"Directory\shell\Sharing", None, None, None),
            
            # Disable Network Navigation Pane
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "NavPaneShowAllFolders", winreg.REG_DWORD, 0),
            
            # Disable Removable Drives in Sidebar
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoDrives", winreg.REG_DWORD, 0x3FFFFFFF),
            
            # Default Windows
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "Start_ShowClassicMode", winreg.REG_DWORD, 0),
            
            # Disable Automatic Updates
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update", "AUOptions", winreg.REG_DWORD, 1),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update", "NoAutoUpdate", winreg.REG_DWORD, 1),
            
            # Disable Delivery Optimization
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\DeliveryOptimization\Config", "DODownloadMode", winreg.REG_DWORD, 0)
        ]
        
        # Apply all registry changes
        for root_key, key_path, value_name, value_type, value in registry_changes:
            try:
                if value_name is None:  # Delete key
                    try:
                        winreg.DeleteKey(root_key, key_path)
                        log(f"Deleted registry key: {key_path}")
                    except WindowsError as e:
                        if e.winerror != 2:  # Ignore "key not found" errors
                            log(f"Error deleting registry key {key_path}: {str(e)}")
                else:  # Set value
                    with winreg.CreateKeyEx(root_key, key_path, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.SetValueEx(key, value_name, 0, value_type, value)
                        log(f"Set registry value: {key_path}\\{value_name}")
                        
            except Exception as e:
                log(f"Error applying registry change {key_path}: {str(e)}")
        
        log("Registry modifications completed")
        cmd_tweaks()
        
    except Exception as e:
        log(f"Error in registry_mods: {str(e)}")
        cmd_tweaks()  # Continue with cmd_tweaks even if registry mods fail

def cmd_tweaks():
    try:
        log("Applying CMD tweaks...")
        
        # Define all CMD commands to execute
        cmd_commands = [
            # Debloat Send To Context Menu
            'reg delete "HKEY_CLASSES_ROOT\\*\\shellex\\ContextMenuHandlers\\SendTo" /f',
            'reg delete "HKEY_CLASSES_ROOT\\Directory\\shellex\\ContextMenuHandlers\\SendTo" /f',
            
            # Disable FSO and Game Bar Support
            'reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR" /v "AppCaptureEnabled" /t REG_DWORD /d 0 /f',
            'reg add "HKEY_CURRENT_USER\\System\\GameConfigStore" /v "GameDVR_Enabled" /t REG_DWORD /d 0 /f',
            'reg add "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\PolicyManager\\default\\ApplicationManagement\\AllowGameDVR" /v "Value" /t REG_DWORD /d 0 /f',
            
            # Disable Hibernation
            'powercfg /h off',
            
            # Disable Location
            'reg add "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\location" /v "Value" /t REG_SZ /d "Deny" /f',
            'reg add "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Sensor\\Overrides\\{BFA794E4-F964-4FDB-90F6-51056BFE4B44}" /v "SensorPermissionState" /t REG_DWORD /d 0 /f',
            
            # Disable Microsoft Copilot
            'reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v "ShowCopilotButton" /t REG_DWORD /d 0 /f',
            
            # Disable Mobile Device Settings
            'reg add "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\bluetooth" /v "Value" /t REG_SZ /d "Deny" /f',
            'reg add "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\bluetoothSync" /v "Value" /t REG_SZ /d "Deny" /f',
            
            # Disable Powersaving
            'powercfg /change monitor-timeout-ac 0',
            'powercfg /change monitor-timeout-dc 0',
            'powercfg /change disk-timeout-ac 0',
            'powercfg /change disk-timeout-dc 0',
            'powercfg /change standby-timeout-ac 0',
            'powercfg /change standby-timeout-dc 0',
            'powercfg /change hibernate-timeout-ac 0',
            'powercfg /change hibernate-timeout-dc 0',
            
            # Disable Printing
            'net stop spooler',
            'sc config spooler start= disabled',
            'reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\Spooler" /v "Start" /t REG_DWORD /d 4 /f',
            
            # Disable Recent Items
            'reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v "Start_TrackDocs" /t REG_DWORD /d 0 /f',
            'reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v "Start_TrackProgs" /t REG_DWORD /d 0 /f',
            
            # Disable Search Indexing
            'net stop "Windows Search"',
            'sc config "Windows Search" start= disabled',
            
            # Disable Sleep Study
            'reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\238C9FA8-0AAD-41ED-83F4-97BE242C8F20\\7bc4a2f9-d8fc-4469-b07b-33eb785aaca0" /v "Attributes" /t REG_DWORD /d 2 /f',
            
            # Disable Web Search
            'reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Search" /v "BingSearchEnabled" /t REG_DWORD /d 0 /f',
            'reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Search" /v "CortanaConsent" /t REG_DWORD /d 0 /f',
            
            # Disable Widgets
            'reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v "TaskbarDa" /t REG_DWORD /d 0 /f',
            
            # Enable Sleep
            'powercfg /change monitor-timeout-ac 15',
            'powercfg /change monitor-timeout-dc 10',
            'powercfg /change disk-timeout-ac 0',
            'powercfg /change disk-timeout-dc 0',
            'powercfg /change standby-timeout-ac 30',
            'powercfg /change standby-timeout-dc 15',
            'powercfg /change hibernate-timeout-ac 0',
            'powercfg /change hibernate-timeout-dc 0',
            
            # Reset Network to WinPrivacy
            'netsh winsock reset',
            'netsh int ip reset',
            'ipconfig /flushdns',
            'ipconfig /release',
            'ipconfig /renew',
            
            # WinPrivacy Visual Effects
            'reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v "VisualFXSetting" /t REG_DWORD /d 2 /f',
            'reg add "HKEY_CURRENT_USER\\Control Panel\\Desktop" /v "UserPreferencesMask" /t REG_BINARY /d 9032078010000000 /f'
        ]
        
        # Execute all CMD commands
        for cmd in cmd_commands:
            try:
                result = subprocess.run(["cmd.exe", "/C", cmd], 
                                      check=True, 
                                      capture_output=True, 
                                      text=True)
                log(f"Successfully executed CMD command: {cmd}")
            except subprocess.CalledProcessError as e:
                log(f"Error executing CMD command {cmd}: {str(e)}")
            except Exception as e:
                log(f"Unexpected error with CMD command {cmd}: {str(e)}")
        
        log("CMD tweaks completed")
        ps1_tweaks()
        
    except Exception as e:
        log(f"Error in cmd_tweaks: {str(e)}")
        ps1_tweaks()  # Continue with ps1_tweaks even if cmd tweaks fail

def ps1_tweaks():
    try:
        log("Applying PowerShell tweaks...")
        
        # Define all PowerShell commands to execute
        ps1_commands = [
            # Disable Power Saving
            'Set-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\238C9FA8-0AAD-41ED-83F4-97BE242C8F20\\7bc4a2f9-d8fc-4469-b07b-33eb785aaca0" -Name "Attributes" -Value 2',
            'powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c',
            
            # Disable File Sharing
            'Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False',
            'Set-SmbServerConfiguration -EncryptData $true -Force',
            'Set-SmbClientConfiguration -EncryptData $true -Force',
            'Set-SmbServerConfiguration -EnableSMB1Protocol $false -Force',
            'Set-SmbServerConfiguration -EnableSMB2Protocol $true -Force',
            'Set-SmbServerConfiguration -EnableSMB3Protocol $true -Force'
        ]
        
        # Execute all PowerShell commands
        for cmd in ps1_commands:
            try:
                result = subprocess.run(["powershell.exe", "-Command", cmd], 
                                      check=True, 
                                      capture_output=True, 
                                      text=True)
                log(f"Successfully executed PowerShell command: {cmd}")
            except subprocess.CalledProcessError as e:
                log(f"Error executing PowerShell command {cmd}: {str(e)}")
            except Exception as e:
                log(f"Unexpected error with PowerShell command {cmd}: {str(e)}")
        
        log("PowerShell tweaks completed")
        finalize_installation()
        
    except Exception as e:
        log(f"Error in ps1_tweaks: {str(e)}")
        finalize_installation()  # Continue with finalization even if ps1 tweaks fail

def finalize_installation():
    log("Installation complete. Please restart your system")
""" Run the program """
if __name__ == "__main__":
    apply_registry_changes()
