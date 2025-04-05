@echo off
:: https://privacy.sexy — v0.13.8 — Sat, 05 Apr 2025 17:44:30 GMT
:: Ensure PowerShell is available
where PowerShell >nul 2>&1 || (
    echo PowerShell is not available. Please install or enable PowerShell.
    pause & exit 1
)
:: Ensure admin privileges
fltmc >nul 2>&1 || (
    echo Administrator privileges are required.
    PowerShell Start -Verb RunAs '%0' 2> nul || (
        echo Right-click on the script and select "Run as administrator".
        pause & exit 1
    )
    exit 0
)
:: Initialize environment
setlocal EnableExtensions DisableDelayedExpansion


:: ----------------------------------------------------------
:: -Disable app access to paired Bluetooth devices (revert)--
:: ----------------------------------------------------------
echo --- Disable app access to paired Bluetooth devices (revert)
:: Restore app capability (bluetooth) using user privacy settings
:: Set the registry value "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\bluetooth!Value"
PowerShell -ExecutionPolicy Unrestricted -Command "$revertData =  'Allow'; reg add 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\bluetooth' /v 'Value' /t 'REG_SZ' /d "^""$revertData"^"" /f"
:: ----------------------------------------------------------


:: ----------------------------------------------------------
:: Disable app access to unpaired Bluetooth devices (revert)-
:: ----------------------------------------------------------
echo --- Disable app access to unpaired Bluetooth devices (revert)
:: Restore app capability (bluetoothSync) using user privacy settings
:: Set the registry value "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\bluetoothSync!Value"
PowerShell -ExecutionPolicy Unrestricted -Command "$revertData =  'Allow'; reg add 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\bluetoothSync' /v 'Value' /t 'REG_SZ' /d "^""$revertData"^"" /f"
:: ----------------------------------------------------------


:: ----------------------------------------------------------
:: -----Disable Bluetooth usage data collection (revert)-----
:: ----------------------------------------------------------
echo --- Disable Bluetooth usage data collection (revert)
:: Restore scheduled task(s) to default state: `\Microsoft\Windows\Customer Experience Improvement Program\BthSQM`
PowerShell -ExecutionPolicy Unrestricted -Command "$taskPathPattern='\Microsoft\Windows\Customer Experience Improvement Program\'; $taskNamePattern='BthSQM'; $shouldDisable =  $false; Write-Output "^""Enabling tasks matching pattern `"^""$taskNamePattern`"^""."^""; $tasks = @(Get-ScheduledTask -TaskPath $taskPathPattern -TaskName $taskNamePattern -ErrorAction Ignore); if (-Not $tasks) { Write-Warning ( "^""Missing task: Cannot enable, no tasks matching pattern `"^""$taskNamePattern`"^"" found."^"" + "^"" This task appears to be not included in this version of Windows."^"" ); exit 0; }; $operationFailed = $false; foreach ($task in $tasks) { $taskName = $task.TaskName; if ($shouldDisable) { if ($task.State -eq [Microsoft.PowerShell.Cmdletization.GeneratedTypes.ScheduledTask.StateEnum]::Disabled) { Write-Output "^""Skipping, task `"^""$taskName`"^"" is already disabled, no action needed."^""; continue; }; } else { if (($task.State -ne [Microsoft.PowerShell.Cmdletization.GeneratedTypes.ScheduledTask.StateEnum]::Disabled) -and ($task.State -ne [Microsoft.PowerShell.Cmdletization.GeneratedTypes.ScheduledTask.StateEnum]::Unknown)) { Write-Output "^""Skipping, task `"^""$taskName`"^"" is already enabled, no action needed."^""; continue; }; }; try { if ($shouldDisable) { $task | Disable-ScheduledTask -ErrorAction Stop | Out-Null; Write-Output "^""Successfully disabled task `"^""$taskName`"^""."^""; } else { $task | Enable-ScheduledTask -ErrorAction Stop | Out-Null; Write-Output "^""Successfully enabled task `"^""$taskName`"^""."^""; }; } catch { Write-Error "^""Failed to restore task `"^""$taskName`"^"": $($_.Exception.Message)"^""; $operationFailed = $true; }; }; if ($operationFailed) { Write-Output 'Failed to restore some tasks. Check error messages above.'; exit 1; }"
:: ----------------------------------------------------------


:: Pause the script to view the final state
pause
:: Restore previous environment settings
endlocal
:: Exit the script successfully
exit /b 0