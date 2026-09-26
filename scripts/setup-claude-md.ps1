# Installs dotfiles/CLAUDE.md as your global ~/.claude/CLAUDE.md.
#   merge   - appends it to your existing CLAUDE.md (creates one if you don't have one)
#   replace - overwrites/creates ~/.claude/CLAUDE.md from this repo's copy
# -Prefix <p> substitutes the <your-prefix> branch-prefix placeholder with <p>.
# Without -Prefix, the placeholder is left in place and a hint is printed.
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("merge", "replace")]
    [string]$Mode,
    [string]$Prefix = ""
)
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$src = Join-Path $repoRoot "dotfiles\CLAUDE.md"
$dest = if ($env:CLAUDE_MD_DEST) { $env:CLAUDE_MD_DEST } else { Join-Path $env:USERPROFILE ".claude\CLAUDE.md" }

# PS 5.1 has no [Text.Encoding]::UTF8's ::new() on all paths - New-Object
# with $false (no BOM) is the reliable spelling here.
$noBomUtf8 = New-Object Text.UTF8Encoding($false)

$incoming = [IO.File]::ReadAllText($src)
if ($Prefix) {
    $incoming = $incoming.Replace("<your-prefix>", $Prefix)
} else {
    Write-Warning "branch prefix left as <your-prefix> placeholder - pass -Prefix <p> to fill it in"
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dest) | Out-Null

if ($Mode -eq "replace") {
    [IO.File]::WriteAllText($dest, $incoming, $noBomUtf8)
    Write-Host "Replaced $dest with $src"
}
elseif (Test-Path $dest) {
    $existing = [IO.File]::ReadAllText($dest)
    $stamp = Get-Date -Format "yyyy-MM-dd"
    $merged = "$existing`n`n<!-- appended from $src on $stamp -->`n`n$incoming"
    [IO.File]::WriteAllText($dest, $merged, $noBomUtf8)
    Write-Host "Merged $src into $dest (appended - check for duplicate sections)"
}
else {
    [IO.File]::WriteAllText($dest, $incoming, $noBomUtf8)
    Write-Host "No existing $dest - created from $src"
}
