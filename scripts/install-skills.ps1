# Installs every skill in this repo into ~/.claude/skills/ (personal, global
# across all repos/terminals). Safe to re-run - each skill is replaced fresh.
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$target = if ($env:CLAUDE_SKILLS_DIR) { $env:CLAUDE_SKILLS_DIR } else { Join-Path $env:USERPROFILE ".claude\skills" }
New-Item -ItemType Directory -Force -Path $target | Out-Null

$installed = @()
Get-ChildItem -Path $repoRoot -Recurse -Filter "SKILL.md" -Depth 2 | ForEach-Object {
    $skillDir = $_.Directory
    $name = $skillDir.Name
    $dest = Join-Path $target $name
    if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
    Copy-Item -Recurse $skillDir.FullName $dest
    $installed += $name
}

Write-Host "Installed $($installed.Count) skill(s) to $target :"
$installed | ForEach-Object { Write-Host "  - $_" }
