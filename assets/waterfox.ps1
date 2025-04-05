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
