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
    reg_files = [
        r'Default',
        r'',
        r'',
        r'',
        r'',
        r'',

    ]

    # Running regedit silently to import the reg file
    for reg_file in reg_files:
        try:
            subprocess.run(["regedit.exe", "/s", reg_file], check=True)
            print("Registry file applied successfully.")
        except subprocess.CalledProcessError:
            print("Failed to apply the registry file.")

    

def custom_scripts():


if __name__ == "__main__":
    main()