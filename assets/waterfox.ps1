$waterfoxUrl = "https://cdn.waterfox.net/releases/latest/win64/installer/Waterfox%20G.exe"
$downloadPath = "$env:TEMP\WaterfoxInstaller.exe"

Write-Host "Downloading Waterfox from $waterfoxUrl..."
Invoke-WebRequest -Uri $waterfoxUrl -OutFile $downloadPath

if (Test-Path $downloadPath) {
    Write-Host "Waterfox has been downloaded successfully to $downloadPath"
    
    Write-Host "Starting Waterfox installation..."
    Start-Process -FilePath $downloadPath -ArgumentList "/S" -NoNewWindow -Wait

    Write-Host "Waterfox installation completed."
    
    Remove-Item $downloadPath -Force
} else {
    Write-Host "Download failed!"
}
