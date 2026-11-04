$raw = Get-Content check.json -Raw
$s = $raw.IndexOf('{')
$json = $raw.Substring($s)
$o = $json | ConvertFrom-Json
"TOP ok=$($o.ok) lintOk=$($o.lint.ok) errors=$($o.lint.errorCount) warnings=$($o.lint.warningCount)"
$o.lint.findings | ForEach-Object {
  "CODE=$($_.code) SEV=$($_.severity) SEL=$($_.selector) MSG=$($_.message)"
}
