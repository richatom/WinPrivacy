import os
import subprocess
import requests
from debloat_windows import *
from scripts.Reg_tweaks import *
from scripts.Misc_Tweaks import *
from init import *

def main():
    log('Preparing to run miscellaneous scripts')
    log('Running registry modifications')
    registry_mods()

def registry_mods():
    # Get the directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go one directory up and into scripts/Reg_tweaks
    registry_dir = os.path.join(os.path.dirname(current_dir), 'scripts', 'Reg_tweaks')
    
    # List of registry files to apply
    reg_files = [
        'Show_Quick_Access.reg',
        'Remove_all_folders_in_This_PC.reg',
        'Remove_Terminals_Context_Menu.reg',
        'Show_Lock_Screen.reg',
        'Remove_Run_With_Priority_In_Context_Menu.reg',
        'Remove_Security_Tray_from_Startup.reg',
        'Remove_Take_Ownership_to_Context_Menu.reg',
        'Modern_Volume_Flyout.reg',
        'Old_Context_Menu.reg',
        'Remove_Extract.reg',
        'Remove_Idle_Toggle_in_Desktop_Context_Menu.reg',
        'Hide_App_and_Browser_Control.reg',
        'Modern_AltTab.reg',
        'Modern_Battery_Flyout.reg',
        'Modern_Date_and_Time_Flyout.reg',
        'Enable_Automatic_Folder_Discovery.reg',
        'Enable_System_Restore.reg',
        'Disable_Windows_Spotlight.reg',
        'Disallow_Edge_Swipe.reg',
        'Enable_App_Icons_on_Thumbnails.reg',
        'Disable_Shortcut_Text.reg',
        'Disable_Store_App_Archiving.reg',
        'Disable_Update_Notifications.reg',
        'Disable_Verbose_Messages.reg',
        'Disable_FTH.reg',
        'Disable_Give_Access_To_Menu.reg',
        'Disable_Network_Navigation_Pane.reg',
        'Disable_Removable_Drives_in_Sidebar.reg',
        'Default_Windows.reg',
        'Disable_Automatic_Updates.reg',
        'Disable_Delivery_Optimization.reg'
    ]

    # Running regedit silently to import each reg file
    for reg_file in reg_files:
        if not reg_file:  # Skip empty entries
            continue
            
        reg_file_path = os.path.join(registry_dir, reg_file)
        try:
            if not os.path.exists(reg_file_path):
                log(f"Warning: Registry file {reg_file} not found in {registry_dir}")
                continue
                
            log(f"Applying registry file: {reg_file}")
            result = subprocess.run(["regedit.exe", "/s", reg_file_path], 
                                  check=True, 
                                  capture_output=True, 
                                  text=True)
            
            if result.returncode == 0:
                log(f"Successfully applied registry file: {reg_file}")
                log('Running command tweaks')
                cmd_tweaks()

            else:
                log(f"Failed to apply registry file {reg_file}. Error: {result.stderr}")
                
        except subprocess.CalledProcessError as e:
            log(f"Error applying registry file {reg_file}: {str(e)}")
        except Exception as e:
            log(f"Unexpected error with registry file {reg_file}: {str(e)}")

def cmd_tweaks():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cmd_tweaks_dir = os.path.join(os.path.dirname(current_dir), 'scripts', 'Misc_Tweaks')
    
    cmd_scripts = [
        'Debloat_Send_To_Context_Menu.cmd',
        'Disable_FSO_and_Game_Bar_Support.cmd',
        'Disable_Hibernation.cmd',
        'Disable_Location.cmd',
        'Disable_Microsoft_Copilot.cmd',
        'Disable_Mobile_Device_Settings.cmd',
        'Disable_Powersaving.cmd',
        'Disable_Printing.cmd',
        'Disable_Recent_Items.cmd',
        'Disable_Search_Indexing.cmd',
        'Disable_Sleep_Study.cmd',
        'Disable_Web_Search.cmd',
        'Disable_Widgets_.cmd',
        'Enable_Sleep.cmd',
        'Reset_Network_to_WinPrivacy.cmd',
        'Winprivacy_Visual_Effects.cmd',
    ]
    
    for cmd_script in cmd_scripts:
        if not cmd_script:
            continue
            
        cmd_path = os.path.join(cmd_tweaks_dir, cmd_script)
        try:
            if not os.path.exists(cmd_path):
                log(f"Warning: CMD script {cmd_script} not found in {cmd_tweaks_dir}")
                continue

            log(f"Running CMD script: {cmd_script}")
            result = subprocess.run(["cmd.exe", "/C", cmd_path], 
                                  check=True, 
                                  capture_output=True, 
                                  text=True)
            
            if result.returncode == 0:
                log(f"Successfully ran CMD script: {cmd_script}")
                log('Running PowerShell tweaks')
                ps1_tweaks()                
            else:
                log(f"Failed to run CMD script {cmd_script}. Error: {result.stderr}")
                
        except subprocess.CalledProcessError as e:
            log(f"Error running CMD script {cmd_script}: {str(e)}")
        except Exception as e:
            log(f"Unexpected error with CMD script {cmd_script}: {str(e)}")

def ps1_tweaks():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ps1_tweaks_dir = os.path.join(os.path.dirname(current_dir), 'scripts', 'Misc_Tweaks')
    
    ps1_scripts = [
        'DisablePowerSaving.ps1',
        'DisableFileSharing.ps1'
    ]
    
    for ps1_script in ps1_scripts:
        if not ps1_script:
            continue
            
        ps1_path = os.path.join(ps1_tweaks_dir, ps1_script)
        try:
            if not os.path.exists(ps1_path):
                log(f"Warning: PowerShell script {ps1_script} not found in {ps1_tweaks_dir}")
                continue

            log(f"Running PowerShell script: {ps1_script}")
            result = subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", ps1_path], 
                                  check=True, 
                                  capture_output=True, 
                                  text=True)
            
            if result.returncode == 0:
                log(f"Successfully ran PowerShell script: {ps1_script}")

            else:
                log(f"Failed to run PowerShell script {ps1_script}. Error: {result.stderr}")
                
        except subprocess.CalledProcessError as e:
            log(f"Error running PowerShell script {ps1_script}: {str(e)}")
        except Exception as e:
            log(f"Unexpected error with PowerShell script {ps1_script}: {str(e)}")

if __name__ == "__main__":
    main()