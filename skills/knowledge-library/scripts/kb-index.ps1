param(
    [string]$LibraryRoot,
    [string]$OutDir,
    [string[]]$IncludeExtensions = @(".md", ".markdown", ".java", ".vue", ".js", ".ts", ".sql", ".xml", ".yaml", ".yml", ".properties"),
    [switch]$IncludeArchive,
    [switch]$IncludeDeprecated,
    [int]$MaxChunkChars = 6000
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

function Get-RelativePath {
    param(
        [Parameter(Mandatory = $true)][string]$Base,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $baseUri = [System.Uri]((Get-Item -LiteralPath $Base).FullName.TrimEnd("\") + "\")
    $pathUri = [System.Uri](Get-Item -LiteralPath $Path).FullName
    return [System.Uri]::UnescapeDataString($baseUri.MakeRelativeUri($pathUri).ToString()).Replace("/", "\")
}

function Test-ExcludedPath {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [switch]$IncludeArchive
    )

    $parts = $RelativePath -split "[\\/]+"
    $excluded = @(".ai", ".git", ".codex", "node_modules", "dist", "build", "target", ".idea", ".vscode")
    if (-not $IncludeArchive) {
        $excluded += "archive"
    }

    foreach ($part in $parts) {
        if ($excluded -contains $part) {
            return $true
        }
    }

    return $false
}

function Read-TextFile {
    param([string]$Path)
    return [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
}

function Get-DocStatus {
    param([string]$Text)

    $first = $Text.Substring(0, [Math]::Min($Text.Length, 1200))
    if ($first -match "(?im)^\s*status\s*:\s*deprecated\s*$") {
        return "deprecated"
    }
    return "active"
}

function Get-Title {
    param(
        [string]$Text,
        [string]$Fallback
    )

    foreach ($line in ($Text -split "`r?`n")) {
        if ($line -match "^\s*#\s+(.+?)\s*$") {
            return $Matches[1].Trim()
        }
    }

    return [System.IO.Path]::GetFileNameWithoutExtension($Fallback)
}

function Get-Headings {
    param([string]$Text)

    $headings = New-Object System.Collections.Generic.List[string]
    foreach ($line in ($Text -split "`r?`n")) {
        if ($line -match "^\s{0,3}(#{1,6})\s+(.+?)\s*$") {
            $headings.Add($Matches[2].Trim())
        }
    }
    return $headings.ToArray()
}

function Get-Keywords {
    param(
        [string]$RelativePath,
        [string]$Title,
        [string[]]$Headings,
        [string]$Text
    )

    $prefix = $Text.Substring(0, [Math]::Min($Text.Length, 2500))
    $joined = ((@($RelativePath, $Title) + $Headings) -join " ") + " " + $prefix
    $matches = [regex]::Matches($joined, "[A-Za-z][A-Za-z0-9_\-]{2,}|[\p{IsCJKUnifiedIdeographs}]{2,}")
    $set = [ordered]@{}

    foreach ($match in $matches) {
        $value = $match.Value.Trim()
        if ($value.Length -lt 2) {
            continue
        }
        $key = $value.ToLowerInvariant()
        if (-not $set.Contains($key)) {
            $set[$key] = $value
        }
        if ($set.Count -ge 80) {
            break
        }
    }

    return @($set.Values)
}

function Split-MarkdownChunks {
    param(
        [string]$Text,
        [string]$RelativePath,
        [string]$Title,
        [string]$Status,
        [int]$MaxChunkChars
    )

    $chunks = New-Object System.Collections.Generic.List[object]
    $lines = $Text -split "`r?`n"
    $currentHeading = $Title
    $currentLevel = 1
    $buffer = New-Object System.Collections.Generic.List[string]
    $index = 0

    function Add-Chunk {
        param(
            [System.Collections.Generic.List[string]]$Buffer,
            [System.Collections.Generic.List[object]]$Chunks,
            [ref]$IndexRef,
            [string]$Heading,
            [int]$Level
        )

        $body = (($Buffer.ToArray()) -join "`n").Trim()
        if ([string]::IsNullOrWhiteSpace($body)) {
            return
        }

        $start = 0
        while ($start -lt $body.Length) {
            $length = [Math]::Min($MaxChunkChars, $body.Length - $start)
            $piece = $body.Substring($start, $length).Trim()
            if (-not [string]::IsNullOrWhiteSpace($piece)) {
                $IndexRef.Value++
                $Chunks.Add([PSCustomObject]@{
                    id = "$RelativePath#$($IndexRef.Value)"
                    path = $RelativePath
                    title = $Title
                    heading = $Heading
                    level = $Level
                    status = $Status
                    text = $piece
                })
            }
            $start += $length
        }
    }

    foreach ($line in $lines) {
        if ($line -match "^\s{0,3}(#{1,6})\s+(.+?)\s*$") {
            Add-Chunk -Buffer $buffer -Chunks $chunks -IndexRef ([ref]$index) -Heading $currentHeading -Level $currentLevel
            $buffer.Clear()
            $currentLevel = $Matches[1].Length
            $currentHeading = $Matches[2].Trim()
        }
        $buffer.Add($line)
    }

    Add-Chunk -Buffer $buffer -Chunks $chunks -IndexRef ([ref]$index) -Heading $currentHeading -Level $currentLevel
    return $chunks.ToArray()
}

function Split-PlainChunks {
    param(
        [string]$Text,
        [string]$RelativePath,
        [string]$Title,
        [string]$Status,
        [int]$MaxChunkChars
    )

    $chunks = New-Object System.Collections.Generic.List[object]
    $start = 0
    $index = 0
    while ($start -lt $Text.Length) {
        $length = [Math]::Min($MaxChunkChars, $Text.Length - $start)
        $piece = $Text.Substring($start, $length).Trim()
        if (-not [string]::IsNullOrWhiteSpace($piece)) {
            $index++
            $chunks.Add([PSCustomObject]@{
                id = "$RelativePath#$index"
                path = $RelativePath
                title = $Title
                heading = $Title
                level = 1
                status = $Status
                text = $piece
            })
        }
        $start += $length
    }
    return $chunks.ToArray()
}

$LibraryRoot = Resolve-LibraryRoot $LibraryRoot
if ([string]::IsNullOrWhiteSpace($OutDir)) {
    $OutDir = Join-Path $LibraryRoot ".ai"
}

if (-not (Test-Path -LiteralPath $OutDir)) {
    New-Item -ItemType Directory -Path $OutDir | Out-Null
}

$manifest = New-Object System.Collections.Generic.List[object]
$allChunks = New-Object System.Collections.Generic.List[object]
$files = Get-ChildItem -LiteralPath $LibraryRoot -Recurse -File | Sort-Object FullName

foreach ($file in $files) {
    if ($IncludeExtensions -notcontains $file.Extension.ToLowerInvariant()) {
        continue
    }

    $relative = Get-RelativePath -Base $LibraryRoot -Path $file.FullName
    if ($relative -ieq "AGENTS.md") {
        continue
    }
    if (Test-ExcludedPath -RelativePath $relative -IncludeArchive:$IncludeArchive) {
        continue
    }

    $text = Read-TextFile $file.FullName
    $status = Get-DocStatus $text
    if (($status -eq "deprecated") -and (-not $IncludeDeprecated)) {
        continue
    }

    $title = Get-Title -Text $text -Fallback $file.Name
    $headings = Get-Headings $text
    $keywords = Get-Keywords -RelativePath $relative -Title $title -Headings $headings -Text $text
    $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()

    $manifest.Add([PSCustomObject]@{
        path = $relative
        title = $title
        extension = $file.Extension.ToLowerInvariant()
        status = $status
        size = $file.Length
        last_write_time = $file.LastWriteTime.ToString("s")
        hash = $hash
        headings = $headings
        keywords = $keywords
    })

    if ($file.Extension.ToLowerInvariant() -in @(".md", ".markdown")) {
        $chunks = Split-MarkdownChunks -Text $text -RelativePath $relative -Title $title -Status $status -MaxChunkChars $MaxChunkChars
    } else {
        $chunks = Split-PlainChunks -Text $text -RelativePath $relative -Title $title -Status $status -MaxChunkChars $MaxChunkChars
    }

    foreach ($chunk in $chunks) {
        $allChunks.Add($chunk)
    }
}

$generatedAt = (Get-Date).ToString("s")
$manifestObject = [PSCustomObject]@{
    schema = "knowledge-library-manifest-v1"
    generated_at = $generatedAt
    library_root = $LibraryRoot
    file_count = $manifest.Count
    chunk_count = $allChunks.Count
    files = $manifest.ToArray()
}

$manifestPath = Join-Path $OutDir "manifest.json"
$chunksPath = Join-Path $OutDir "chunks.jsonl"
$reportPath = Join-Path $OutDir "search-report.md"

$manifestObject | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
$writer = [System.IO.StreamWriter]::new($chunksPath, $false, [System.Text.UTF8Encoding]::new($false))
try {
    foreach ($chunk in $allChunks) {
        $writer.WriteLine(($chunk | ConvertTo-Json -Compress -Depth 8))
    }
} finally {
    $writer.Dispose()
}

$report = @(
    "# Knowledge Library Index Report",
    "",
    "- generated_at: $generatedAt",
    "- library_root: $LibraryRoot",
    "- files_indexed: $($manifest.Count)",
    "- chunks_indexed: $($allChunks.Count)",
    "- manifest: manifest.json",
    "- chunks: chunks.jsonl",
    "",
    "Generated files are disposable search caches. Do not hand edit `.ai/` files."
)
$report | Set-Content -LiteralPath $reportPath -Encoding UTF8

Write-Host "Indexed $($manifest.Count) files and $($allChunks.Count) chunks."
Write-Host "Manifest: $manifestPath"
Write-Host "Chunks:   $chunksPath"
