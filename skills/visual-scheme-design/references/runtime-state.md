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
  "level": "L3",
  "base_level": "L3",
  "base_validation_status": "passed",
  "active_base": "base_v1",
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
- `active_option_level` and `active_option_validation_status` decide whether the selected option can enter stable deepening.
- A warning in one option must not downgrade the base model or contaminate other options.
- Switching active option updates `active_option`, `active_option_level`, `active_option_validation_status`, related files, and option registry only.
## Update rules

- Update state after a phase change, validation run, option status change, scheme migration, rollback, or delivery.
- Do not change `source_facts` through state.
- Do not mark `validation_status` as `passed` without a validation report or explicit manual check.
- If a base version changes, mark dependent schemes affected instead of silently carrying them forward.
- If an option is rejected, do not use it as a parent for later versions.
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

