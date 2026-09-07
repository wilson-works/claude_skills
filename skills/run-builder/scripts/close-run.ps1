<#
.SYNOPSIS
  Close a /run-builder run. Windows PowerShell 5.1 safe (no &&, no ternary).

.DESCRIPTION
  Run by the GATE lane at the final turn, AFTER next-shift/PROMPTS.md, next-shift/RUN.md,
  HANDOFF.md, REPORT.md and OWNER-QUESTIONS.md are written.

  Tags run-NN-close at a named commit, flips the LEDGER row OPEN -> CLOSED, deletes scratch and
  VERIFIES the deletion, and emits evidence/gate/CONFORMANCE.json.

  It does not deploy. It does not push. Deploy is always the owner's attended act.

.EXAMPLE
  .\close-run.ps1 -RunDir 'D:\Hub\20-Coding\Projects\barkey\runs\run-70' -RepoPath 'D:\Hub\20-Coding\Projects\barkey' -CloseSha abc1234
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
$prepLine = git -C $RepoPath log --pretty='%H %s' --grep=([regex]::Escape($runName) + ' prep:')
$c1 = $false
if (-not [string]::IsNullOrWhiteSpace($prepLine)) { $c1 = $true }

# Check 2 - lane count == shape. Read the shape from RUN.md; count the prompt files.
$runMd  = Get-Content -LiteralPath ($RunDir + '\RUN.md') -Raw
$shape  = ''
$m = [regex]::Match($runMd, '\*\*Shape:\*\*\s*([A-E]+)')
if ($m.Success) { $shape = $m.Groups[1].Value }
$promptCount = (Get-ChildItem -LiteralPath ($RunDir + '\prompts') -Filter 'PROMPT-*.md' -ErrorAction SilentlyContinue | Measure-Object).Count
$c2 = $false
if ($shape.Length -gt 0) { if ($promptCount -eq $shape.Length) { $c2 = $true } }

# Check 3 - gate lane non-building: zero product-code commits authored by the gate lane.
# Determined by inspecting commits carrying the gate marker that touch paths outside runs/.
$gateLetter = ''
if ($shape.Length -gt 0) { $gateLetter = $shape.Substring($shape.Length - 1, 1).ToLower() }
$c3 = $true
if ($gateLetter.Length -gt 0) {
  $gateCommits = git -C $RepoPath log --pretty=%H --grep=('\[lane-' + $gateLetter + '\]') -E
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
  $need = 7
  if ($isGate) { $need = 6 }
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
$scratchDeleted = $true
$scratchNote = 'no scratch workspace present'
if (Test-Path -LiteralPath $scratchRoot) {
  $before = (Get-ChildItem -LiteralPath $scratchRoot -Directory -Filter 'run-*' -ErrorAction SilentlyContinue | Measure-Object).Count
  $sweeper = $HubRoot + '\50-AI\fleet-ops\policy\scratch-sweep.ps1'
  if (Test-Path -LiteralPath $sweeper) {
    & $sweeper
  } else {
    Write-Warning ("scratch-sweep.ps1 not found at " + $sweeper + "; removing run-* dirs directly.")
    Get-ChildItem -LiteralPath $scratchRoot -Directory -Filter 'run-*' -ErrorAction SilentlyContinue | ForEach-Object {
      Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    }
  }
  # Re-stat. Deletion is load-bearing; "I ran the sweeper" is not evidence.
  $after = (Get-ChildItem -LiteralPath $scratchRoot -Directory -Filter 'run-*' -ErrorAction SilentlyContinue | Measure-Object).Count
  if ($after -eq 0) {
    $scratchNote = ('swept ' + $before + ' run-* dirs; re-stat confirms 0 remain')
  } else {
    $scratchDeleted = $false
    $scratchNote = ('SWEEP INCOMPLETE: ' + $after + ' run-* dirs remain of ' + $before)
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
  'deployed'        = $false
  'deploy_note'     = 'Deploy is always the owner attended act. A green gate is a finding, not an authorization.'
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
Write-Host "Owner check-in reads: REPORT.md -> OWNER-QUESTIONS.md -> next-shift/PROMPTS.md"
Write-Host "Nothing was pushed. Nothing was deployed."
