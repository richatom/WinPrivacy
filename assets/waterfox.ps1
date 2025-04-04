Write-Output "Starting Waterfox installation via winget..."

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Error "Winget is not available. Install App Installer from Microsoft Store."
    exit 1
}

winget install --id Waterfox.Waterfox --source winget --accept-package-agreements --accept-source-agreements

Write-Output "Waterfox installation completed."