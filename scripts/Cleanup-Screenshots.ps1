# Cleanup-Screenshots.ps1
# Deletes screenshots older than 14 days from Pictures\Screenshots
# Created: 2026-09-05
# Runs via Task Scheduler daily

$ScreenshotsPath = Join-Path $env:USERPROFILE "Pictures\Screenshots"
$MaxAgeDays = 14
$LogFile = Join-Path $env:USERPROFILE "Documents\Default Project\scripts\screenshot-cleanup.log"

# Ensure paths exist
if (-not (Test-Path $ScreenshotsPath)) {
    Add-Content -Path $LogFile -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Screenshots folder not found: $ScreenshotsPath"
    exit
}

# Find old screenshots
$cutoffDate = (Get-Date).AddDays(-$MaxAgeDays)
$oldFiles = Get-ChildItem -Path $ScreenshotsPath -File -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -lt $cutoffDate }

if ($oldFiles.Count -eq 0) {
    Add-Content -Path $LogFile -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] No old screenshots found (0 files older than $MaxAgeDays days)"
    exit
}

# Calculate total size
$totalSizeMB = [math]::Round(($oldFiles | Measure-Object -Property Length -Sum).Sum / 1MB, 1)

# Delete
$deleted = 0
$errors = 0
foreach ($file in $oldFiles) {
    try {
        Remove-Item -LiteralPath $file.FullName -Force -ErrorAction Stop
        $deleted++
    } catch {
        $errors++
    }
}

# Log
$logLine = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Deleted $deleted / $($oldFiles.Count) screenshots ($totalSizeMB MB) older than $MaxAgeDays days. Errors: $errors"
Add-Content -Path $LogFile -Value $logLine
