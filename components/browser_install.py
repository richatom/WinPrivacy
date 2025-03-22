""" Import necessary modules for the program to work """
import subprocess



""" Install whichever browser the user selected from browser_select_screen """
def install_browser(selected_browser):
    browser_map = {
        "Chrome": "Google.Chrome",
        "Brave": "Brave.Brave",
        "Firefox": "Mozilla.Firefox",
        "Librewolf": "Librewolf.Librewolf",
        "Edge": "Microsoft.Edge"
    }
    if selected_browser not in browser_map:
        print(f"Unknown browser selected: {selected_browser}")
        return
    browser_id = browser_map[selected_browser]
    print(f"Installing {selected_browser} via Winget...")
    try:
        subprocess.run(
            ["winget", "install", browser_id, "--silent", "--accept-package-agreements", "--accept-source-agreements"],
            check=True
        )
        print(f"{selected_browser} installation completed.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {selected_browser}: {e}")
