param(
    [string]$ProjectRoot,
    [string]$ModelRoot,
    [string]$OutDir,
    [switch]$Json
)

$ErrorActionPreference = "Stop"

$python = "python"
$script = Join-Path $PSScriptRoot "context_rag.py"
$argsList = @("validate")

if (-not [string]::IsNullOrWhiteSpace($ProjectRoot)) { $argsList += @("--project-root", $ProjectRoot) }
if (-not [string]::IsNullOrWhiteSpace($ModelRoot)) { $argsList += @("--model-root", $ModelRoot) }
if (-not [string]::IsNullOrWhiteSpace($OutDir)) { $argsList += @("--out-dir", $OutDir) }
if ($Json) { $argsList += "--json" }

& $python $script @argsList
exit $LASTEXITCODE
