<#
.SYNOPSIS
  Writes the plugin-format calendar event list into each daily note.

.DESCRIPTION
  Full Calendar Remastered reads a "Daily Note" calendar source by parsing list
  items under a heading. This script keeps that section in sync with the aSc
  timetable so the vault's calendar shows the real week instead of an empty grid.

  Format written per line (the plugin's default inline-field format - it is the
  one that can express a start with no end, which the strict DayPlanner prefix
  cannot):
      - Category - Title [uid:: unique] [startTime:: HH:mm] [endTime:: HH:mm] [location:: ...]

  The leading "Category - " is NOT decoration. Advanced Categorization parses
  the title as `Category - Sub-Category - Event Name`, strips the category from
  what the calendar displays, and colours the event from the matching entry in
  the plugin's categorySettings. Categories and their aSc timetable colours:

      Math      #F9E17D  yellow        Social    #F5A9B8  pink
      English   #A9C6F5  periwinkle    CS        #7ED8C3  mint
      Science   #93DC93  green         Health    #7FD6D6  cyan
      Elective  #B5D96B  lime          Advisory  #9BB0C4  slate
      Options   #C4B5FD  purple        Study     #818CF8  indigo
      Personal  #F6A85C  orange

  ELECTIVE STRUCTURE - read this before "fixing" it again. On the Grade 9
  Phnom Penh printout each weekday column has ONE merged cell spanning
  13:35-15:05 (a 10-minute break sits inside it at 14:15-14:25) and ONE merged
  cell spanning 15:16-16:45 (break inside at 15:55-16:05). The teacher name is
  printed once per merged cell, which is the tell. So Monday's K is a single
  90-minute period, NOT two 40-minute slots. Splitting those cells into
  13:35-14:15 and 14:25-15:05 is wrong and it also made the day end at 15:05
  instead of 16:45. WEDNESDAY IS THE EXCEPTION: its column has three separate
  cells - M at 13:35-14:15, K at 14:25-15:05, C at 15:16-16:45 (the last cell
  is still 90 minutes; only the first two are shortened).

  SUBJECT LEGEND, supplied by the user 2026-10-19. The printouts carry no key,
  so the codes are resolved HERE only and always spelled out in the event
  title: K=Khmer, H=History, C=Chemistry, Mo=Civic Ethics, G=Geography,
  M=Mathematics, Ea=Earth Study, P=Physics, B=Biology.

  The section is regenerated from scratch every run, so it is safe to re-run.
  Only the documented inline fields are used: uid, startTime, endTime, location.

  ASCII-only on purpose: Windows PowerShell 5.1 reads BOM-less .ps1 as ANSI.

.PARAMETER Vault
  Vault root. Defaults to the openhuman journal vault.
#>
param(
  [string]$Vault = 'C:\Users\ZBook\.openhuman\users\6a744f5e93802f5472ebc834\workspace\memory_tree\content\.obsidian\journal'
)

$ErrorActionPreference = 'Stop'

# Each entry: ISO date -> ordered list of @{ T=title; S=start; E=end; L=location }
$week = [ordered]@{
  '2026-10-19' = @(
    @{ T='Social - Social Studies';S='07:30';E='08:40';L='Room 202 - Daniel SS' },
    @{ T='Math - Mathematics';S='08:55';E='10:05';L='Room 137 - Natun' },
    @{ T='English - English Language Arts';S='10:10';E='11:20';L='Room 105 - Arna' },
    @{ T='Advisory - Advisory';S='11:20';E='11:35';L='Room 111 - Kris' },
    @{ T='Science - Life Science + Chemistry';S='12:15';E='13:25';L='Rooms 302/303 - R-Jay' },
    @{ T='Elective - Khmer';S='13:35';E='15:05';L='San Sreynich' },
    @{ T='Elective - History';S='15:16';E='16:45';L='Phorn Seyha' },
    @{ T='Personal - Tutor';S='18:30';E='19:30';L='' },
    @{ T="Personal - Meeting at friend's - presentation + record";S='20:30';E='';L="Friend's house" }
  )
  '2026-10-20' = @(
    @{ T='Math - Mathematics';S='07:30';E='08:40';L='Room 137 - Natun' },
    @{ T='Health - Health and Hygiene';S='08:55';E='10:05';L='Room 2023 - Rurrel' },
    @{ T='Social - Social Studies';S='10:10';E='11:20';L='Room 202 - Daniel SS' },
    @{ T='Advisory - Advisory';S='11:20';E='11:35';L='Room 111 - Kris' },
    @{ T='Science - Life Science + Chemistry';S='12:15';E='13:25';L='Rooms 302/303 - R-Jay' },
    @{ T='Elective - Biology';S='13:35';E='15:05';L='Him Sarith' },
    @{ T='Elective - Mathematics';S='15:16';E='16:45';L='Eang Samathphary' },
    @{ T='Personal - Tutor';S='18:30';E='19:30';L='' }
  )
  '2026-10-21' = @(
    @{ T='English - English Language Arts';S='07:30';E='08:40';L='Room 105 - Arna' },
    @{ T='CS - Computer Science Principles';S='08:55';E='10:05';L='Room 106 - Aric' },
    @{ T='Math - Mathematics';S='10:10';E='11:20';L='Room 137 - Natun' },
    @{ T='Advisory - Advisory';S='11:20';E='11:35';L='Room 111 - Kris' },
    @{ T='Science - Life Science + Chemistry';S='12:15';E='13:25';L='Rooms 302/303 - R-Jay' },
    @{ T='Elective - Mathematics';S='13:35';E='14:15';L='Eang Samathphary' },
    @{ T='Elective - Khmer';S='14:25';E='15:05';L='San Sreynich' },
    @{ T='Elective - Chemistry';S='15:16';E='16:45';L='Son Chanthirit' },
    @{ T='Personal - Tutor';S='18:30';E='19:30';L='' }
  )
  '2026-10-22' = @(
    @{ T='Social - Social Studies';S='07:30';E='08:40';L='Room 202 - Daniel SS' },
    @{ T='English - English Language Arts';S='08:55';E='10:05';L='Room 105 - Arna' },
    @{ T='CS - Computer Science Principles';S='10:10';E='11:20';L='Room 111 - Kris' },
    @{ T='Advisory - Advisory';S='11:20';E='11:35';L='Room 111 - Kris' },
    @{ T='Math - Mathematics';S='12:15';E='13:25';L='Room 137 - Natun' },
    @{ T='Elective - Civic Ethics';S='13:35';E='15:05';L='Chheang Bunthour' },
    @{ T='Elective - Khmer';S='15:16';E='16:45';L='San Sreynich' },
    @{ T='Personal - Tutor';S='18:30';E='19:30';L='' }
  )
  '2026-10-23' = @(
    @{ T='Science - Life Science + Chemistry';S='07:30';E='08:40';L='Rooms 302/303 - R-Jay' },
    @{ T='English - English Language Arts';S='08:55';E='10:05';L='Room 105 - Arna' },
    @{ T='Options - Rotation - Pre-Calc / Optics';S='10:10';E='11:20';L='Kris' },
    @{ T='Advisory - Advisory';S='11:20';E='11:35';L='Room 111 - Kris' },
    @{ T='Social - Social Studies';S='12:15';E='13:25';L='Room 202 - Daniel SS' },
    @{ T='Elective - Mathematics';S='13:35';E='15:05';L='Eang Samathphary' },
    @{ T='Elective - Physics';S='15:16';E='16:45';L='Chhan Kimchhorn' },
    @{ T='Personal - Tutor';S='18:30';E='19:30';L='' }
  )
  '2026-10-24' = @(
    @{ T='Elective - Geography';S='13:35';E='15:05';L='Bun Yithro' },
    @{ T='Elective - Earth Study';S='15:16';E='16:45';L='Pich Khunnarady' },
    @{ T='Study - Homework catch-up';S='17:30';E='18:00';L='Carried over from Monday' },
    @{ T='Study - Geography + Earth Study';S='18:00';E='18:30';L="Today's electives - retrieval" },
    @{ T='Personal - Football';S='18:30';E='19:30';L='' }
  )
  '2026-10-25' = @(
    @{ T='Personal - Weekly review';S='07:10';E='07:15';L='Photo check + weigh in' },
    @{ T='Personal - Football';S='13:30';E='14:30';L='' },
    @{ T='Personal - Neck curls 3x15-20';S='14:30';E='15:00';L='' }
  )
}

$heading = '## Calendar events'
$enc = New-Object System.Text.UTF8Encoding($false)

foreach ($iso in $week.Keys) {
  $path = Join-Path $Vault "$iso.md"
  if (-not (Test-Path -LiteralPath $path)) {
    Write-Warning "missing $iso.md, skipped"
    continue
  }

  $lines = [System.Collections.Generic.List[string]]::new()
  foreach ($l in (Get-Content -LiteralPath $path -Encoding UTF8)) { $lines.Add($l) }

  # Rewrite the whole frontmatter block. The Calendar events section below is
  # now the single source of truth, so no events key lives in the frontmatter.
  # (Rebuilding the block wholesale also guarantees no orphaned list items are
  # left behind when a key is removed - YAML breaks if they survive.)
  $dayName = ([datetime]::ParseExact($iso, 'yyyy-MM-dd', $null)).ToString('dddd')
  if ($lines.Count -gt 0 -and $lines[0].Trim() -eq '---') {
    $close = -1
    for ($i = 1; $i -lt $lines.Count; $i++) {
      if ($lines[$i].Trim() -eq '---') { $close = $i; break }
    }
    if ($close -gt 0) { $lines.RemoveRange(0, $close + 1) }
  }
  $fm = @('---', "date: $iso", "day: $dayName", '---')
  for ($i = $fm.Count - 1; $i -ge 0; $i--) { $lines.Insert(0, $fm[$i]) }

  # Rebuild the Calendar events section from scratch.
  $start = -1
  for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i].Trim() -eq $heading) { $start = $i; break }
  }
  if ($start -ge 0) {
    $end = $start + 1
    while ($end -lt $lines.Count -and $lines[$end] -notmatch '^##\s') { $end++ }
    while ($end -gt $start -and [string]::IsNullOrWhiteSpace($lines[$end - 1])) { $end-- }
    $lines.RemoveRange($start, $end - $start)
    while ($lines.Count -gt 0 -and [string]::IsNullOrWhiteSpace($lines[$lines.Count - 1])) { $lines.RemoveAt($lines.Count - 1) }
  }

  # A markdown heading needs a blank line before it or it is not parsed as a heading.
  $lines.Add('')

  $block = [System.Collections.Generic.List[string]]::new()
  $block.Add($heading)
  $block.Add('')
  $n = 0
  foreach ($ev in $week[$iso]) {
    $n++
    $s = "- $($ev.T) [uid:: s-$($iso.Replace('-',''))-$n] [startTime:: $($ev.S)]"
    if ($ev.E) { $s += " [endTime:: $($ev.E)]" }
    if ($ev.L) { $s += " [location:: $($ev.L)]" }
    $block.Add($s)
  }
  $block.Add('')
  $block.Add('> Read by the Full Calendar Remastered plugin. The leading word of each line is its colour category. Regenerated by `scripts\sync-calendar-events.ps1` - edit the script, not this section.')
  $block.Add('')

  while ($block.Count -gt 0) { $lines.Add($block[0]); $block.RemoveAt(0) }

  [System.IO.File]::WriteAllText($path, ($lines -join "`n"), $enc)
  "$iso  $($week[$iso].Count) events"
}