param(
    [Parameter(Mandatory = $true, Position = 0)][string]$Query,
    [string]$LibraryRoot,
    [int]$Top = 8,
    [switch]$IncludeDeprecated,
    [switch]$ShowText
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

function Get-Tokens {
    param([string]$Text)
    $matches = [regex]::Matches($Text, "[A-Za-z0-9_\-\.]+|[\p{IsCJKUnifiedIdeographs}]{2,}")
    $tokens = New-Object System.Collections.Generic.List[string]
    foreach ($match in $matches) {
        $value = $match.Value.Trim().ToLowerInvariant()
        if ($value.Length -ge 2) {
            $tokens.Add($value)
        }
    }
    return @($tokens.ToArray() | Select-Object -Unique)
}

function Count-Contains {
    param(
        [string]$Haystack,
        [string]$Needle
    )
    if ([string]::IsNullOrWhiteSpace($Needle)) {
        return 0
    }
    return ([regex]::Matches($Haystack, [regex]::Escape($Needle))).Count
}

$LibraryRoot = Resolve-LibraryRoot $LibraryRoot
$chunksPath = Join-Path $LibraryRoot ".ai\chunks.jsonl"
if (-not (Test-Path -LiteralPath $chunksPath)) {
    throw "Index not found: $chunksPath. Run kb-index.ps1 first."
}

$tokens = Get-Tokens $Query
if ($tokens.Count -eq 0) {
    throw "Query has no searchable terms."
}

$results = New-Object System.Collections.Generic.List[object]
$lines = Get-Content -LiteralPath $chunksPath -Encoding UTF8
foreach ($line in $lines) {
    if ([string]::IsNullOrWhiteSpace($line)) {
        continue
    }

    $chunk = $line | ConvertFrom-Json
    if (($chunk.status -eq "deprecated") -and (-not $IncludeDeprecated)) {
        continue
    }

    $pathLower = ([string]$chunk.path).ToLowerInvariant()
    $titleLower = ([string]$chunk.title).ToLowerInvariant()
    $headingLower = ([string]$chunk.heading).ToLowerInvariant()
    $textLower = ([string]$chunk.text).ToLowerInvariant()
    $score = 0
    $hits = New-Object System.Collections.Generic.List[string]

    foreach ($token in $tokens) {
        $tokenScore = 0
        if ($pathLower.Contains($token)) { $tokenScore += 12 }
        if ($titleLower.Contains($token)) { $tokenScore += 10 }
        if ($headingLower.Contains($token)) { $tokenScore += 8 }
        $bodyCount = Count-Contains -Haystack $textLower -Needle $token
        if ($bodyCount -gt 0) { $tokenScore += [Math]::Min(10, $bodyCount * 2) }

        if ($tokenScore -gt 0) {
            $score += $tokenScore
            $hits.Add($token)
        }
    }

    if ($chunk.status -eq "deprecated") {
        $score = [Math]::Floor($score * 0.4)
    }

    if ($score -gt 0) {
        $snippet = ([string]$chunk.text).Replace("`r", " ").Replace("`n", " ")
        if ($snippet.Length -gt 220) {
            $snippet = $snippet.Substring(0, 220) + "..."
        }

        $results.Add([PSCustomObject]@{
            score = $score
            path = $chunk.path
            heading = $chunk.heading
            title = $chunk.title
            status = $chunk.status
            hits = (@($hits.ToArray() | Select-Object -Unique) -join ", ")
            snippet = $snippet
            text = $chunk.text
        })
    }
}

$ranked = @($results | Sort-Object -Property score -Descending | Select-Object -First $Top)
if ($ranked.Count -eq 0) {
    Write-Host "No matches."
    exit 0
}

$i = 0
foreach ($item in $ranked) {
    $i++
    Write-Host "[$i] score=$($item.score) status=$($item.status)"
    Write-Host "    path:    $($item.path)"
    Write-Host "    heading: $($item.heading)"
    Write-Host "    hits:    $($item.hits)"
    if ($ShowText) {
        Write-Host "    text:"
        Write-Host $item.text
    } else {
        Write-Host "    snippet: $($item.snippet)"
    }
    Write-Host ""
}
