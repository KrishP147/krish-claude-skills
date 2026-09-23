# Installs dotfiles/CLAUDE.md as your global ~/.claude/CLAUDE.md.
#   merge   - appends it to your existing CLAUDE.md (creates one if you don't have one)
#   replace - overwrites/creates ~/.claude/CLAUDE.md from this repo's copy
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("merge", "replace")]
    [string]$Mode
)
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$src = Join-Path $repoRoot "dotfiles\CLAUDE.md"
$dest = if ($env:CLAUDE_MD_DEST) { $env:CLAUDE_MD_DEST } else { Join-Path $env:USERPROFILE ".claude\CLAUDE.md" }

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dest) | Out-Null

if ($Mode -eq "replace") {
    Copy-Item -Force $src $dest
    Write-Host "Replaced $dest with $src"
}
elseif (Test-Path $dest) {
    $existing = Get-Content $dest -Raw
    $incoming = Get-Content $src -Raw
    $stamp = Get-Date -Format "yyyy-MM-dd"
    "$existing`n`n<!-- appended from $src on $stamp -->`n`n$incoming" | Set-Content -Encoding utf8 $dest
    Write-Host "Merged $src into $dest (appended - check for duplicate sections)"
}
else {
    Copy-Item $src $dest
    Write-Host "No existing $dest - created from $src"
}
