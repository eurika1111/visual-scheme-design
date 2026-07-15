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
$SvgPreviewRenderer = Join-Path $EngineDir 'svg_preview_renderer.py'
$StateUpdater = Join-Path $EngineDir 'update_project_state.py'
$StateReader = Join-Path $EngineDir 'read_project_state.py'
$Workflow = Join-Path $EngineDir 'home_geometry_workflow.py'
$BaseHandoffBuilder = Join-Path $EngineDir 'base_handoff_builder.py'
$NeedsBriefBuilder = Join-Path $EngineDir 'needs_brief_builder.py'
$SchemeOptionPlanner = Join-Path $EngineDir 'scheme_option_planner.py'
$SchemePlacementResolver = Join-Path $EngineDir 'scheme_placement_resolver.py'
$SchemeReviewBuilder = Join-Path $EngineDir 'scheme_review_package_builder.py'
$SchemeFeedbackMigrator = Join-Path $EngineDir 'scheme_feedback_migrator.py'
$SchemeHistoryManager = Join-Path $EngineDir 'scheme_history_manager.py'
$VisualHandoffBuilder = Join-Path $EngineDir 'visual_generation_handoff_builder.py'
$BaseLockBuilder = Join-Path $EngineDir 'base_lock_manifest.py'
$ConceptOutputReview = Join-Path $EngineDir 'concept_output_review.py'
$SchemeDraftRenderer = Join-Path $EngineDir 'scheme_draft_renderer.py'
$Summarizer = Join-Path $EngineDir 'summarize_validation.py'
$RepairDraft = Join-Path $EngineDir 'draft_repair_operations.py'
$ConfirmRepair = Join-Path $EngineDir 'confirm_repair_draft.py'
$SourceQualityGate = Join-Path $EngineDir 'source_quality_gate.py'
$BaseFidelityGate = Join-Path $EngineDir 'base_fidelity_gate.py'
$SourceWallMask = Join-Path $EngineDir 'source_wall_mask.py'
$TraceModelBuilder = Join-Path $EngineDir 'build_model_from_trace.py'
$StagedTopologyImporter = Join-Path $EngineDir 'staged_topology_importer.py'
$SourceTraceOverlay = Join-Path $EngineDir 'source_trace_overlay.py'
$SourceExtractionValidator = Join-Path $EngineDir 'validate_source_extraction.py'
$BaseModelExporter = Join-Path $EngineDir 'export_base_model_from_extraction.py'
$DimensionChainAudit = Join-Path $EngineDir 'dimension_chain_audit.py'
$DimensionChainCalibrator = Join-Path $EngineDir 'dimension_chain_calibrator.py'
$DimensionAnchorDrafter = Join-Path $EngineDir 'dimension_chain_anchor_drafter.py'
$DimensionAnchorApplier = Join-Path $EngineDir 'apply_dimension_anchor_draft.py'
$DimensionAnchorChecklist = Join-Path $EngineDir 'dimension_anchor_confirmation_checklist.py'
$DimensionAnchorConfirmationApplier = Join-Path $EngineDir 'apply_dimension_anchor_confirmation.py'
$DimensionAnchorReviewRenderer = Join-Path $EngineDir 'dimension_anchor_review_svg.py'
$BaseModel = Join-Path $ExamplesDir 'base_object_model.sample.json'
$ProblemModel = Join-Path $ExamplesDir 'base_object_model.problem-sample.json'
$DoorSwingModel = Join-Path $ExamplesDir 'base_object_model.door-swing-sample.json'
$IslandMoveModel = Join-Path $ExamplesDir 'base_object_model.island-move-sample.json'
$ArcPartitionModel = Join-Path $ExamplesDir 'base_object_model.arc-partition-sample.json'
$Operations = Join-Path $ExamplesDir 'operations.sample.json'
$SourceExtractionPackage = Join-Path $ExamplesDir 'source_extraction_package.sample.json'
$SourceExtractionProblemPackage = Join-Path $ExamplesDir 'source_extraction_package.problem-sample.json'
$DimensionAnchorConfirmationResponse = Join-Path $ExamplesDir 'dimension_anchor_confirmation_response.sample.json'
$NeedsResponse = Join-Path $ExamplesDir 'needs_response.sample.json'
$CaseStrategy = Join-Path $ExamplesDir 'case_strategy.sample.json'
$PlacementSampleIntent = Join-Path $ExamplesDir 'scheme_intent.placement-sample.json'
$PlacementSampleIntentB = Join-Path $ExamplesDir 'scheme_intent.placement-sample-b.json'
$PlacementSampleIntentC = Join-Path $ExamplesDir 'scheme_intent.placement-sample-c.json'
$SchemeFeedbackSample = Join-Path $ExamplesDir 'scheme_feedback.copy-object.sample.json'
$MoveFeedbackSample = Join-Path $ExamplesDir 'scheme_feedback.move-object.sample.json'
$RotateFeedbackSample = Join-Path $ExamplesDir 'scheme_feedback.rotate-object.sample.json'
$RemoveFeedbackSample = Join-Path $ExamplesDir 'scheme_feedback.remove-object.sample.json'
$ReplaceFeedbackSample = Join-Path $ExamplesDir 'scheme_feedback.replace-object.sample.json'
$VisualStyleBrief = Join-Path $ExamplesDir 'visual_style_brief.sample.json'
$AcceptedBaseFidelityEvidence = Join-Path $ExamplesDir 'base_fidelity_evidence.accepted.sample.json'

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
$DimensionAnchorConfirmedPackage = Join-Path $OutputDir 'source_extraction.anchors_confirmed.json'
$DimensionAnchorConfirmationApplyReport = Join-Path $OutputDir 'dimension_anchor_confirmation_apply.report.json'
$DimensionAnchorConfirmedValidation = Join-Path $OutputDir 'source_extraction.anchors_confirmed.validation.json'
$DimensionAnchorReviewSvg = Join-Path $OutputDir 'dimension_anchor_review.svg'
$ValidationExportedBase = Join-Path $OutputDir 'validation.base_from_extraction_v1.json'
$PlanBase = Join-Path $OutputDir 'plan.svg'
$PlanBaseClient = Join-Path $OutputDir 'plan.client_base.svg'
$PlanBaseClientPreview = Join-Path $OutputDir 'plan.client_base.preview.png'
$PlanBaseClientPreviewSmall = Join-Path $OutputDir 'plan.client_base.preview.small.png'
$BaseLockManifest = Join-Path $OutputDir 'base_sample_v1.lock.json'
$BaseHandoff = Join-Path $OutputDir 'base_handoff.md'
$BaseReviewPackageDir = Join-Path $OutputDir 'base_review_package'
$NeedsBriefJson = Join-Path $OutputDir 'client.needs_brief.json'
$NeedsBriefMd = Join-Path $OutputDir 'client.needs_brief.md'
$SchemeOptionsDir = Join-Path $OutputDir 'scheme_options'
$SchemeOptionPlan = Join-Path $SchemeOptionsDir 'scheme_option_plan.json'
$SchemeOptionPlanMd = Join-Path $SchemeOptionsDir 'scheme_option_plan.md'
$PlannedSchemeAIntent = Join-Path $SchemeOptionsDir 'scheme_A_v1_intent.json'
$BlockedDraftDir = Join-Path $OutputDir 'blocked_draft_check'
$BlockedDraftReport = Join-Path $BlockedDraftDir 'scheme_A_v1.draft_report.json'
$PlacementDemoDir = Join-Path $OutputDir 'placement_demo'
$ResolvedPlacementIntent = Join-Path $PlacementDemoDir 'placement_sample.layout_intent.json'
$ResolvedPlacementIntentB = Join-Path $PlacementDemoDir 'placement_sample_b.layout_intent.json'
$ResolvedPlacementIntentC = Join-Path $PlacementDemoDir 'placement_sample_c.layout_intent.json'
$PlacementReport = Join-Path $PlacementDemoDir 'placement_sample.placement_report.json'
$PlacementDraftReport = Join-Path $PlacementDemoDir 'placement_sample.draft_report.json'
$SchemeReviewDir = Join-Path $OutputDir 'scheme_review_package'
$SchemeReviewManifest = Join-Path $SchemeReviewDir 'scheme_review_manifest.json'
$FeedbackDemoDir = Join-Path $OutputDir 'feedback_demo'
$MigratedSchemeB = Join-Path $FeedbackDemoDir 'scheme_feedback.copy-object.sample.migrated_intent.json'
$FeedbackMigrationReport = Join-Path $FeedbackDemoDir 'scheme_feedback.copy-object.sample.migration_report.json'
$MoveFeedbackReport = Join-Path $FeedbackDemoDir 'scheme_feedback.move-object.sample.migration_report.json'
$RotateFeedbackReport = Join-Path $FeedbackDemoDir 'scheme_feedback.rotate-object.sample.migration_report.json'
$RemoveFeedbackReport = Join-Path $FeedbackDemoDir 'scheme_feedback.remove-object.sample.migration_report.json'
$ReplaceFeedbackReport = Join-Path $FeedbackDemoDir 'scheme_feedback.replace-object.sample.migration_report.json'
$MovedSchemeB = Join-Path $FeedbackDemoDir 'scheme_feedback.move-object.sample.migrated_intent.json'
$SchemeHistory = Join-Path $OutputDir 'scheme_history.json'
$SchemeHistoryBranch = Join-Path $OutputDir 'scheme_B_alt_branch.intent.json'
$RejectedHistoryChild = Join-Path $OutputDir 'rejected_history_child.intent.json'
$VisualHandoffNeedsStyleDir = Join-Path $OutputDir 'visual_handoff_needs_style'
$VisualHandoffReadyDir = Join-Path $OutputDir 'visual_handoff_ready'
$VisualHandoffNeedsStyle = Join-Path $VisualHandoffNeedsStyleDir 'visual_generation_handoff.json'
$VisualHandoffReady = Join-Path $VisualHandoffReadyDir 'visual_generation_handoff.json'
$VisualGenerationPrompt = Join-Path $VisualHandoffReadyDir 'generation_prompt.txt'
$VisualHandoffQuickDir = Join-Path $OutputDir 'visual_handoff_quick'
$VisualHandoffQuick = Join-Path $VisualHandoffQuickDir 'visual_generation_handoff.json'
$VisualHandoffTamperedDir = Join-Path $OutputDir 'visual_handoff_tampered_base'
$VisualHandoffTampered = Join-Path $VisualHandoffTamperedDir 'visual_generation_handoff.json'
$ConceptReviewDir = Join-Path $OutputDir 'concept_output_review'
$ConceptReviewReport = Join-Path $ConceptReviewDir 'concept_output_review.json'
$ConceptReviewMismatchDir = Join-Path $OutputDir 'concept_output_review_mismatch'
$ConceptReviewMismatchReport = Join-Path $ConceptReviewMismatchDir 'concept_output_review.json'
$UpdatedSchemeReviewDir = Join-Path $OutputDir 'scheme_review_after_feedback'
$UpdatedSchemeReviewManifest = Join-Path $UpdatedSchemeReviewDir 'scheme_review_manifest.json'
$PlanExportedBase = Join-Path $OutputDir 'plan.base_from_extraction_v1.svg'
$PlanSchemeA = Join-Path $OutputDir 'plan.scheme_A_v1.svg'
$PlanProblem = Join-Path $OutputDir 'plan.problem.svg'
$PlanDoorSwing = Join-Path $OutputDir 'plan.door_swing_sample.svg'
$PlanIslandMove = Join-Path $OutputDir 'plan.island_move_sample.svg'
$PlanArcPartition = Join-Path $OutputDir 'plan.arc_partition_sample.svg'
$ProjectState = Join-Path $OutputDir 'project_state.json'
$BaseFidelityReport = Join-Path $OutputDir 'base_fidelity.accepted.report.json'

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
Remove-Item -LiteralPath $SchemeHistory -Force -ErrorAction SilentlyContinue

Invoke-Step 'compile validator' { & $PythonExe -m py_compile $Validator }
Invoke-Step 'compile operation applier' { & $PythonExe -m py_compile $Applier }
Invoke-Step 'compile renderer' { & $PythonExe -m py_compile $Renderer }
Invoke-Step 'compile SVG preview renderer' { & $PythonExe -m py_compile $SvgPreviewRenderer }
Invoke-Step 'compile workflow entrypoint' { & $PythonExe -m py_compile $Workflow }
Invoke-Step 'compile base handoff builder' { & $PythonExe -m py_compile $BaseHandoffBuilder }
Invoke-Step 'compile needs brief builder' { & $PythonExe -m py_compile $NeedsBriefBuilder }
Invoke-Step 'compile scheme option planner' { & $PythonExe -m py_compile $SchemeOptionPlanner }
Invoke-Step 'compile scheme placement resolver' { & $PythonExe -m py_compile $SchemePlacementResolver }
Invoke-Step 'compile scheme review package builder' { & $PythonExe -m py_compile $SchemeReviewBuilder }
Invoke-Step 'compile scheme feedback migrator' { & $PythonExe -m py_compile $SchemeFeedbackMigrator }
Invoke-Step 'compile scheme history manager' { & $PythonExe -m py_compile $SchemeHistoryManager }
Invoke-Step 'compile visual generation handoff builder' { & $PythonExe -m py_compile $VisualHandoffBuilder }
Invoke-Step 'compile base lock builder' { & $PythonExe -m py_compile $BaseLockBuilder }
Invoke-Step 'compile concept output review' { & $PythonExe -m py_compile $ConceptOutputReview }
Invoke-Step 'compile scheme draft renderer' { & $PythonExe -m py_compile $SchemeDraftRenderer }
Invoke-Step 'compile summarizer' { & $PythonExe -m py_compile $Summarizer }
Invoke-Step 'compile repair draft' { & $PythonExe -m py_compile $RepairDraft }
Invoke-Step 'compile confirm repair' { & $PythonExe -m py_compile $ConfirmRepair }
Invoke-Step 'compile source quality gate' { & $PythonExe -m py_compile $SourceQualityGate }
Invoke-Step 'compile base fidelity gate' { & $PythonExe -m py_compile $BaseFidelityGate }
Invoke-Step 'compile source wall mask' { & $PythonExe -m py_compile $SourceWallMask }
Invoke-Step 'compile trace model builder' { & $PythonExe -m py_compile $TraceModelBuilder }
Invoke-Step 'compile staged topology importer' { & $PythonExe -m py_compile $StagedTopologyImporter }
Invoke-Step 'compile source trace overlay' { & $PythonExe -m py_compile $SourceTraceOverlay }
Invoke-Step 'compile source extraction validator' { & $PythonExe -m py_compile $SourceExtractionValidator }
Invoke-Step 'compile base model exporter' { & $PythonExe -m py_compile $BaseModelExporter }
Invoke-Step 'compile dimension chain audit' { & $PythonExe -m py_compile $DimensionChainAudit }
Invoke-Step 'compile dimension chain calibrator' { & $PythonExe -m py_compile $DimensionChainCalibrator }
Invoke-Step 'compile dimension anchor drafter' { & $PythonExe -m py_compile $DimensionAnchorDrafter }
Invoke-Step 'compile dimension anchor applier' { & $PythonExe -m py_compile $DimensionAnchorApplier }
Invoke-Step 'compile dimension anchor checklist' { & $PythonExe -m py_compile $DimensionAnchorChecklist }
Invoke-Step 'compile dimension anchor confirmation applier' { & $PythonExe -m py_compile $DimensionAnchorConfirmationApplier }
Invoke-Step 'compile dimension anchor review renderer' { & $PythonExe -m py_compile $DimensionAnchorReviewRenderer }
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
Invoke-Step 'apply dimension anchor confirmation response' { & $PythonExe $DimensionAnchorConfirmationApplier $SourceExtractionPackage $DimensionAnchorChecklistJson $DimensionAnchorConfirmationResponse $DimensionAnchorConfirmedPackage $DimensionAnchorConfirmationApplyReport --version source_extraction_anchors_confirmed_v1 }
Invoke-Step 'validate source with confirmed anchors' { & $PythonExe $SourceExtractionValidator $DimensionAnchorConfirmedPackage $DimensionAnchorConfirmedValidation }
Invoke-Step 'render dimension anchor review SVG' { & $PythonExe $DimensionAnchorReviewRenderer $DimensionAnchorConfirmedPackage $DimensionAnchorReviewSvg }
Invoke-Step 'export base model from extraction package' { & $PythonExe $BaseModelExporter $SourceExtractionPackage $ExportedBaseModel --validation-output $ExportedBaseValidation --minimum-level L3 --version base_from_extraction_v1 }
Invoke-Step 'reject bad source extraction export' { & $PythonExe $BaseModelExporter $SourceExtractionProblemPackage $FailedBaseExport --validation-output $FailedBaseExportValidation --minimum-level L2 --allow-warning --version base_problem_v1 } @(0, 1)
Invoke-Step 'validate exported base model' { & $PythonExe $Validator $ExportedBaseModel $ValidationExportedBase }
Invoke-Step 'source quality exported base' { & $PythonExe $SourceQualityGate $ExportedBaseModel $SourceQualityExportedBase --validation $ValidationExportedBase }
Invoke-Step 'accept reviewed base fidelity' { & $PythonExe $BaseFidelityGate $ExportedBaseModel $AcceptedBaseFidelityEvidence $BaseFidelityReport }
Invoke-Step 'rebuild scheme A from exported base' { & $PythonExe $Applier $ExportedBaseModel $Operations $SchemeA }
Invoke-Step 'validate scheme A from exported base' { & $PythonExe $Validator $SchemeA $ValidationSchemeA }
Invoke-Step 'render base SVG' { & $PythonExe $Renderer $BaseModel $PlanBase $ValidationBase }
Invoke-Step 'render client base SVG' { & $PythonExe $Renderer $BaseModel $PlanBaseClient $ValidationBase --mode client --title 'Client Base Confirmation' }
Invoke-Step 'render client base PNG preview' { & $PythonExe $SvgPreviewRenderer $PlanBaseClient $PlanBaseClientPreview --max-width 1600 }
Invoke-Step 'render mismatched PNG test preview' { & $PythonExe $SvgPreviewRenderer $PlanBaseClient $PlanBaseClientPreviewSmall --max-width 800 }
Invoke-Step 'lock confirmed concept base' { & $PythonExe $Workflow lock-base --base-model $BaseModel --confirmation-visual $PlanBaseClientPreview --validation $ValidationBase --base-id 'base_sample_v1' --confirmed-by 'demo_user' --output $BaseLockManifest --force }
$baseLock = Get-Content -Path $BaseLockManifest -Raw -Encoding UTF8 | ConvertFrom-Json
if ($baseLock.base_lock_status -ne 'locked' -or $baseLock.base_id -ne 'base_sample_v1') {
    throw "Confirmed base lock was not created"
}
Invoke-Step 'build client base handoff with preview' { & $PythonExe $BaseHandoffBuilder --project-root $OutputDir --base-model $BaseModel --review-svg $PlanBaseClient --preview-png $PlanBaseClientPreview --validation $ValidationBase --output $BaseHandoff --title 'Demo Base Review Package' }
Invoke-Step 'build one-command base review package' { & $PythonExe $Workflow build-base-review --base-model $ExportedBaseModel --validation $ValidationExportedBase --output-dir $BaseReviewPackageDir --project-root $OutputDir --title 'Demo One-Command Base Review' --stem 'base_from_extraction_v1' }
Invoke-Step 'build needs brief' { & $PythonExe $Workflow build-needs-brief $NeedsResponse --output-dir $OutputDir --stem 'client' }
Invoke-Step 'plan isolated A/B/C scheme options' { & $PythonExe $Workflow plan-options $ExportedBaseModel $NeedsBriefJson --output-dir $SchemeOptionsDir --case-strategy $CaseStrategy --base-fidelity-report $BaseFidelityReport }
Invoke-Step 'reject draft with unresolved placements' { & $PythonExe $Workflow render-scheme-draft $ExportedBaseModel $PlannedSchemeAIntent --output-dir $BlockedDraftDir --version 'scheme_A_v1' } @(2)
$blockedDraft = Get-Content -Path $BlockedDraftReport -Raw -Encoding UTF8 | ConvertFrom-Json
if ($blockedDraft.status -ne 'blocked_unresolved_placement') {
    throw "Unresolved placement gate did not block the draft"
}
Invoke-Step 'resolve validated placement sample' { & $PythonExe $Workflow resolve-layout $BaseModel $PlacementSampleIntent --output-dir $PlacementDemoDir --version 'placement_sample' }
Invoke-Step 'resolve validated placement sample B' { & $PythonExe $Workflow resolve-layout $BaseModel $PlacementSampleIntentB --output-dir $PlacementDemoDir --version 'placement_sample_b' }
Invoke-Step 'resolve validated placement sample C' { & $PythonExe $Workflow resolve-layout $BaseModel $PlacementSampleIntentC --output-dir $PlacementDemoDir --version 'placement_sample_c' }
$placement = Get-Content -Path $PlacementReport -Raw -Encoding UTF8 | ConvertFrom-Json
if ($placement.layout_gate -ne 'ready' -or $placement.placed_object_count -ne 1) {
    throw "Placement resolver did not produce one ready object"
}
Invoke-Step 'render resolved placement sample' { & $PythonExe $Workflow render-scheme-draft $BaseModel $ResolvedPlacementIntent --output-dir $PlacementDemoDir --version 'placement_sample' }
$placementDraft = Get-Content -Path $PlacementDraftReport -Raw -Encoding UTF8 | ConvertFrom-Json
if ($placementDraft.status -ne 'draft_rendered_pending_review') {
    throw "Resolved placement did not render a deterministic draft"
}
Invoke-Step 'build same-scale scheme review package' { & $PythonExe $Workflow build-scheme-review $BaseModel $ResolvedPlacementIntent $ResolvedPlacementIntentB $ResolvedPlacementIntentC --output-dir $SchemeReviewDir }
$schemeReview = Get-Content -Path $SchemeReviewManifest -Raw -Encoding UTF8 | ConvertFrom-Json
if ($schemeReview.status -ne 'ready' -or $schemeReview.options.Count -ne 3 -or -not $schemeReview.same_scale) {
    throw "Scheme review package did not pass shared-scale checks"
}
Invoke-Step 'apply cross-scheme client feedback' { & $PythonExe $Workflow apply-scheme-feedback $BaseModel $ResolvedPlacementIntent $ResolvedPlacementIntentB $SchemeFeedbackSample --output-dir $FeedbackDemoDir }
$feedbackMigration = Get-Content -Path $FeedbackMigrationReport -Raw -Encoding UTF8 | ConvertFrom-Json
if ($feedbackMigration.status -ne 'applied' -or -not $feedbackMigration.new_object_id) {
    throw "Cross-scheme feedback migration did not produce a validated object"
}
Invoke-Step 'apply move-object feedback' { & $PythonExe $Workflow apply-scheme-feedback $BaseModel $ResolvedPlacementIntentB $ResolvedPlacementIntentB $MoveFeedbackSample --output-dir $FeedbackDemoDir }
Invoke-Step 'apply rotate-object feedback' { & $PythonExe $Workflow apply-scheme-feedback $BaseModel $ResolvedPlacementIntent $ResolvedPlacementIntent $RotateFeedbackSample --output-dir $FeedbackDemoDir }
Invoke-Step 'apply remove-object feedback' { & $PythonExe $Workflow apply-scheme-feedback $BaseModel $ResolvedPlacementIntentC $ResolvedPlacementIntentC $RemoveFeedbackSample --output-dir $FeedbackDemoDir }
Invoke-Step 'apply replace-object feedback' { & $PythonExe $Workflow apply-scheme-feedback $BaseModel $ResolvedPlacementIntent $ResolvedPlacementIntentB $ReplaceFeedbackSample --output-dir $FeedbackDemoDir }
foreach ($reportPath in @($MoveFeedbackReport, $RotateFeedbackReport, $RemoveFeedbackReport, $ReplaceFeedbackReport)) {
    $editReport = Get-Content -Path $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($editReport.status -ne 'applied') {
        throw "Furniture feedback action failed: $reportPath"
    }
}
Invoke-Step 'register accepted scheme B version' { & $PythonExe $Workflow scheme-history $SchemeHistory register $ResolvedPlacementIntentB --status accepted }
Invoke-Step 'register accepted migrated scheme B version' { & $PythonExe $Workflow scheme-history $SchemeHistory register $MigratedSchemeB --status accepted }
Invoke-Step 'register candidate moved scheme B version' { & $PythonExe $Workflow scheme-history $SchemeHistory register $MovedSchemeB --status candidate }
Invoke-Step 'activate migrated scheme B version' { & $PythonExe $Workflow scheme-history $SchemeHistory activate 'sample_b_v2_layout_v1' }
Invoke-Step 'rollback active scheme B version' { & $PythonExe $Workflow scheme-history $SchemeHistory activate 'placement_sample_b_layout_v1' }
Invoke-Step 'branch from accepted scheme B version' { & $PythonExe $Workflow scheme-history $SchemeHistory branch 'sample_b_v2_layout_v1' 'sample_b_alt_v1' --output-intent $SchemeHistoryBranch }
Invoke-Step 'reject moved scheme B version' { & $PythonExe $Workflow scheme-history $SchemeHistory set-status 'sample_b_move_v2_layout_v1' rejected }
Invoke-Step 'block branch from rejected version' { & $PythonExe $Workflow scheme-history $SchemeHistory branch 'sample_b_move_v2_layout_v1' 'sample_b_rejected_child_v1' --output-intent $RejectedHistoryChild } @(2)
$historyData = Get-Content -Path $SchemeHistory -Raw -Encoding UTF8 | ConvertFrom-Json
if ($historyData.active_versions.'方案 B' -ne 'placement_sample_b_layout_v1' -or (Test-Path $RejectedHistoryChild)) {
    throw "Scheme history rollback or rejected-parent gate failed"
}
Invoke-Step 'build visual handoff pending style' { & $PythonExe $Workflow build-visual-handoff --base-model $BaseModel --base-lock $BaseLockManifest --scheme-intent $ResolvedPlacementIntentB --stage deep --review-manifest $SchemeReviewManifest --history $SchemeHistory --needs-brief $NeedsBriefJson --output-dir $VisualHandoffNeedsStyleDir }
$handoffNeedsStyle = Get-Content -Path $VisualHandoffNeedsStyle -Raw -Encoding UTF8 | ConvertFrom-Json
if ($handoffNeedsStyle.status -ne 'needs_style_confirmation' -or $handoffNeedsStyle.generation_gate -ne 'closed') {
    throw "Visual handoff did not close the gate for missing style confirmation"
}
Invoke-Step 'build ready visual handoff' { & $PythonExe $Workflow build-visual-handoff --base-model $BaseModel --base-lock $BaseLockManifest --scheme-intent $ResolvedPlacementIntentB --stage deep --review-manifest $SchemeReviewManifest --history $SchemeHistory --needs-brief $NeedsBriefJson --style-brief $VisualStyleBrief --output-dir $VisualHandoffReadyDir }
$handoffReady = Get-Content -Path $VisualHandoffReady -Raw -Encoding UTF8 | ConvertFrom-Json
if ($handoffReady.status -ne 'ready' -or $handoffReady.generation_gate -ne 'open' -or -not (Test-Path $VisualGenerationPrompt)) {
    throw "Visual handoff did not open after style confirmation"
}
Invoke-Step 'build ready quick visual handoff from locked base' { & $PythonExe $Workflow build-visual-handoff --base-model $BaseModel --base-lock $BaseLockManifest --scheme-intent $ResolvedPlacementIntentB --stage quick --needs-brief $NeedsBriefJson --style-brief $VisualStyleBrief --output-dir $VisualHandoffQuickDir }
$handoffQuick = Get-Content -Path $VisualHandoffQuick -Raw -Encoding UTF8 | ConvertFrom-Json
if ($handoffQuick.status -ne 'ready' -or $handoffQuick.stage -ne 'quick' -or $handoffQuick.structure_lock.base_lock_status -ne 'locked') {
    throw "Quick visual handoff did not inherit the locked base"
}
Invoke-Step 'reject changed base behind locked id' { & $PythonExe $Workflow build-visual-handoff --base-model $ProblemModel --base-lock $BaseLockManifest --scheme-intent $ResolvedPlacementIntentB --stage quick --needs-brief $NeedsBriefJson --style-brief $VisualStyleBrief --output-dir $VisualHandoffTamperedDir } @(2)
$handoffTampered = Get-Content -Path $VisualHandoffTampered -Raw -Encoding UTF8 | ConvertFrom-Json
if ($handoffTampered.status -ne 'blocked' -or $handoffTampered.blockers -notcontains 'base model content differs from the locked base hash') {
    throw "Visual handoff did not reject changed content behind a locked base id"
}
Invoke-Step 'build same-canvas concept review aids' { & $PythonExe $Workflow review-concept-output --base-lock $BaseLockManifest --generated-image $PlanBaseClientPreview --output-dir $ConceptReviewDir --review-result passed --notes 'deterministic stand-in for pipeline regression' }
$conceptReview = Get-Content -Path $ConceptReviewReport -Raw -Encoding UTF8 | ConvertFrom-Json
if ($conceptReview.status -ne 'reviewed_passed' -or -not $conceptReview.canvas_match) {
    throw "Concept output review did not preserve the locked canvas"
}
Invoke-Step 'reject mismatched concept canvas' { & $PythonExe $ConceptOutputReview --base-lock $BaseLockManifest --generated-image $PlanBaseClientPreviewSmall --output-dir $ConceptReviewMismatchDir } @(2)
$conceptReviewMismatch = Get-Content -Path $ConceptReviewMismatchReport -Raw -Encoding UTF8 | ConvertFrom-Json
if ($conceptReviewMismatch.status -ne 'rejected_canvas_mismatch' -or $conceptReviewMismatch.canvas_match) {
    throw "Concept output review did not reject the mismatched canvas"
}
Invoke-Step 'build review package after feedback' { & $PythonExe $Workflow build-scheme-review $BaseModel $ResolvedPlacementIntent $MigratedSchemeB $ResolvedPlacementIntentC --output-dir $UpdatedSchemeReviewDir }
$updatedReview = Get-Content -Path $UpdatedSchemeReviewManifest -Raw -Encoding UTF8 | ConvertFrom-Json
if ($updatedReview.status -ne 'ready' -or $updatedReview.options.Count -ne 3) {
    throw "Updated scheme review package did not pass"
}
Invoke-Step 'render exported base SVG' { & $PythonExe $Renderer $ExportedBaseModel $PlanExportedBase $ValidationExportedBase }
Invoke-Step 'render scheme A SVG' { & $PythonExe $Renderer $SchemeA $PlanSchemeA $ValidationSchemeA }
Invoke-Step 'render problem SVG' { & $PythonExe $Renderer $ProblemModel $PlanProblem $ValidationProblem }
Invoke-Step 'render door swing SVG' { & $PythonExe $Renderer $DoorSwingModel $PlanDoorSwing $ValidationDoorSwing }
Invoke-Step 'render island move SVG' { & $PythonExe $Renderer $IslandMoveModel $PlanIslandMove $ValidationIslandMove }
Invoke-Step 'render arc partition SVG' { & $PythonExe $Renderer $ArcPartitionModel $PlanArcPartition $ValidationArcPartition }
Invoke-Step 'update project state' { & $PythonExe $StateUpdater --output $ProjectState --base-model $ExportedBaseModel --base-validation $ValidationExportedBase --base-version base_from_extraction_v1 --scheme-a-model $SchemeA --scheme-a-validation $ValidationSchemeA --scheme-a-version scheme_A_v1 --problem-validation $ValidationProblem --base-source-quality $SourceQualityExportedBase --base-source-extraction $SourceExtractionValidation --needs-brief $NeedsBriefJson --option-plan $SchemeOptionPlan }

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

Write-Host '== dimension anchor confirmation apply'
& $PythonExe $DimensionAnchorConfirmationApplier $SourceExtractionPackage $DimensionAnchorChecklistJson $DimensionAnchorConfirmationResponse $DimensionAnchorConfirmedPackage $DimensionAnchorConfirmationApplyReport --version source_extraction_anchors_confirmed_v1
& $PythonExe $SourceExtractionValidator $DimensionAnchorConfirmedPackage $DimensionAnchorConfirmedValidation
& $PythonExe $DimensionAnchorReviewRenderer $DimensionAnchorConfirmedPackage $DimensionAnchorReviewSvg

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
Write-Host $DimensionAnchorConfirmedPackage
Write-Host $DimensionAnchorConfirmationApplyReport
Write-Host $DimensionAnchorConfirmedValidation
Write-Host $DimensionAnchorReviewSvg
Write-Host $ExportedBaseModel
Write-Host $ValidationExportedBase
Write-Host $ExportedBaseValidation
Write-Host $FailedBaseExportValidation
Write-Host $PlanBase
Write-Host $PlanBaseClient
Write-Host $PlanBaseClientPreview
Write-Host $BaseHandoff
Write-Host $BaseReviewPackageDir
Write-Host $NeedsBriefJson
Write-Host $NeedsBriefMd
Write-Host $SchemeOptionPlan
Write-Host $SchemeOptionPlanMd
Write-Host $PlannedSchemeAIntent
Write-Host $BlockedDraftReport
Write-Host $PlanExportedBase
Write-Host $PlanSchemeA
Write-Host $PlanProblem
Write-Host $PlanDoorSwing
Write-Host $PlanIslandMove
Write-Host $PlanArcPartition
Write-Host $ProjectState

# Demo intentionally runs negative samples; reaching this point means required steps passed.
exit 0
