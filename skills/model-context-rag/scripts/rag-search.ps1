param(
    [Parameter(Position = 0)][string]$Query = "",
    [string]$ProjectRoot,
    [string]$ModelRoot,
    [string]$OutDir,
    [int]$Top = 8,
    [string]$Module,
    [string]$Page,
    [string]$SourceType,
    [string]$Severity,
    [switch]$ShowText,
    [switch]$Json
)

$ErrorActionPreference = "Stop"

$python = "python"
$script = Join-Path $PSScriptRoot "context_rag.py"
$argsList = @("search", $Query)

if (-not [string]::IsNullOrWhiteSpace($ProjectRoot)) { $argsList += @("--project-root", $ProjectRoot) }
if (-not [string]::IsNullOrWhiteSpace($ModelRoot)) { $argsList += @("--model-root", $ModelRoot) }
if (-not [string]::IsNullOrWhiteSpace($OutDir)) { $argsList += @("--out-dir", $OutDir) }
$argsList += @("--top", [string]$Top)
if (-not [string]::IsNullOrWhiteSpace($Module)) { $argsList += @("--module", $Module) }
if (-not [string]::IsNullOrWhiteSpace($Page)) { $argsList += @("--page", $Page) }
if (-not [string]::IsNullOrWhiteSpace($SourceType)) { $argsList += @("--source-type", $SourceType) }
if (-not [string]::IsNullOrWhiteSpace($Severity)) { $argsList += @("--severity", $Severity) }
if ($ShowText) { $argsList += "--show-text" }
if ($Json) { $argsList += "--json" }

& $python $script @argsList
exit $LASTEXITCODE
