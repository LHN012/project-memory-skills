param(
    [string]$ProjectRoot,
    [string]$ModelRoot,
    [string]$OutDir,
    [int]$MaxChunkChars = 2400,
    [int]$MinChunkChars = 120,
    [switch]$Json
)

$ErrorActionPreference = "Stop"

$python = "python"
$script = Join-Path $PSScriptRoot "context_rag.py"
$argsList = @("index")

if (-not [string]::IsNullOrWhiteSpace($ProjectRoot)) { $argsList += @("--project-root", $ProjectRoot) }
if (-not [string]::IsNullOrWhiteSpace($ModelRoot)) { $argsList += @("--model-root", $ModelRoot) }
if (-not [string]::IsNullOrWhiteSpace($OutDir)) { $argsList += @("--out-dir", $OutDir) }
$argsList += @("--max-chunk-chars", [string]$MaxChunkChars, "--min-chunk-chars", [string]$MinChunkChars)
if ($Json) { $argsList += "--json" }

& $python $script @argsList
exit $LASTEXITCODE
