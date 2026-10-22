param(
    [Parameter(Mandatory = $true)][string]$Path,
    [string]$ReplacedBy,
    [string]$Reason = "Replaced or no longer recommended.",
    [switch]$NoBackup
)

$ErrorActionPreference = "Stop"

$Path = (Resolve-Path -LiteralPath $Path).Path
$date = Get-Date -Format "yyyy-MM-dd"
$content = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)

$block = @"
---
status: deprecated
deprecated_at: $date
replaced_by: $ReplacedBy
reason: $Reason
---

"@

if (-not $NoBackup) {
    Copy-Item -LiteralPath $Path -Destination "$Path.bak-$(Get-Date -Format 'yyyyMMdd-HHmmss')" -Force
}

if ($content -match "^\s*---\s*`r?`n[\s\S]*?status\s*:\s*deprecated[\s\S]*?---\s*`r?`n") {
    $newContent = [regex]::Replace($content, "^\s*---\s*`r?`n[\s\S]*?status\s*:\s*deprecated[\s\S]*?---\s*`r?`n\s*", $block, 1)
} else {
    $newContent = $block + $content.TrimStart()
}

[System.IO.File]::WriteAllText($Path, $newContent, [System.Text.UTF8Encoding]::new($false))
Write-Host "Deprecated: $Path"
