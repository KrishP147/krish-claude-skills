# Installs every skill in this repo into ~/.claude/skills/ (personal, global
# across all repos/terminals). Safe to re-run - each of our own skill dirs is
# replaced fresh; a same-named dir NOT installed by this repo (no marker
# file) is left alone unless -Force. Also copies agents/*.md and
# agents/hooks/ over ~/.claude/agents/; agents there that aren't in this
# repo are warned about, never deleted.
param(
    [switch]$NoLint,
    [switch]$Force
)
$ErrorActionPreference = "Stop"

$Marker = ".from-krishp147-skills"

$repoRoot = Split-Path -Parent $PSScriptRoot
$target = if ($env:CLAUDE_SKILLS_DIR) { $env:CLAUDE_SKILLS_DIR } else { Join-Path $env:USERPROFILE ".claude\skills" }
$agentsTarget = if ($env:CLAUDE_AGENTS_DIR) { $env:CLAUDE_AGENTS_DIR } else { Join-Path $env:USERPROFILE ".claude\agents" }

function Get-WorkingPython3 {
    # first candidate that actually runs Python 3 (skips e.g. the Windows
    # Store python stub, which sits on PATH under WindowsApps but refuses
    # to run code)
    $candidates = @(
        @{ Cmd = "python"; Args = @() },
        @{ Cmd = "python3"; Args = @() },
        @{ Cmd = "py"; Args = @("-3") }
    )
    foreach ($c in $candidates) {
        $cmd = Get-Command $c.Cmd -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }
        if ($cmd.Source -like "*WindowsApps*") { continue }
        try {
            & $cmd.Source @($c.Args) -c "import sys;sys.exit(0 if sys.version_info[0]==3 else 1)" 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) {
                return [PSCustomObject]@{ Path = $cmd.Source; Args = $c.Args }
            }
        } catch {
            continue
        }
    }
    return $null
}

$py = Get-WorkingPython3
if ($py) {
    # lint WARN lines go to stderr; under "Stop", PS 5.1 turns redirected
    # native stderr into a terminating error, so relax it for this call.
    $ErrorActionPreference = "Continue"
    & $py.Path @($py.Args) (Join-Path $repoRoot "scripts\lint.py")
    $lintExit = $LASTEXITCODE
    $ErrorActionPreference = "Stop"
    if ($lintExit -ne 0) {
        Write-Error "lint failed - aborting install"
        exit 1
    }
} elseif ($NoLint) {
    Write-Warning "no working python 3 found, skipping lint (-NoLint)"
} else {
    Write-Error "no working python 3 found on PATH (checked python, python3, py -3). Install Python 3, or pass -NoLint to skip the lint step."
    exit 1
}

New-Item -ItemType Directory -Force -Path $target | Out-Null
New-Item -ItemType Directory -Force -Path $agentsTarget | Out-Null

$templatesPath = Join-Path $repoRoot "templates"
$installed = @()
$skippedForeign = @()
Get-ChildItem -Path $repoRoot -Recurse -Filter "SKILL.md" -Depth 2 | Where-Object {
    -not $_.FullName.StartsWith($templatesPath + [System.IO.Path]::DirectorySeparatorChar)
} | ForEach-Object {
    $skillDir = $_.Directory
    $name = $skillDir.Name
    $dest = Join-Path $target $name
    if ((Test-Path $dest) -and -not (Test-Path (Join-Path $dest $Marker)) -and -not $Force) {
        Write-Warning "$dest exists and wasn't installed by this repo, skipping (use -Force to replace)"
        $skippedForeign += $name
        return
    }
    if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
    Copy-Item -Recurse $skillDir.FullName $dest
    Get-ChildItem -Path $dest -Recurse -Filter "__pycache__" -Directory -ErrorAction SilentlyContinue |
        ForEach-Object { Remove-Item -Recurse -Force $_.FullName }
    New-Item -ItemType File -Force -Path (Join-Path $dest $Marker) | Out-Null
    $installed += $name
}

$installedAgents = @()
Get-ChildItem -Path (Join-Path $repoRoot "agents") -Filter "*.md" -File | Where-Object { $_.Name -ne "README.md" } | ForEach-Object {
    $dest = Join-Path $agentsTarget $_.Name
    Copy-Item -Force $_.FullName $dest
    $installedAgents += [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
}

$hooksSrc = Join-Path $repoRoot "agents\hooks"
$hooksDest = Join-Path $agentsTarget "hooks"
if (Test-Path $hooksSrc) {
    New-Item -ItemType Directory -Force -Path $hooksDest | Out-Null
    Copy-Item -Force -Recurse (Join-Path $hooksSrc "*") $hooksDest
    Get-ChildItem -Path $hooksDest -Recurse -Filter "__pycache__" -Directory -ErrorAction SilentlyContinue |
        ForEach-Object { Remove-Item -Recurse -Force $_.FullName }
}

Write-Host "Installed $($installed.Count) skill(s) to $target :"
$installed | ForEach-Object { Write-Host "  - $_" }

if ($skippedForeign.Count -gt 0) {
    Write-Warning "skipped $($skippedForeign.Count) foreign skill dir(s) without marker (use -Force): $($skippedForeign -join ', ')"
}

Write-Host "Installed $($installedAgents.Count) agent(s) to $agentsTarget :"
$installedAgents | ForEach-Object { Write-Host "  - $_" }

$agentsSrc = Join-Path $repoRoot "agents"
$stale = @(Get-ChildItem -Path $agentsTarget -Filter "*.md" -File | Where-Object {
    $_.Name -ne "README.md" -and -not (Test-Path (Join-Path $agentsSrc $_.Name))
} | ForEach-Object { $_.Name })
if ($stale.Count -gt 0) {
    Write-Warning "stale agent(s) not in repo, remove manually: $($stale -join ', ')"
}

if ($skippedForeign.Count -gt 0) {
    exit 1
}
