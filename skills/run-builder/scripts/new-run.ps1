<#
.SYNOPSIS
  Scaffold a run object for /run-builder. Windows PowerShell 5.1 safe (no &&, no ternary).

.DESCRIPTION
  Resolves the Hub root and the code zone AT RUNTIME (never hardcoded), scaffolds
  <repo>/runs/run-NN/, provisions one git worktree per building lane, creates the run-NN comms
  channel, appends the OPEN ledger row, and makes the prep commit.

  It does NOT launch lanes. The owner pastes.

.EXAMPLE
  .\new-run.ps1 -Shape ABC -Theme 'portal polish' -Shift night -Repo barkey-command-center
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][ValidateSet('AB','ABC','ABCD','ABCDE')][string]$Shape,
  [Parameter(Mandatory=$true)][string]$Theme,
  [Parameter(Mandatory=$true)][ValidateSet('night','morning','afternoon','evening')][string]$Shift,
  [string]$Repo,
  [string]$RepoPath,
  [string]$StopAt,
  [switch]$SharedTree,
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------- hub resolution

function Resolve-HubRoot {
  # String concat, not Join-Path: a missing drive must not throw.
  $candidates = @('D:\Hub', 'C:\Hub')
  foreach ($c in $candidates) {
    $marker = $c + '\CLAUDE.md'
    if (Test-Path -LiteralPath $marker) { return $c }
  }
  throw "Hub root not found. Probed D:\Hub\CLAUDE.md then C:\Hub\CLAUDE.md; neither exists."
}

function Resolve-CodeZone {
  param([string]$HubRoot)
  # HQ uses 20-Coding\Projects; ENGINE/FIELD use 20-Coding\Active. Two things differ
  # between machines, not one. Fail loudly rather than fall through silently.
  $zones = @(($HubRoot + '\20-Coding\Projects'), ($HubRoot + '\20-Coding\Active'))
  foreach ($z in $zones) {
    if (Test-Path -LiteralPath $z) { return $z }
  }
  throw ("Code zone not found under " + $HubRoot + ". Probed 20-Coding\Projects then 20-Coding\Active; neither exists.")
}

$HubRoot  = Resolve-HubRoot
$CodeZone = Resolve-CodeZone -HubRoot $HubRoot
Write-Host ("hub root  : " + $HubRoot)
Write-Host ("code zone : " + $CodeZone)

$FleetOps  = $HubRoot + '\50-AI\fleet-ops'
$Ledger    = $FleetOps + '\runs\LEDGER.md'
$ScratchRun = $FleetOps + '\policy\scratch-run.ps1'
if (-not (Test-Path -LiteralPath $ScratchRun)) {
  throw ("scratch-run.ps1 not found at " + $ScratchRun + ". The scratch policy is canonical; refusing to build a run that cannot test cleanly.")
}

# ---------------------------------------------------------------- repo resolution

if ([string]::IsNullOrWhiteSpace($RepoPath)) {
  if ([string]::IsNullOrWhiteSpace($Repo)) {
    throw "Supply -Repo <name> (resolved under the code zone) or -RepoPath <absolute path>."
  }
  $RepoPath = $CodeZone + '\' + $Repo
}
if (-not (Test-Path -LiteralPath ($RepoPath + '\.git'))) {
  throw ("Not a git repo: " + $RepoPath)
}
if ([string]::IsNullOrWhiteSpace($Repo)) { $Repo = Split-Path -Leaf $RepoPath }

# ---------------------------------------------------------------- shape -> lanes

$laneMap = @{
  'AB'    = @('a','b')
  'ABC'   = @('a','b','c')
  'ABCD'  = @('a','b','c','d')
  'ABCDE' = @('a','b','c','d','e')
}
$lanes    = $laneMap[$Shape]
$gateLane = $lanes[-1]
$builders = @()
foreach ($l in $lanes) { if ($l -ne $gateLane) { $builders += $l } }

# Concurrency cap: D: is a spinning HDD and multi-lane runs thrash it.
if ($builders.Count -gt 4) {
  throw ("Concurrency cap is 4 building lanes on HQ; shape " + $Shape + " asks for " + $builders.Count + ".")
}

# Isolation. Worktrees are the default. The shared-tree exception is AB/ABC only, and only
# when the lanes share one running dev service. ABCD/ABCDE are ALWAYS worktrees.
$isolation = 'worktrees'
if ($SharedTree) {
  if ($Shape -eq 'AB' -or $Shape -eq 'ABC') {
    $isolation = 'shared-tree'
    Write-Warning "shared-tree: the Â§7 shared-index mitigations are now load-bearing, not belt-and-suspenders."
  } else {
    throw ("-SharedTree is legal only for AB and ABC. " + $Shape + " is always worktrees.")
  }
}

# ---------------------------------------------------------------- run number

$runsDir = $RepoPath + '\runs'
if (-not (Test-Path -LiteralPath $runsDir)) { New-Item -ItemType Directory -Path $runsDir | Out-Null }

$maxN = 0
Get-ChildItem -LiteralPath $runsDir -Directory -Filter 'run-*' -ErrorAction SilentlyContinue | ForEach-Object {
  $tail = $_.Name.Substring(4)
  $n = 0
  if ([int]::TryParse($tail, [ref]$n)) {
    if ($n -gt $maxN) { $maxN = $n }
  }
}
$NN = $maxN + 1
$runName = 'run-' + $NN
$runDir  = $runsDir + '\' + $runName

if (Test-Path -LiteralPath $runDir) { throw ($runDir + " already exists.") }

if ([string]::IsNullOrWhiteSpace($StopAt)) {
  $defaults = @{ 'night'='08:00'; 'morning'='11:00'; 'afternoon'='17:00'; 'evening'='22:00' }
  $StopAt = $defaults[$Shift]
}

Write-Host ""
Write-Host ("run       : " + $runName)
Write-Host ("shape     : " + $Shape + "  lanes=" + ($lanes -join ',') + "  gate=" + $gateLane)
Write-Host ("shift     : " + $Shift + "   stop-at=" + $StopAt)
Write-Host ("isolation : " + $isolation)
Write-Host ("repo      : " + $RepoPath)

if ($DryRun) {
  Write-Host ""
  Write-Host "DRY RUN - nothing written."
  return
}

# ---------------------------------------------------------------- scaffold

$dirs = @($runDir, ($runDir + '\prompts'), ($runDir + '\queue'), ($runDir + '\evidence'),
          ($runDir + '\evidence\gate'), ($runDir + '\next-shift'))
foreach ($l in $lanes) { $dirs += ($runDir + '\evidence\' + $l) }
foreach ($d in $dirs) {
  if (-not (Test-Path -LiteralPath $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
}

# .gitkeep so the empty evidence/next-shift dirs survive the prep commit
foreach ($d in $dirs) {
  $keep = $d + '\.gitkeep'
  if (-not (Test-Path -LiteralPath $keep)) { New-Item -ItemType File -Path $keep | Out-Null }
}

$skillDir = Split-Path -Parent $PSScriptRoot
$tmplDir  = $skillDir + '\templates'

# RUN.md, HANDOFF.md, LEDGER-ROW.md from templates; the caller (the skill) fills the {â€¦}.
Copy-Item -LiteralPath ($tmplDir + '\RUN.md.tmpl')     -Destination ($runDir + '\RUN.md')
Copy-Item -LiteralPath ($tmplDir + '\HANDOFF.md.tmpl') -Destination ($runDir + '\HANDOFF.md')

foreach ($l in $lanes) {
  $q = $runDir + '\queue\' + $l + '.md'
  if (-not (Test-Path -LiteralPath $q)) {
    Set-Content -LiteralPath $q -Value ("# lane " + $l.ToUpper() + " queue - run-" + $NN + " (FIXED; no lane invents work)") -Encoding UTF8
  }
}

Write-Host "scaffold  : written"

# ---------------------------------------------------------------- worktrees

if ($isolation -eq 'worktrees') {
  foreach ($l in $builders) {
    $branch = 'run-' + $NN + '/lane-' + $l
    $wt     = $RepoPath + '-' + $runName + '-lane-' + $l
    if (Test-Path -LiteralPath $wt) {
      Write-Warning ("worktree already exists, skipping: " + $wt)
    } else {
      git -C $RepoPath worktree add -b $branch $wt
      if ($LASTEXITCODE -ne 0) { throw ("worktree add failed for lane " + $l) }
      Write-Host ("worktree  : " + $wt + "  (" + $branch + ")")
    }
  }
} else {
  Write-Host "worktree  : skipped (shared-tree; lanes coordinate via comms.py path claims)"
}

# ---------------------------------------------------------------- comms channel

$comms = $RepoPath + '\.claude\comms\comms.py'
if (Test-Path -LiteralPath $comms) {
  foreach ($l in $lanes) {
    python $comms post ('run-' + $NN) ('lane-' + $l) --subject ("STATUS run-" + $NN + " channel open: lane-" + $l) ("lane-" + $l + " registered on run-" + $NN + " (" + $Shape + ", " + $Shift + ").")
    if ($LASTEXITCODE -ne 0) {
      Write-Warning ("comms registration failed for lane-" + $l + ". Channel/ACL may need a comms.py roster entry - route to Cole before launch.")
    }
  }
  Write-Host ("comms     : channel run-" + $NN + " seeded for " + ($lanes -join ','))
} else {
  Write-Warning ("comms.py not found at " + $comms + " - the run has no message bus. Do not launch until this resolves.")
}

# ---------------------------------------------------------------- ledger row (OPEN)

if (-not (Test-Path -LiteralPath $Ledger)) {
  $hdr = @(
    '# Fleet runs ledger',
    '',
    '| Run | Shape | Shift | Date | Repo | Theme | Status | Prep SHA | Close tag | Legs MET | Artifacts |',
    '|---|---|---|---|---|---|---|---|---|---|---|'
  )
  Set-Content -LiteralPath $Ledger -Value $hdr -Encoding UTF8
}
$today = Get-Date -Format 'yyyy-MM-dd'
$row = '| ' + $runName + ' | ' + $Shape + ' | ' + $Shift + ' | ' + $today + ' | ' + $Repo + ' | ' + $Theme + ' | OPEN | PENDING |  |  | `runs/' + $runName + '/` |'
Add-Content -LiteralPath $Ledger -Value $row -Encoding UTF8
Write-Host ("ledger    : OPEN row appended to " + $Ledger)

# ---------------------------------------------------------------- prep commit

# Explicit pathspec, -F message file, judged by `git log -1` grep of the marker. Never by
# exit code. One retry maximum. Never clear a peer index.lock.
$marker  = '[' + $runName + '-prep]'
$msgFile = [System.IO.Path]::GetTempFileName()
$msgBody = @(
  ($runName + ' prep: ' + $Shape + ' ' + $Theme + ' ' + $Shift),
  '',
  $marker,
  ('Run object committed before launch. Lanes: ' + ($lanes -join ',') + '; gate=' + $gateLane + '; isolation=' + $isolation + '; stop-at=' + $StopAt + '.')
)
Set-Content -LiteralPath $msgFile -Value $msgBody -Encoding UTF8

$pathspec = 'runs/' + $runName
git -C $RepoPath add -- $pathspec
git -C $RepoPath ls-files --error-unmatch -- ($pathspec + '/RUN.md') | Out-Null
if ($LASTEXITCODE -ne 0) { throw "prep commit aborted: RUN.md was not staged." }

git -C $RepoPath commit -F $msgFile -- $pathspec | Out-Null
$landed = git -C $RepoPath log -1 --pretty=%B
$prepSha = ''
if (([string]$landed).Contains($marker)) {
  $prepSha = (git -C $RepoPath rev-parse --short HEAD)
} else {
  Write-Warning "prep commit not detected in git log -1. Retrying once."
  git -C $RepoPath commit -F $msgFile -- $pathspec | Out-Null
  $landed = git -C $RepoPath log -1 --pretty=%B
  if (([string]$landed).Contains($marker)) {
    $prepSha = (git -C $RepoPath rev-parse --short HEAD)
  } else {
    Remove-Item -LiteralPath $msgFile -Force
    throw "prep commit did not land after one retry. Do NOT launch: the run object must be committed before the owner pastes."
  }
}
Remove-Item -LiteralPath $msgFile -Force

# Backfill the prep SHA into the ledger row.
$ledgerText = Get-Content -LiteralPath $Ledger
$ledgerText = $ledgerText -replace ('\| ' + [regex]::Escape($runName) + ' \| .*\| OPEN \| PENDING \|'), $row.Replace('PENDING', $prepSha)
Set-Content -LiteralPath $Ledger -Value $ledgerText -Encoding UTF8

Write-Host ("prep      : committed " + $prepSha + " " + $marker)
Write-Host ""
Write-Host "NEXT: the skill fills RUN.md + queue/*.md + prompts/, then the OWNER pastes."
Write-Host "This script does not launch lanes."
