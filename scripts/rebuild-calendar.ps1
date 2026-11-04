<#
.SYNOPSIS
  Rebuilds the Obsidian vault's Calendar.md from daily-note frontmatter.

.DESCRIPTION
  Zero-plugin calendar. Reads YYYY-MM-DD.md notes in the vault root, pulls the
  `events:` list out of each note's frontmatter, and writes a Monday-first month
  grid plus a this-week agenda to Calendar.md. Days with a note but no events
  fall back to "standard day" so the grid always reads as a real week.

  Add an event by editing the Properties panel of any daily note. Never
  hand-edit Calendar.md - it is overwritten.

  All literals in this script are ASCII on purpose: Windows PowerShell 5.1
  reads BOM-less .ps1 files as ANSI, so a literal en-dash in here would be
  mojibake in the output. Non-ASCII is read from the notes with -Encoding UTF8
  and written back as BOM-less UTF-8.

.PARAMETER Vault
  Vault root. Defaults to the openhuman journal vault.

.PARAMETER Month
  Any date inside the month to render. Defaults to today.

.EXAMPLE
  .\rebuild-calendar.ps1
  .\rebuild-calendar.ps1 -Month 2026-11-01
#>
param(
  [string]$Vault = 'C:\Users\ZBook\.openhuman\users\6a744f5e93802f5472ebc834\workspace\memory_tree\content\.obsidian\journal',
  [datetime]$Month = (Get-Date)
)

$ErrorActionPreference = 'Stop'

function Get-DayInfo {
  param([datetime]$Date)

  $iso = $Date.ToString('yyyy-MM-dd')
  $path = Join-Path $Vault "$iso.md"
  # Events come from the "## Calendar events" section that
  # scripts\sync-calendar-events.ps1 writes, not from frontmatter. Each line is
  # "- Title [uid:: x] [startTime:: HH:mm] [endTime:: HH:mm] [location:: y]";
  # display as "HH:mm-HH:mm Title" and strip the inline fields.
  [string[]]$events = @()
  $hasNote = Test-Path -LiteralPath $path

  if ($hasNote) {
    $inSection = $false
    foreach ($line in (Get-Content -LiteralPath $path -Encoding UTF8)) {
      if ($line -match '^##\s') { $inSection = ($line.Trim() -eq '## Calendar events'); continue }
      if (-not $inSection) { continue }
      if ($line -notmatch '^\s*-\s') { continue }

      $item = $line.Trim() -replace '^\-\s*', ''
      $start = if ($item -match '\[startTime::\s*([^\]]+)\]') { $Matches[1].Trim() } else { '' }
      $end = if ($item -match '\[endTime::\s*([^\]]+)\]') { $Matches[1].Trim() } else { '' }
      $title = ($item -replace '\s*\[[^\]]*\]', '').Trim()
      if (-not $title) { continue }

      # Strip the colour category prefix the plugin consumes
      # ("Category - Sub - Title" is displayed by the plugin as "Sub - Title").
      if ($title -match '^[A-Za-z]+ - (.*)$') { $title = $Matches[1] }

      if ($start -and $end) { $events += @("$start-$end $title") }
      elseif ($start) { $events += @("$start $title") }
      else { $events += @($title) }
    }
  }

  [pscustomobject]@{ Iso = $iso; HasNote = $hasNote; Events = $events }
}

function Get-MondayFirstOffset {
  param([datetime]$Date)
  # DayOfWeek: Sunday=0 ... Saturday=6. Monday-first index: Sunday=6, Monday=0 ... Saturday=5
  (([int]$Date.DayOfWeek) + 6) % 7
}

$today = (Get-Date).Date
$todayIso = $today.ToString('yyyy-MM-dd')

$firstOfMonth = [datetime]::new($Month.Year, $Month.Month, 1)
$lastOfMonth = $firstOfMonth.AddMonths(1).AddDays(-1)

$out = New-Object System.Collections.Generic.List[string]
$out.Add('# Calendar')
$out.Add('')
$out.Add('> Generated from daily-note frontmatter by `scripts\rebuild-calendar.ps1`.')
$out.Add('> Do not hand-edit this file, it is overwritten. Add events in a daily note''s Properties panel instead.')
$out.Add('')

# ---- Month grid -------------------------------------------------------------
$out.Add("## $($firstOfMonth.ToString('MMMM yyyy'))")
$out.Add('')
$out.Add('| Mon | Tue | Wed | Thu | Fri | Sat | Sun |')
$out.Add('|---|---|---|---|---|---|---|')

$row = New-Object System.Collections.Generic.List[string]
for ($i = 0; $i -lt (Get-MondayFirstOffset $firstOfMonth); $i++) { $row.Add('') }

for ($day = 1; $day -le $lastOfMonth.Day; $day++) {
  $date = $firstOfMonth.AddDays($day - 1)
  $info = Get-DayInfo -Date $date

  $cell = "$day"
  if ($info.HasNote) { $cell = "[[$($info.Iso)]] $day" }

  if ($info.Events.Count -gt 0) {
    $cell += '<br>' + ($info.Events -join '<br>')
  }
  elseif ($info.HasNote) {
    $cell += '<br>standard day'
  }

  if ($info.Iso -eq $todayIso) { $cell = "**$cell**" }

  $row.Add($cell)
  if ($row.Count -eq 7) {
    $out.Add('| ' + ($row -join ' | ') + ' |')
    $row.Clear()
  }
}
if ($row.Count -gt 0) {
  while ($row.Count -lt 7) { $row.Add('') }
  $out.Add('| ' + ($row -join ' | ') + ' |')
}

$out.Add('')

# ---- This week --------------------------------------------------------------
$weekStart = $today.AddDays(-(Get-MondayFirstOffset $today))
$weekEnd = $weekStart.AddDays(6)

$out.Add("## This week - $($weekStart.ToString('d MMM')) to $($weekEnd.ToString('d MMM'))")
$out.Add('')
$out.Add('| Day | Date | Events |')
$out.Add('|---|---|---|')

for ($i = 0; $i -lt 7; $i++) {
  $date = $weekStart.AddDays($i)
  $info = Get-DayInfo -Date $date
  $dayName = $date.ToString('dddd')
  $label = if ($info.Iso -eq $todayIso) { "**$dayName (today)**" } else { $dayName }
  $link = if ($info.HasNote) { "[[$($info.Iso)]]" } else { $info.Iso }

  if ($info.Events.Count -gt 0) { $events = ($info.Events -join '<br>') }
  elseif ($info.HasNote) { $events = 'standard day - see the note' }
  else { $events = 'no note yet' }

  $out.Add("| $label | $link | $events |")
}

$out.Add('')
$out.Add('## Standard weekday shape')
$out.Add('')
$out.Add('| Time | Block |')
$out.Add('|---|---|')
$out.Add('| 05:30 | Wake - water, no phone |')
$out.Add('| 05:35-06:05 | Train (M/W/F) / Walk (T/Th) |')
$out.Add('| 06:05-06:25 | Shower + AM skincare |')
$out.Add('| 06:25-06:40 | Breakfast |')
$out.Add('| 06:40-07:20 | Travel |')
$out.Add('| 07:30-13:25 | P1-P4 at school |')
$out.Add('| 13:35-16:45 | Elective block |')
$out.Add('| 16:45-17:30 | Travel home |')
$out.Add('| 17:30-18:00 | Decompress |')
$out.Add('| 18:00-18:30 | Dinner |')
$out.Add('| **18:30-19:30** | **Tutor** |')
$out.Add('| 19:30-19:45 | Break |')
$out.Add('| **19:45-21:15** | **Free** |')
$out.Add('| 21:15-21:30 | Pack bag / screens down |')
$out.Add('| 22:00 | Bed |')
$out.Add('')
$out.Add('Full grid and rules: [[timeblocking]]')

$dest = Join-Path $Vault 'Calendar.md'
[System.IO.File]::WriteAllText($dest, ($out -join "`n"), (New-Object System.Text.UTF8Encoding($false)))

"wrote $dest - $($lastOfMonth.Day) days, $($firstOfMonth.ToString('MMMM yyyy'))"