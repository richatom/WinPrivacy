$desktopPath = [Environment]::GetFolderPath('Desktop')
$atomFolderPath = Join-Path $desktopPath "Win Privacy"
$zipUrl = "https://raw.githubusercontent.com/richatom/WinPrivacy/refs/heads/main/assets/WinPrivacy.zip"
$zipPath = Join-Path $env:TEMP "AtomUtilites.zip"
$tempExtractPath = Join-Path $env:TEMP "AtomUtilites_Extracted"

if (-not (Test-Path -Path $atomFolderPath)) {
    New-Item -ItemType Directory -Path $atomFolderPath | Out-Null
}

Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath

Expand-Archive -Path $zipPath -DestinationPath $tempExtractPath -Force

Get-ChildItem -Path $tempExtractPath | ForEach-Object {
    Move-Item -Path $_.FullName -Destination $atomFolderPath -Force
}

Remove-Item $zipPath -Force
Remove-Item $tempExtractPath -Recurse -Force
