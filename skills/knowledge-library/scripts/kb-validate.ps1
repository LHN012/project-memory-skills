param(
    [string]$LibraryRoot,
    [switch]$Strict
)

$ErrorActionPreference = "Stop"

function Get-RulesFileName {
    return ([string]([char]0x5B9A) + [string]([char]0x4E49) + [string]([char]0x89C4) + [string]([char]0x5219) + ".md")
}

function Resolve-LibraryRoot {
    param([string]$Path)

    if (-not [string]::IsNullOrWhiteSpace($Path)) {
        return (Resolve-Path -LiteralPath $Path).Path
    }

    $candidates = @(
        (Get-Location).Path,
        (Join-Path (Get-Location).Path "library"),
        (Join-Path (Get-Location).Path ".codex\model-implement\library"),
        (Join-Path $PSScriptRoot "..\..\..\model-implement\library")
    )

    foreach ($candidate in $candidates) {
        if ((Test-Path -LiteralPath $candidate) -and (Test-Path -LiteralPath (Join-Path $candidate (Get-RulesFileName)))) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    throw "LibraryRoot was not provided and no directory containing the knowledge rules entry file was found."
}

function Add-Issue {
    param(
        [System.Collections.Generic.List[object]]$Issues,
        [string]$Level,
        [string]$Message
    )
    $Issues.Add([PSCustomObject]@{ level = $Level; message = $Message })
}

$LibraryRoot = Resolve-LibraryRoot $LibraryRoot
$issues = New-Object System.Collections.Generic.List[object]

$rulesPath = Join-Path $LibraryRoot (Get-RulesFileName)
if (-not (Test-Path -LiteralPath $rulesPath)) {
    Add-Issue $issues "error" "Missing knowledge rules entry file."
}

$manifestPath = Join-Path $LibraryRoot ".ai\manifest.json"
$chunksPath = Join-Path $LibraryRoot ".ai\chunks.jsonl"
if (-not (Test-Path -LiteralPath $manifestPath)) {
    Add-Issue $issues "error" "Missing .ai/manifest.json. Run kb-index.ps1."
}
if (-not (Test-Path -LiteralPath $chunksPath)) {
    Add-Issue $issues "error" "Missing .ai/chunks.jsonl. Run kb-index.ps1."
}

if (Test-Path -LiteralPath $manifestPath) {
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($file in $manifest.files) {
        $source = Join-Path $LibraryRoot $file.path
        if (-not (Test-Path -LiteralPath $source)) {
            Add-Issue $issues "error" "Indexed source file no longer exists: $($file.path)"
            continue
        }

        $currentHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($currentHash -ne $file.hash) {
            Add-Issue $issues "warning" "Indexed hash is stale: $($file.path)"
        }
    }
}

$mdFiles = Get-ChildItem -LiteralPath $LibraryRoot -Recurse -File -Include "*.md" | Where-Object {
    $_.FullName -notmatch "[\\/]\.ai[\\/]" -and
    $_.FullName -notmatch "[\\/]\.codex[\\/]"
}

foreach ($md in $mdFiles) {
    $text = [System.IO.File]::ReadAllText($md.FullName, [System.Text.Encoding]::UTF8)
    $matches = [regex]::Matches($text, "\[[^\]]+\]\(([^)]+)\)")
    foreach ($match in $matches) {
        $target = $match.Groups[1].Value
        if ($target -match "^[a-zA-Z]+://") {
            continue
        }
        if ($target.StartsWith("#")) {
            continue
        }
        $clean = ($target -split "#")[0]
        if ([string]::IsNullOrWhiteSpace($clean)) {
            continue
        }
        if ([System.IO.Path]::IsPathRooted($clean)) {
            $resolved = $clean
        } else {
            $resolved = Join-Path (Split-Path -Parent $md.FullName) $clean
        }
        if (-not (Test-Path -LiteralPath $resolved)) {
            Add-Issue $issues "warning" "Possible broken markdown link in $($md.Name): $target"
        }
    }
}

if ($issues.Count -eq 0) {
    Write-Host "Knowledge library validation passed: $LibraryRoot"
    exit 0
}

foreach ($issue in $issues) {
    Write-Host "[$($issue.level)] $($issue.message)"
}

if (($issues | Where-Object { $_.level -eq "error" }).Count -gt 0) {
    exit 1
}
if ($Strict -and $issues.Count -gt 0) {
    exit 1
}
