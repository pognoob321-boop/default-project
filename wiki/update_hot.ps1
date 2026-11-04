# update_hot.ps1 — Regenerates wiki/hot.md from wiki/log.md
# Run from project root: powershell -ExecutionPolicy Bypass -File wiki/update_hot.ps1

$ErrorActionPreference = "SilentlyContinue"
$wikiDir = "wiki"
$logFile = "$wikiDir\log.md"
$hotFile = "$wikiDir\hot.md"

# Read existing hot.md to preserve Next Actions block
$nextActions = ""
if (Test-Path $hotFile) {
    $content = Get-Content $hotFile -Raw
    if ($content -match '(?s)## Next Actions\s*\n(.*)') {
        $nextActions = $matches[1].Trim()
    }
}

# Parse log.md for recent entries (last 10)
$logEntries = @()
if (Test-Path $logFile) {
    $lines = Get-Content $logFile
    foreach ($line in $lines) {
        if ($line -match '^## \[(\d{4}-\d{2}-\d{2})\]\s*(.*)') {
            $logEntries += "- $line"
        }
    }
}
$recentLog = ($logEntries | Select-Object -Last 10) -join "`n"
if (-not $recentLog) { $recentLog = "_No log entries yet._" }

# Count features
$featureCount = 0
$activeCount = 0
if (Test-Path "$wikiDir\features") {
    $features = Get-ChildItem "$wikiDir\features\*.md" -ErrorAction SilentlyContinue
    $featureCount = $features.Count
    foreach ($f in $features) {
        $fc = Get-Content $f.FullName -Raw
        if ($fc -match 'status:\s*active') { $activeCount++ }
    }
}

# Count failed ideas
$failedCount = 0
$ledgerFile = "$wikiDir\Failed Ideas\ledger.md"
if (Test-Path $ledgerFile) {
    $ledger = Get-Content $ledgerFile
    $failedCount = ($ledger | Where-Object { $_ -match '^\|.*\|.*\|.*\|.*\|' -and $_ -notmatch '^\| Date' -and $_ -notmatch '^\| —' }).Count
}

# Generate
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
$hot = @"
> **AUTO-GENERATED** — Do not hand-edit the sections between the banners.
> The script ``wiki/update_hot.ps1`` owns this file. Edit the "Next Actions" block only.

<!-- BEGIN AUTO -->

## Current State

- Updated: $timestamp
- Features: $featureCount total, $activeCount active
- Failed ideas: $failedCount

## Recent Log

$recentLog

<!-- END AUTO -->

## Next Actions

$nextActions
"@

Set-Content -Path $hotFile -Value $hot -Encoding UTF8
Write-Output "hot.md regenerated"
