# Runtime State

Use this reference when a space-scheme task spans multiple turns, creates files, has option versions, or depends on residential geometry validation.

## Purpose

State reduces token use and contamination. It stores the current project pointer so Codex does not reconstruct phase, option status, validation status, and latest action from long chat history.

State is a pointer, not the source of truth. Source facts, object models, operation logs, validation reports, generated images, and client-facing boards remain separate files or explicit conversation facts.

## Recommended location

For project-local work, prefer:

```text
outputs/project_state.json
```

For a narrower geometry-engine demo, a project may use:

```text
outputs/<project-name>/project_state.json
```

Do not store large object models inside state. Store file paths, IDs, status, and short notes.

## Minimal schema

```json
{
  "schema_version": "space_scheme_state_v1",
  "updated_at": "YYYY-MM-DD",
  "domain": "residential",
  "mode": "execute",
  "phase": "production",
  "interaction_context": "first_use",
  "interaction_checkpoint": "option_direction_confirmation",
  "awaiting_confirmation": "approve_or_edit_option_directions",
  "confirmed_checkpoints": ["welcome", "source_understanding", "base_confirmation", "needs_rounds"],
  "level": "L3",
  "base_level": "L3",
  "base_validation_status": "passed",
  "active_base": "base_v1",
  "base_lock_status": "locked",
  "base_lock_manifest": "outputs/base_versions/base_v1_lock.json",
  "active_option": "scheme_A_v1",
  "active_option_level": "L3",
  "active_option_validation_status": "passed",
  "validation_status": "passed",
  "last_action": "validate_geometry",
  "option_registry": [
    {
      "id": "方案 A",
      "version": "scheme_A_v1",
      "status": "保留",
      "parent": null,
      "notes": "selected for deepening"
    }
  ],
  "files": {
    "base_model": "outputs/base_versions/base_v1.json",
    "validation_report": "outputs/base_versions/base_v1_validation.json",
    "operation_log": "outputs/operation_logs/scheme_A.json"
  },
  "blockers": [],
  "evolution_flags": []
}
```


## Base gate and active option gate

Keep base readiness separate from the active scheme option:

- `base_level` and `base_validation_status` decide whether quick concepts can continue from the confirmed base.
- `base_lock_status` must be `locked` before residential quick concepts start.
- `active_option_level` and `active_option_validation_status` decide whether the selected option can enter stable deepening.
- A warning in one option must not downgrade the base model or contaminate other options.
- Switching active option updates `active_option`, `active_option_level`, `active_option_validation_status`, related files, and option registry only.

## Interaction gate

- `interaction_checkpoint` identifies the one user-visible decision currently active.
- `awaiting_confirmation` must be cleared by an explicit answer before moving to the next checkpoint.
- `confirmed_checkpoints` is append-only for the active branch. Returning to an earlier checkpoint creates a revised branch and invalidates dependent later confirmations.
- `继续` confirms only the next action previously stated; it does not clear multiple checkpoints.
- For `first_use` or `clean_test`, do not populate confirmations from prior conversation or prior generated schemes.
## Update rules

- Update state after a phase change, validation run, option status change, scheme migration, rollback, or delivery.
- Update interaction state before stopping at, and after resolving, every mandatory checkpoint.
- Do not change `source_facts` through state.
- Do not change or unlock an active residential base through state. Point to a newly confirmed base version after a specific user-requested correction.
- Do not mark `validation_status` as `passed` without a validation report or explicit manual check.
- If a base version changes, mark dependent schemes affected instead of silently carrying them forward.
- If an option is rejected, do not use it as a parent for later versions.
- Each residential option must record the same locked parent `base_id`; cross-option migration changes only the target option branch.
- Treat rollback as an active-version pointer change to an already accepted version; never overwrite or delete later files.
- Only `accepted` versions may become active or create branches. `candidate` versions require review, and `rejected` versions are terminal.
- Register a content hash for each version. Reusing one version ID with different content is a contamination error.
- A branch copies one accepted intent into a new candidate version with an explicit `parent_intent`; it does not inherit chat context or generated-image geometry.
- If no state file exists and the task is small, keep a compact inline state in the response instead of creating files.

## Runtime pattern

Use this sequence for multi-step work:

```text
read state if present
→ read only needed reference and data files
→ execute one current action
→ run deterministic checks when available
→ update state or inline registry
→ report concise result and next action
```

## Evolution flags

Use `evolution_flags` only to record possible future maintenance. Do not automatically restructure the skill during runtime.

Recommended flag shape:

```json
{
  "type": "token-heavy|ambiguous-routing|unstable-output|missing-script|repeated-manual-step",
  "location": "short file or phase name",
  "severity": "low|medium|high",
  "suggestion": "one short maintenance idea"
}
```

Only move an evolution flag into `SKILL.md` or references after the user approves maintenance work.

