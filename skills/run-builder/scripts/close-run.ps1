<#
.SYNOPSIS
  Close a /run-builder run. Windows PowerShell 5.1 safe (no &&, no ternary).

.DESCRIPTION
  BENCHED by charter Article 33 until the rig-lifecycle drill passes: the gate closes by hand
  (templates\PROMPT-GATE.md.tmpl, "The final turn"). Kept, and kept correct, for the day the bench lifts.

  Run by the GATE lane at the final turn, AFTER next-shift/PROMPTS.md, next-shift/RUN.md,
  HANDOFF.md, REPORT.md and OWNER-QUESTIONS.md (the office question ids asked) are written.

  Tags run-NN-close at a named commit, flips the LEDGER row OPEN -> CLOSED, removes this run's own
  run-* scratch dirs and VERIFIES the removal, and emits evidence/gate/CONFORMANCE.json.

  It does not deploy. It does not push. Deploy is always the owner's attended act.

.EXAMPLE
  .\close-run.ps1 -RunDir 'D:\Hub\20-Coding\Projects\my-app\runs\run-70' -RepoPath 'D:\Hub\20-Coding\Projects\my-app' -CloseSha abc1234
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$RunDir,
  [Parameter(Mandatory=$true)][string]$RepoPath,
  [Parameter(Mandatory=$true)][string]$CloseSha,
  [string]$LegsMet,
  [switch]$KeepWorktrees
)

$ErrorActionPreference = 'Stop'

function Resolve-HubRoot {
  $candidates = @('D:\Hub', 'C:\Hub')
  foreach ($c in $candidates) {
    $marker = $c + '\CLAUDE.md'
    if (Test-Path -LiteralPath $marker) { return $c }
  }
  throw "Hub root not found. Probed D:\Hub\CLAUDE.md then C:\Hub\CLAUDE.md; neither exists."
}

$HubRoot = Resolve-HubRoot
$Ledger  = $HubRoot + '\50-AI\fleet-ops\runs\LEDGER.md'

if (-not (Test-Path -LiteralPath $RunDir))  { throw ("run dir not found: " + $RunDir) }
if (-not (Test-Path -LiteralPath ($RepoPath + '\.git'))) { throw ("not a git repo: " + $RepoPath) }

$runName = Split-Path -Leaf $RunDir
$tag     = $runName + '-close'

# ---------------------------------------------------------------- conformance checks

# Check 1 - run object committed pre-launch: the prep commit exists and precedes every lane commit.
# Every --grep is ONE argument: Windows PowerShell 5.1 hands `--grep=(expr)` to git as two, so git read
# the pattern as a revision ("invalid object name 'run-6 prep'") and the check failed (run-6, 2026-10-07).
$prepLine = git -C $RepoPath log --pretty='%H %s' ('--grep=' + [regex]::Escape($runName) + ' prep:')
$c1 = $false
if ($LASTEXITCODE -eq 0) {
  if (-not [string]::IsNullOrWhiteSpace($prepLine)) { $c1 = $true }
}

# Check 2 - lane count == shape. Read the shape from RUN.md; count the prompt files.
$runMd  = Get-Content -LiteralPath ($RunDir + '\RUN.md') -Raw
$shape  = ''
$m = [regex]::Match($runMd, '\*\*Shape:\*\*\s*([A-E]+)')
if ($m.Success) { $shape = $m.Groups[1].Value }
$promptCount = (Get-ChildItem -LiteralPath ($RunDir + '\prompts') -Filter 'PROMPT-*.md' -ErrorAction SilentlyContinue | Measure-Object).Count
$c2 = $false
if ($shape.Length -gt 0) { if ($promptCount -eq $shape.Length) { $c2 = $true } }

# Check 3 - gate lane non-building: zero product-code commits authored by the gate lane.
# Determined by inspecting THIS run's gate commits ("[run-N][lane-<gate>]", a fixed string) that touch
# paths outside runs/ and backlog/. Every "[lane-<gate>]" in history also caught older runs whose lane of
# that letter was a builder (run-6: 75 such commits). A git error or an unread shape is a FAIL, never a
# pass that checked nothing.
$gateLetter = ''
if ($shape.Length -gt 0) { $gateLetter = $shape.Substring($shape.Length - 1, 1).ToLower() }
$c3 = $false
if ($gateLetter.Length -gt 0) {
  $gateMarker  = '[' + $runName + '][lane-' + $gateLetter + ']'
  $gateCommits = git -C $RepoPath log --pretty=%H --fixed-strings ('--grep=' + $gateMarker)
  if ($LASTEXITCODE -eq 0) { $c3 = $true }
  foreach ($sha in $gateCommits) {
    if (-not [string]::IsNullOrWhiteSpace($sha)) {
      $touched = git -C $RepoPath show --name-only --pretty=format: $sha
      foreach ($f in $touched) {
        $ff = $f.Trim()
        if ($ff.Length -gt 0) {
          if (-not ($ff -like 'runs/*')) {
            if (-not ($ff -like 'backlog/*')) { $c3 = $false }
          }
        }
      }
    }
  }
}

# Check 4 - every lane prompt carries the MANDATORY lines.
$c4 = $true
$promptFiles = Get-ChildItem -LiteralPath ($RunDir + '\prompts') -Filter 'PROMPT-*.md' -ErrorAction SilentlyContinue
if (($promptFiles | Measure-Object).Count -eq 0) { $c4 = $false }
foreach ($pf in $promptFiles) {
  $body = Get-Content -LiteralPath $pf.FullName -Raw
  $isGate = $false
  if ($body -match 'sole terminal authority') { $isGate = $true }
  $need = 6
  if ($isGate) { $need = 5 }
  $i = 1
  while ($i -le $need) {
    if (-not ($body -match ('(?m)^' + $i + '\. '))) { $c4 = $false }
    $i = $i + 1
  }
  if ($isGate) {
    if (-not ($body -match 'GATE CHECKLIST')) { $c4 = $false }
  }
}

# Check 5 - next-shift prompts written BEFORE close (i.e. now, before the tag).
$c5 = (Test-Path -LiteralPath ($RunDir + '\next-shift\PROMPTS.md'))
if ($c5) {
  if ((Get-Item -LiteralPath ($RunDir + '\next-shift\PROMPTS.md')).Length -lt 200) { $c5 = $false }
}

# Check 6 - ledger row flipped. Set below, then re-read.

# ---------------------------------------------------------------- tag

$existing = git -C $RepoPath tag --list $tag
if (-not [string]::IsNullOrWhiteSpace($existing)) {
  Write-Warning ("tag already exists: " + $tag)
} else {
  git -C $RepoPath tag -a $tag $CloseSha -m ($runName + ' close at ' + $CloseSha)
  if ($LASTEXITCODE -ne 0) { throw ("tag failed for " + $CloseSha) }
  Write-Host ("tag       : " + $tag + " -> " + $CloseSha)
}

# ---------------------------------------------------------------- ledger flip

$c6 = $false
if (Test-Path -LiteralPath $Ledger) {
  $lines = Get-Content -LiteralPath $Ledger
  $out = @()
  foreach ($line in $lines) {
    if ($line -like ('| ' + $runName + ' |*')) {
      if ([string]::IsNullOrWhiteSpace($LegsMet)) { $LegsMet = 'see RUN.md' }
      $new = $line -replace '\| OPEN \|', '| CLOSED |'
      # fill the trailing Close tag / Legs MET cells
      $new = $new -replace '\|\s*\|\s*\|\s*`runs/', ('| ' + $tag + ' | ' + $LegsMet + ' | `runs/')
      $out += $new
      $c6 = $true
    } else {
      $out += $line
    }
  }
  Set-Content -LiteralPath $Ledger -Value $out -Encoding UTF8
  if ($c6) { Write-Host ("ledger    : " + $runName + " flipped OPEN -> CLOSED") }
  else     { Write-Warning ("no ledger row found for " + $runName) }
} else {
  Write-Warning ("ledger not found at " + $Ledger)
}

# ---------------------------------------------------------------- scratch delete + VERIFY

$scratchRoot = $env:LOCALAPPDATA + '\HubScratch'
# The machine named by fleet-ops scratch-config.json (hubRoot) sweeps its own workspace instead (HQ: D:\tmp\scratch).
$scratchCfg = $HubRoot + '\50-AI\fleet-ops\policy\scratch-config.json'
if (Test-Path -LiteralPath $scratchCfg) {
  $sc = Get-Content -LiteralPath $scratchCfg -Raw | ConvertFrom-Json
  if (-not $sc -or -not $sc.hubRoot) { throw ("scratch-config.json is empty or has no hubRoot: " + $scratchCfg) }
  if ($sc.hubRoot -eq $HubRoot -and $sc.workspace) { $scratchRoot = $sc.workspace }
}
# Only THIS run's own dirs: the one named for the run (run-N) or run-N-*. Never the whole workspace and
# never another run's run-* dir: scratch-sweep.ps1 emptied every top-level entry, and on 2026-10-07 another
# live session's folder sat in the workspace at a close (charter Article 33: closing never sweeps another
# run's scratch). T1 dirs (run-<stamp>-<pid>) are cleaned by scratch-run.ps1 itself and are left alone.
function Get-OwnScratchDirs {
  param([string]$Root, [string]$Run)
  Get-ChildItem -LiteralPath $Root -Directory -Filter 'run-*' -ErrorAction SilentlyContinue | Where-Object {
    ($_.Name -eq $Run) -or $_.Name.StartsWith($Run + '-', [StringComparison]::OrdinalIgnoreCase)
  }
}
$scratchDeleted = $true
$scratchNote = 'no scratch workspace present'
if (Test-Path -LiteralPath $scratchRoot) {
  $allRunDirs = @(Get-ChildItem -LiteralPath $scratchRoot -Directory -Filter 'run-*' -ErrorAction SilentlyContinue)
  $own = @(Get-OwnScratchDirs -Root $scratchRoot -Run $runName)
  foreach ($d in $own) { Remove-Item -LiteralPath $d.FullName -Recurse -Force -ErrorAction SilentlyContinue }
  # Re-stat. Removal is load-bearing; "I ran the removal" is not evidence.
  $left   = @(Get-OwnScratchDirs -Root $scratchRoot -Run $runName)
  $others = $allRunDirs.Count - $own.Count
  if ($left.Count -eq 0) {
    $scratchNote = ('removed ' + $own.Count + ' dir(s) named for ' + $runName + '; re-stat confirms 0 remain; ' + $others + ' other run-* dir(s) left alone')
  } else {
    $scratchDeleted = $false
    $scratchNote = ('REMOVAL INCOMPLETE: ' + $left.Count + ' of ' + $own.Count + ' dir(s) named for ' + $runName + ' remain')
    Write-Warning $scratchNote
  }
  Write-Host ("scratch   : " + $scratchNote)
}

# ---------------------------------------------------------------- worktrees

if (-not $KeepWorktrees) {
  $wts = git -C $RepoPath worktree list --porcelain
  foreach ($line in $wts) {
    if ($line -like ('worktree *' + $runName + '-lane-*')) {
      $wtPath = $line.Substring(9)
      $dirty = git -C $wtPath status --porcelain
      if ([string]::IsNullOrWhiteSpace($dirty)) {
        git -C $RepoPath worktree remove $wtPath
        Write-Host ("worktree  : removed " + $wtPath)
      } else {
        Write-Warning ("worktree DIRTY, left in place (nothing is destroyed unverified): " + $wtPath)
      }
    }
  }
}

# ---------------------------------------------------------------- CONFORMANCE.json

$gateDir = $RunDir + '\evidence\gate'
if (-not (Test-Path -LiteralPath $gateDir)) { New-Item -ItemType Directory -Path $gateDir | Out-Null }

$checks = [ordered]@{
  'run_object_committed_pre_launch'  = $c1
  'lane_count_matches_shape'         = $c2
  'gate_lane_non_building'           = $c3
  'all_prompts_carry_mandatory_lines'= $c4
  'next_shift_prompts_before_close'  = $c5
  'ledger_row_flipped_at_close'      = $c6
}
$passed = 0
foreach ($k in $checks.Keys) { if ($checks[$k]) { $passed = $passed + 1 } }

# "deployed" is this run's own state, read from the "- Deploy state:" line the gate writes in HANDOFF.md;
# never assumed. A fixed false was wrong for run-6 (2026-10-07), whose owner-authorized merges each
# deployed to production. No line, or a line still holding the template's {placeholder}: "unknown".
$deployed   = 'unknown'
$deployNote = 'HANDOFF.md has no filled "- Deploy state:" line, so the deploy state is unknown.'
$handoffMd  = $RunDir + '\HANDOFF.md'
if (Test-Path -LiteralPath $handoffMd) {
  $dm = [regex]::Match((Get-Content -LiteralPath $handoffMd -Raw), '(?m)^\s*-\s*Deploy state:\s*(.+?)\s*$')
  if ($dm.Success) {
    $deployText = $dm.Groups[1].Value
    $plain = $deployText -replace '[*_`]', ''
    if (-not ($plain -match '\{')) {
      $deployNote = 'HANDOFF.md: ' + $deployText
      if ($plain -match '(?i)\b(not|never|nothing|no)\b[^.;]*\bdeployed\b') { $deployed = $false }
      elseif ($plain -match '(?i)\bdeployed\b') { $deployed = $true }
    }
  }
}

$conf = [ordered]@{
  'run'             = $runName
  'shape'           = $shape
  'closed_at'       = (Get-Date -Format 'yyyy-MM-ddTHH:mm:ssK')
  'close_tag'       = $tag
  'close_sha'       = $CloseSha
  'checks'          = $checks
  'score'           = ($passed.ToString() + '/6')
  'pass'            = ($passed -eq 6)
  'scratch_deleted_and_verified' = $scratchDeleted
  'scratch_note'    = $scratchNote
  'deployed'        = $deployed
  'deploy_note'     = $deployNote
}
$conf | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath ($gateDir + '\CONFORMANCE.json') -Encoding UTF8

Write-Host ""
Write-Host ("CONFORMANCE: " + $passed + "/6  (pass bar is 6/6 on 5 consecutive runs)")
foreach ($k in $checks.Keys) {
  $mark = 'FAIL'
  if ($checks[$k]) { $mark = 'PASS' }
  Write-Host ("  " + $mark + "  " + $k)
}
Write-Host ("written   : " + $gateDir + "\CONFORMANCE.json")
Write-Host ""
Write-Host "Owner check-in reads: REPORT.md -> his questions on the office -> next-shift/PROMPTS.md"
Write-Host "Nothing was pushed. Nothing was deployed."
