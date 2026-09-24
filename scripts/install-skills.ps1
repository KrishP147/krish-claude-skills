# Installs every skill in this repo into ~/.claude/skills/ (personal, global
# across all repos/terminals). Safe to re-run - each skill is replaced fresh.
# Also copies agents/*.md and agents/hooks/ over ~/.claude/agents/; agents
# there that aren't in this repo are warned about, never deleted.
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$target = if ($env:CLAUDE_SKILLS_DIR) { $env:CLAUDE_SKILLS_DIR } else { Join-Path $env:USERPROFILE ".claude\skills" }
$agentsTarget = if ($env:CLAUDE_AGENTS_DIR) { $env:CLAUDE_AGENTS_DIR } else { Join-Path $env:USERPROFILE ".claude\agents" }

$pyCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pyCmd) { $pyCmd = Get-Command python3 -ErrorAction SilentlyContinue }

if ($pyCmd) {
    & $pyCmd.Source (Join-Path $repoRoot "scripts\lint.py")
    if ($LASTEXITCODE -ne 0) {
        Write-Error "lint failed - aborting install"
        exit 1
    }
} else {
    Write-Warning "python/python3 not found on PATH, skipping lint"
}

New-Item -ItemType Directory -Force -Path $target | Out-Null
New-Item -ItemType Directory -Force -Path $agentsTarget | Out-Null

$installed = @()
Get-ChildItem -Path $repoRoot -Recurse -Filter "SKILL.md" -Depth 2 | ForEach-Object {
    $skillDir = $_.Directory
    $name = $skillDir.Name
    $dest = Join-Path $target $name
    if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
    Copy-Item -Recurse $skillDir.FullName $dest
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
}

Write-Host "Installed $($installed.Count) skill(s) to $target :"
$installed | ForEach-Object { Write-Host "  - $_" }

Write-Host "Installed $($installedAgents.Count) agent(s) to $agentsTarget :"
$installedAgents | ForEach-Object { Write-Host "  - $_" }

$agentsSrc = Join-Path $repoRoot "agents"
$stale = @(Get-ChildItem -Path $agentsTarget -Filter "*.md" -File | Where-Object {
    $_.Name -ne "README.md" -and -not (Test-Path (Join-Path $agentsSrc $_.Name))
} | ForEach-Object { $_.Name })
if ($stale.Count -gt 0) {
    Write-Warning "stale agent(s) not in repo, remove manually: $($stale -join ', ')"
}
