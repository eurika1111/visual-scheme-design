param(
    [string]$PythonExe = 'C:\Users\eurik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe',
    [string]$OutputDir = 'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01'
)

$ErrorActionPreference = 'Stop'

$EngineDir = Split-Path -Parent $PSScriptRoot
$ExamplesDir = Join-Path $EngineDir 'examples'

$Validator = Join-Path $EngineDir 'geometry_validator.py'
$Applier = Join-Path $EngineDir 'operation_applier.py'
$Renderer = Join-Path $EngineDir 'simple_renderer.py'
$BaseModel = Join-Path $ExamplesDir 'base_object_model.sample.json'
$ProblemModel = Join-Path $ExamplesDir 'base_object_model.problem-sample.json'
$Operations = Join-Path $ExamplesDir 'operations.sample.json'

$SchemeA = Join-Path $OutputDir 'scheme_A_v1.json'
$ValidationBase = Join-Path $OutputDir 'validation.json'
$ValidationSchemeA = Join-Path $OutputDir 'validation.scheme_A_v1.json'
$ValidationProblem = Join-Path $OutputDir 'validation.problem.json'
$PlanBase = Join-Path $OutputDir 'plan.svg'
$PlanSchemeA = Join-Path $OutputDir 'plan.scheme_A_v1.svg'
$PlanProblem = Join-Path $OutputDir 'plan.problem.svg'

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Action,
        [int[]]$AllowedExitCodes = @(0)
    )
    Write-Host "== $Name"
    & $Action
    $code = $LASTEXITCODE
    if ($null -eq $code) { $code = 0 }
    if ($AllowedExitCodes -notcontains $code) {
        throw "$Name failed with exit code $code"
    }
}

function Show-Summary {
    param([string]$Label, [string]$Path)
    $data = Get-Content -Path $Path -Raw -Encoding UTF8 | ConvertFrom-Json
    $summary = $data.summary
    Write-Host ("{0}: readiness={1}, errors={2}, warnings={3}, furniture={4}, kitchen={5}, paths={6}" -f `
        $Label, $data.readiness, $summary.error_count, $summary.warning_count, `
        $summary.furniture_count, $summary.kitchen_object_count, $summary.circulation_path_count)
}

if (-not (Test-Path -Path $PythonExe)) {
    throw "Bundled Python not found: $PythonExe"
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Invoke-Step 'compile validator' { & $PythonExe -m py_compile $Validator }
Invoke-Step 'compile renderer' { & $PythonExe -m py_compile $Renderer }
Invoke-Step 'validate base model' { & $PythonExe $Validator $BaseModel $ValidationBase }
Invoke-Step 'build scheme A' { & $PythonExe $Applier $BaseModel $Operations $SchemeA }
Invoke-Step 'validate scheme A' { & $PythonExe $Validator $SchemeA $ValidationSchemeA }
Invoke-Step 'validate problem sample' { & $PythonExe $Validator $ProblemModel $ValidationProblem } @(0, 1)
Invoke-Step 'render base SVG' { & $PythonExe $Renderer $BaseModel $PlanBase $ValidationBase }
Invoke-Step 'render scheme A SVG' { & $PythonExe $Renderer $SchemeA $PlanSchemeA $ValidationSchemeA }
Invoke-Step 'render problem SVG' { & $PythonExe $Renderer $ProblemModel $PlanProblem $ValidationProblem }

Write-Host '== validation summary'
Show-Summary 'base' $ValidationBase
Show-Summary 'scheme_A' $ValidationSchemeA
Show-Summary 'problem' $ValidationProblem

Write-Host '== outputs'
Write-Host $ValidationBase
Write-Host $ValidationSchemeA
Write-Host $ValidationProblem
Write-Host $PlanBase
Write-Host $PlanSchemeA
Write-Host $PlanProblem
