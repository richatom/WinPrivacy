$powerPlanFile = "C:\Users\atom\Documents\GitHub\WinPrivacy\components\powerplan.pow"
powercfg -import "$powerPlanFile"
$powerPlanGUID = (powercfg -list | Where-Object { $_ -match "Optimized Power Plan" }) -replace ".*GUID: ([^ ]*).*", '$1'

if ($powerPlanGUID) {
    powercfg -setactive $powerPlanGUID
    Write-Host "Optimized Power Plan activated successfully!"
} else {
    Write-Host "Failed to find the imported power plan."
}
