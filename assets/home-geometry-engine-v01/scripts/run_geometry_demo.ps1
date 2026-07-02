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
$StateUpdater = Join-Path $EngineDir 'update_project_state.py'
$StateReader = Join-Path $EngineDir 'read_project_state.py'
$Summarizer = Join-Path $EngineDir 'summarize_validation.py'
$RepairDraft = Join-Path $EngineDir 'draft_repair_operations.py'
$ConfirmRepair = Join-Path $EngineDir 'confirm_repair_draft.py'
$SourceQualityGate = Join-Path $EngineDir 'source_quality_gate.py'
$SourceExtractionValidator = Join-Path $EngineDir 'validate_source_extraction.py'
$BaseModelExporter = Join-Path $EngineDir 'export_base_model_from_extraction.py'
$DimensionChainAudit = Join-Path $EngineDir 'dimension_chain_audit.py'
$DimensionChainCalibrator = Join-Path $EngineDir 'dimension_chain_calibrator.py'
$DimensionAnchorDrafter = Join-Path $EngineDir 'dimension_chain_anchor_drafter.py'
$DimensionAnchorApplier = Join-Path $EngineDir 'apply_dimension_anchor_draft.py'
$DimensionAnchorChecklist = Join-Path $EngineDir 'dimension_anchor_confirmation_checklist.py'
$BaseModel = Join-Path $ExamplesDir 'base_object_model.sample.json'
$ProblemModel = Join-Path $ExamplesDir 'base_object_model.problem-sample.json'
$DoorSwingModel = Join-Path $ExamplesDir 'base_object_model.door-swing-sample.json'
$IslandMoveModel = Join-Path $ExamplesDir 'base_object_model.island-move-sample.json'
$ArcPartitionModel = Join-Path $ExamplesDir 'base_object_model.arc-partition-sample.json'
$Operations = Join-Path $ExamplesDir 'operations.sample.json'
$SourceExtractionPackage = Join-Path $ExamplesDir 'source_extraction_package.sample.json'
$SourceExtractionProblemPackage = Join-Path $ExamplesDir 'source_extraction_package.problem-sample.json'

$ExportedBaseModel = Join-Path $OutputDir 'base_from_extraction_v1.json'
$ExportedBaseValidation = Join-Path $OutputDir 'source_extraction.export.validation.json'
$FailedBaseExport = Join-Path $OutputDir 'base_from_extraction_problem.json'
$FailedBaseExportValidation = Join-Path $OutputDir 'source_extraction.problem.export.validation.json'
$SchemeA = Join-Path $OutputDir 'scheme_A_v1.json'
$ValidationBase = Join-Path $OutputDir 'validation.json'
$ValidationSchemeA = Join-Path $OutputDir 'validation.scheme_A_v1.json'
$ValidationProblem = Join-Path $OutputDir 'validation.problem.json'
$ValidationDoorSwing = Join-Path $OutputDir 'validation.door_swing_sample.json'
$ValidationIslandMove = Join-Path $OutputDir 'validation.island_move_sample.json'
$ValidationArcPartition = Join-Path $OutputDir 'validation.arc_partition_sample.json'
$SourceQualityBase = Join-Path $OutputDir 'source_quality.base.json'
$SourceQualityProblem = Join-Path $OutputDir 'source_quality.problem.json'
$SourceQualityExportedBase = Join-Path $OutputDir 'source_quality.base_from_extraction_v1.json'
$SourceExtractionValidation = Join-Path $OutputDir 'source_extraction.validation.json'
$SourceExtractionProblemValidation = Join-Path $OutputDir 'source_extraction.problem.validation.json'
$DimensionChainAuditReport = Join-Path $OutputDir 'dimension_chain_audit.json'
$DimensionChainProblemAuditReport = Join-Path $OutputDir 'dimension_chain_audit.problem.json'
$DimensionCalibrationPlan = Join-Path $OutputDir 'dimension_calibration_plan.json'
$DimensionProblemCalibrationPlan = Join-Path $OutputDir 'dimension_calibration_plan.problem.json'
$DimensionAnchorDraft = Join-Path $OutputDir 'dimension_anchor_draft.json'
$DimensionProblemAnchorDraft = Join-Path $OutputDir 'dimension_anchor_draft.problem.json'
$DimensionAnchorAppliedPackage = Join-Path $OutputDir 'source_extraction.anchors_applied.json'
$DimensionAnchorApplyReport = Join-Path $OutputDir 'dimension_anchor_apply.report.json'
$DimensionAnchorAppliedValidation = Join-Path $OutputDir 'source_extraction.anchors_applied.validation.json'
$DimensionAnchorChecklistJson = Join-Path $OutputDir 'dimension_anchor_confirmation_checklist.json'
$DimensionAnchorChecklistMd = Join-Path $OutputDir 'dimension_anchor_confirmation_checklist.md'
$ValidationExportedBase = Join-Path $OutputDir 'validation.base_from_extraction_v1.json'
$PlanBase = Join-Path $OutputDir 'plan.svg'
$PlanExportedBase = Join-Path $OutputDir 'plan.base_from_extraction_v1.svg'
$PlanSchemeA = Join-Path $OutputDir 'plan.scheme_A_v1.svg'
$PlanProblem = Join-Path $OutputDir 'plan.problem.svg'
$PlanDoorSwing = Join-Path $OutputDir 'plan.door_swing_sample.svg'
$PlanIslandMove = Join-Path $OutputDir 'plan.island_move_sample.svg'
$PlanArcPartition = Join-Path $OutputDir 'plan.arc_partition_sample.svg'
$ProjectState = Join-Path $OutputDir 'project_state.json'

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
Invoke-Step 'compile operation applier' { & $PythonExe -m py_compile $Applier }
Invoke-Step 'compile renderer' { & $PythonExe -m py_compile $Renderer }
Invoke-Step 'compile summarizer' { & $PythonExe -m py_compile $Summarizer }
Invoke-Step 'compile repair draft' { & $PythonExe -m py_compile $RepairDraft }
Invoke-Step 'compile confirm repair' { & $PythonExe -m py_compile $ConfirmRepair }
Invoke-Step 'compile source quality gate' { & $PythonExe -m py_compile $SourceQualityGate }
Invoke-Step 'compile source extraction validator' { & $PythonExe -m py_compile $SourceExtractionValidator }
Invoke-Step 'compile base model exporter' { & $PythonExe -m py_compile $BaseModelExporter }
Invoke-Step 'compile dimension chain audit' { & $PythonExe -m py_compile $DimensionChainAudit }
Invoke-Step 'compile dimension chain calibrator' { & $PythonExe -m py_compile $DimensionChainCalibrator }
Invoke-Step 'compile dimension anchor drafter' { & $PythonExe -m py_compile $DimensionAnchorDrafter }
Invoke-Step 'compile dimension anchor applier' { & $PythonExe -m py_compile $DimensionAnchorApplier }
Invoke-Step 'compile dimension anchor checklist' { & $PythonExe -m py_compile $DimensionAnchorChecklist }
Invoke-Step 'compile state updater' { & $PythonExe -m py_compile $StateUpdater }
Invoke-Step 'compile state reader' { & $PythonExe -m py_compile $StateReader }
Invoke-Step 'validate base model' { & $PythonExe $Validator $BaseModel $ValidationBase }
Invoke-Step 'validate problem sample' { & $PythonExe $Validator $ProblemModel $ValidationProblem } @(0, 1)
Invoke-Step 'validate door swing sample' { & $PythonExe $Validator $DoorSwingModel $ValidationDoorSwing } @(0, 1)
Invoke-Step 'validate island move sample' { & $PythonExe $Validator $IslandMoveModel $ValidationIslandMove } @(0, 1)
Invoke-Step 'validate arc partition sample' { & $PythonExe $Validator $ArcPartitionModel $ValidationArcPartition } @(0, 1)
Invoke-Step 'source quality base' { & $PythonExe $SourceQualityGate $BaseModel $SourceQualityBase --validation $ValidationBase }
Invoke-Step 'source quality problem' { & $PythonExe $SourceQualityGate $ProblemModel $SourceQualityProblem --validation $ValidationProblem } @(0, 1)
Invoke-Step 'validate source extraction package' { & $PythonExe $SourceExtractionValidator $SourceExtractionPackage $SourceExtractionValidation }
Invoke-Step 'validate source extraction problem package' { & $PythonExe $SourceExtractionValidator $SourceExtractionProblemPackage $SourceExtractionProblemValidation } @(0, 1)
Invoke-Step 'audit source dimension chains' { & $PythonExe $DimensionChainAudit $SourceExtractionPackage $DimensionChainAuditReport }
Invoke-Step 'audit problem dimension chains' { & $PythonExe $DimensionChainAudit $SourceExtractionProblemPackage $DimensionChainProblemAuditReport } @(0, 1)
Invoke-Step 'plan source dimension calibration' { & $PythonExe $DimensionChainCalibrator $SourceExtractionPackage $DimensionCalibrationPlan }
Invoke-Step 'plan problem dimension calibration' { & $PythonExe $DimensionChainCalibrator $SourceExtractionProblemPackage $DimensionProblemCalibrationPlan } @(0, 1)
Invoke-Step 'draft source dimension anchors' { & $PythonExe $DimensionAnchorDrafter $SourceExtractionPackage $DimensionAnchorDraft }
Invoke-Step 'draft problem dimension anchors' { & $PythonExe $DimensionAnchorDrafter $SourceExtractionProblemPackage $DimensionProblemAnchorDraft } @(0, 1)
Invoke-Step 'apply source dimension anchor draft' { & $PythonExe $DimensionAnchorApplier $SourceExtractionPackage $DimensionAnchorDraft $DimensionAnchorAppliedPackage $DimensionAnchorApplyReport --version source_extraction_anchors_applied_v1 }
Invoke-Step 'validate source with applied anchors' { & $PythonExe $SourceExtractionValidator $DimensionAnchorAppliedPackage $DimensionAnchorAppliedValidation }
Invoke-Step 'build dimension anchor confirmation checklist' { & $PythonExe $DimensionAnchorChecklist $DimensionAnchorDraft $DimensionAnchorChecklistJson $DimensionAnchorChecklistMd --title 'Dimension Anchor Confirmation Checklist' }
Invoke-Step 'export base model from extraction package' { & $PythonExe $BaseModelExporter $SourceExtractionPackage $ExportedBaseModel --validation-output $ExportedBaseValidation --minimum-level L3 --version base_from_extraction_v1 }
Invoke-Step 'reject bad source extraction export' { & $PythonExe $BaseModelExporter $SourceExtractionProblemPackage $FailedBaseExport --validation-output $FailedBaseExportValidation --minimum-level L2 --allow-warning --version base_problem_v1 } @(0, 1)
Invoke-Step 'validate exported base model' { & $PythonExe $Validator $ExportedBaseModel $ValidationExportedBase }
Invoke-Step 'source quality exported base' { & $PythonExe $SourceQualityGate $ExportedBaseModel $SourceQualityExportedBase --validation $ValidationExportedBase }
Invoke-Step 'rebuild scheme A from exported base' { & $PythonExe $Applier $ExportedBaseModel $Operations $SchemeA }
Invoke-Step 'validate scheme A from exported base' { & $PythonExe $Validator $SchemeA $ValidationSchemeA }
Invoke-Step 'render base SVG' { & $PythonExe $Renderer $BaseModel $PlanBase $ValidationBase }
Invoke-Step 'render exported base SVG' { & $PythonExe $Renderer $ExportedBaseModel $PlanExportedBase $ValidationExportedBase }
Invoke-Step 'render scheme A SVG' { & $PythonExe $Renderer $SchemeA $PlanSchemeA $ValidationSchemeA }
Invoke-Step 'render problem SVG' { & $PythonExe $Renderer $ProblemModel $PlanProblem $ValidationProblem }
Invoke-Step 'render door swing SVG' { & $PythonExe $Renderer $DoorSwingModel $PlanDoorSwing $ValidationDoorSwing }
Invoke-Step 'render island move SVG' { & $PythonExe $Renderer $IslandMoveModel $PlanIslandMove $ValidationIslandMove }
Invoke-Step 'render arc partition SVG' { & $PythonExe $Renderer $ArcPartitionModel $PlanArcPartition $ValidationArcPartition }
Invoke-Step 'update project state' { & $PythonExe $StateUpdater --output $ProjectState --base-model $ExportedBaseModel --base-validation $ValidationExportedBase --base-version base_from_extraction_v1 --scheme-a-model $SchemeA --scheme-a-validation $ValidationSchemeA --scheme-a-version scheme_A_v1 --problem-validation $ValidationProblem --base-source-quality $SourceQualityExportedBase --base-source-extraction $SourceExtractionValidation }

Write-Host '== state gate'
& $PythonExe $StateReader $ProjectState

Write-Host '== validation summary'
Show-Summary 'base' $ValidationBase
Show-Summary 'exported_base' $ValidationExportedBase
Show-Summary 'scheme_A' $ValidationSchemeA
Show-Summary 'problem' $ValidationProblem
Show-Summary 'door_swing' $ValidationDoorSwing
Show-Summary 'island_move' $ValidationIslandMove
Show-Summary 'arc_partition' $ValidationArcPartition
Write-Host '== source extraction gate'
& $PythonExe $SourceExtractionValidator $SourceExtractionPackage $SourceExtractionValidation
& $PythonExe $SourceExtractionValidator $SourceExtractionProblemPackage $SourceExtractionProblemValidation

Write-Host '== dimension chain audit'
& $PythonExe $DimensionChainAudit $SourceExtractionPackage $DimensionChainAuditReport
& $PythonExe $DimensionChainAudit $SourceExtractionProblemPackage $DimensionChainProblemAuditReport

Write-Host '== dimension calibration plan'
& $PythonExe $DimensionChainCalibrator $SourceExtractionPackage $DimensionCalibrationPlan
& $PythonExe $DimensionChainCalibrator $SourceExtractionProblemPackage $DimensionProblemCalibrationPlan

Write-Host '== dimension anchor draft'
& $PythonExe $DimensionAnchorDrafter $SourceExtractionPackage $DimensionAnchorDraft
& $PythonExe $DimensionAnchorDrafter $SourceExtractionProblemPackage $DimensionProblemAnchorDraft

Write-Host '== dimension anchor apply'
& $PythonExe $DimensionAnchorApplier $SourceExtractionPackage $DimensionAnchorDraft $DimensionAnchorAppliedPackage $DimensionAnchorApplyReport --version source_extraction_anchors_applied_v1
& $PythonExe $SourceExtractionValidator $DimensionAnchorAppliedPackage $DimensionAnchorAppliedValidation

Write-Host '== dimension anchor confirmation checklist'
& $PythonExe $DimensionAnchorChecklist $DimensionAnchorDraft $DimensionAnchorChecklistJson $DimensionAnchorChecklistMd --title 'Dimension Anchor Confirmation Checklist'

Write-Host '== source quality gate'
& $PythonExe $SourceQualityGate $BaseModel $SourceQualityBase --validation $ValidationBase
& $PythonExe $SourceQualityGate $ExportedBaseModel $SourceQualityExportedBase --validation $ValidationExportedBase
& $PythonExe $SourceQualityGate $ProblemModel $SourceQualityProblem --validation $ValidationProblem

Write-Host '== outputs'
Write-Host $ValidationBase
Write-Host $ValidationSchemeA
Write-Host $ValidationProblem
Write-Host $ValidationDoorSwing
Write-Host $ValidationIslandMove
Write-Host $ValidationArcPartition
Write-Host $SourceQualityBase
Write-Host $SourceQualityExportedBase
Write-Host $SourceQualityProblem
Write-Host $SourceExtractionValidation
Write-Host $SourceExtractionProblemValidation
Write-Host $DimensionChainAuditReport
Write-Host $DimensionChainProblemAuditReport
Write-Host $DimensionCalibrationPlan
Write-Host $DimensionProblemCalibrationPlan
Write-Host $DimensionAnchorDraft
Write-Host $DimensionProblemAnchorDraft
Write-Host $DimensionAnchorAppliedPackage
Write-Host $DimensionAnchorApplyReport
Write-Host $DimensionAnchorAppliedValidation
Write-Host $DimensionAnchorChecklistJson
Write-Host $DimensionAnchorChecklistMd
Write-Host $ExportedBaseModel
Write-Host $ValidationExportedBase
Write-Host $ExportedBaseValidation
Write-Host $FailedBaseExportValidation
Write-Host $PlanBase
Write-Host $PlanExportedBase
Write-Host $PlanSchemeA
Write-Host $PlanProblem
Write-Host $PlanDoorSwing
Write-Host $PlanIslandMove
Write-Host $PlanArcPartition
Write-Host $ProjectState
