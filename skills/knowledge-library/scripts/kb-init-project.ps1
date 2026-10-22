param(
    [string]$ProjectRoot = (Get-Location).Path,
    [string]$LibraryRoot,
    [string]$AgentsPath,
    [switch]$NoBackup
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
        (Join-Path $ProjectRoot ".codex\model-implement\library"),
        (Join-Path $ProjectRoot "library"),
        (Get-Location).Path
    )

    foreach ($candidate in $candidates) {
        if ((Test-Path -LiteralPath $candidate) -and (Test-Path -LiteralPath (Join-Path $candidate (Get-RulesFileName)))) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    throw "LibraryRoot was not provided and no directory containing the knowledge rules entry file was found."
}

$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$LibraryRoot = Resolve-LibraryRoot $LibraryRoot
$RulesFileName = Get-RulesFileName
$RulesPath = Join-Path $LibraryRoot $RulesFileName

if ([string]::IsNullOrWhiteSpace($AgentsPath)) {
    $AgentsPath = Join-Path $ProjectRoot "AGENTS.md"
}

$agentsDir = Split-Path -Parent $AgentsPath
if (-not (Test-Path -LiteralPath $agentsDir)) {
    New-Item -ItemType Directory -Path $agentsDir | Out-Null
}

$begin = "<!-- BEGIN KNOWLEDGE_LIBRARY -->"
$end = "<!-- END KNOWLEDGE_LIBRARY -->"
$block = @"
$begin
## Knowledge Library

For code, SQL, component integration, style, review, maintenance, or reusable-knowledge tasks, first read:

$RulesPath

Then read only the matched library documents. Do not scan the entire library without a reason.

Use local search when the target document is unclear:

powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\kb-search.ps1" -LibraryRoot "$LibraryRoot" -Query "<keywords>"

Mandatory routing:
- Code tasks: follow the code-style route registered in the knowledge rules entry file.
- New modules, refactors, directory changes, or naming changes: follow the naming/structure route registered in the knowledge rules entry file.
- SQL, MyBatis, or database compatibility tasks: confirm the active database, then read the SQL compatibility route registered in the knowledge rules entry file.
- Component tasks: read the matched component README or entry document before implementation.
- After .codex/model-implement/reports/ or memory/ is supplemented and before entering the next stage, refresh model-context-rag; if reports/context-rag/index-status.json is blocked, do not rely on context search results.
- Missing facts: mark them as pending confirmation; do not guess business tables, fields, APIs, permissions, database dialects, or component contracts.
- Final answers should list the knowledge-library paths actually read.
$end
"@

if (Test-Path -LiteralPath $AgentsPath) {
    $content = [System.IO.File]::ReadAllText($AgentsPath, [System.Text.Encoding]::UTF8)
    if (-not $NoBackup) {
        $backupPath = "$AgentsPath.bak-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Copy-Item -LiteralPath $AgentsPath -Destination $backupPath -Force
    }
} else {
    $content = ""
}

$pattern = [regex]::Escape($begin) + "[\s\S]*?" + [regex]::Escape($end)
if ([regex]::IsMatch($content, $pattern)) {
    $newContent = [regex]::Replace($content, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $block })
} elseif ([string]::IsNullOrWhiteSpace($content)) {
    $newContent = $block + "`r`n"
} else {
    $newContent = $content.TrimEnd() + "`r`n`r`n" + $block + "`r`n"
}

[System.IO.File]::WriteAllText($AgentsPath, $newContent, [System.Text.UTF8Encoding]::new($false))
Write-Host "Updated AGENTS.md knowledge-library block: $AgentsPath"
