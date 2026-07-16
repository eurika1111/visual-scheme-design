# Residential Design Knowledge

Use this reference after the residential base is confirmed and needs are being translated into differentiated, reviewable options. Use it for design programming and comparison, not for geometry authority or construction compliance.

## Contents

- Evidence levels
- Needs programming
- Adjacency and conflict mapping
- Option construction
- Evaluation rubric
- Alteration and buildability tiers
- Decision output

## Evidence Levels

Label each important design claim before using it:

- `confirmed_fact`: visible in accepted source data or explicitly confirmed by the user.
- `hard_constraint`: must remain true for an option to survive.
- `project_assumption`: reasonable but still awaiting confirmation.
- `design_heuristic`: professional guidance used for comparison, not a code requirement.
- `reference_standard`: sourced numerical guidance whose jurisdiction and edition are recorded.
- `site_verification`: cannot be resolved safely without measurement, property information, or a qualified professional.

Never present a heuristic or unsourced number as a legal, structural, fire, accessibility, or construction requirement. If jurisdiction, edition, wall status, service route, or site dimension is unknown, create a confirmation item.

When a decision benefits from external knowledge, extract a transferable case strategy or named professional insight according to `professional-knowledge-sourcing.md`. When option comparison needs explicit relationship, access, furniture-use, or distinctness checks, use `residential-computational-design.md` rather than expanding the rubric informally.

Create and review each option's design argument according to `scheme-logic-and-visual-plausibility.md`. Treat logical coherence and visible proof as the bridge between needs programming and image generation.

## Needs Programming

Translate the needs conversation into a compact program before creating options:

```json
{
  "residents_and_routines": [],
  "required_spaces": [],
  "support_function_inventory": [],
  "priority_outcomes": [],
  "pain_points": [],
  "must_keep": [],
  "forbidden_or_sensitive": [],
  "acceptable_tradeoffs": [],
  "alteration_tolerance": "low|medium|high|uncertain",
  "budget_tolerance": "controlled|balanced|key_investment|uncertain",
  "style_signals": [],
  "disliked_signals": [],
  "unresolved_questions": []
}
```

Separate the user's desired outcome from a proposed solution. For example, store “more shared cooking space” as the need and “add an island” as one candidate response.

Build `support_function_inventory` only from relevant household routines and affected areas. Consider laundry/drying, refrigerator and food storage, waste, cleaning supplies, entry shoes/coats, linen/luggage, small appliances, child/elder/pet items, and maintenance access when they matter. Map each retained item to a location and routine; do not turn the inventory into a universal checklist or automatic blocker.

## Adjacency And Conflict Mapping

For spaces or activities affected by the scheme, record relationships as:

- `required_near`: separation would defeat the function.
- `preferred_near`: proximity improves daily use.
- `neutral`: no meaningful relationship.
- `preferred_apart`: separation improves privacy, noise, smell, or circulation.
- `must_separate`: combining the functions violates a hard constraint.

Record the reason and evidence level. Do not invent adjacency from a generic room-type template when the user's routine says otherwise.

Use a conflict list for competing goals:

```text
goal A: larger shared living area
goal B: retain an enclosed study
conflict: both require the same daylight-facing zone
decision variable: movable partition / reduced study size / unchanged layout
options compared: [approved option IDs]
```

## Option Construction

Build options from decisions, not style names. Give every option:

- one primary user problem
- one to three linked obligations that must not be sacrificed
- one spatial strategy
- one storage or furniture strategy
- one circulation consequence
- one alteration tier
- one visual direction
- one explicit tradeoff
- required validation checks
- one to three concurrent-use scenarios for affected core spaces when simultaneous activities matter
- affected daylight, glare, ventilation/exhaust, privacy, noise, or odor relationships when relevant
- a compact scheme logic manifest and the visible proof the final view must show

Require at least two meaningful differences between options from this list:

- functional zoning
- adjacency
- circulation
- storage strategy
- kitchen and dining relationship
- privacy and openness
- furniture organization
- alteration scope
- material and lighting direction
- cost and buildability risk

Replacing colors or furniture models alone does not create a new spatial option.

Derive the user-approved number of options from different responses to the conflict variables. Assign alteration tier after the core move is defined; do not use low/medium/high risk as fixed A/B/C archetypes.

Treat any inherited option plan that maps A/B/C to fixed low/medium/high risk tiers as stale strategy evidence. Keep useful needs and constraints, but rebuild directions from the current conflict variables and obtain user approval before scheme work.

## Evaluation Rubric

Evaluate each option on a 0-3 scale and attach evidence:

- `0`: fails a hard constraint or has a blocking unknown.
- `1`: weak; substantial compromise or repair is required.
- `2`: workable; tradeoffs are visible and manageable.
- `3`: strong for the confirmed need and current evidence.

Score only relevant dimensions:

| Dimension | Question |
|---|---|
| hard constraints | Does the option preserve every confirmed non-negotiable? |
| daily routines | Does it improve the routines named by the user? |
| functional completeness | Are required living, sleeping, kitchen, bathroom, work, child, elder, guest, or storage functions retained? |
| adjacency | Are important activities placed together or separated for a stated reason? |
| circulation | Are entries, doors, main paths, and furniture relationships plausible? |
| storage | Is storage placed where the relevant activity occurs without obstructing use? |
| support functions | Are the relevant laundry, cleaning, food, waste, entry, linen, child, elder, pet, or maintenance needs placed in the daily routine? |
| concurrent use | Can the named simultaneous activities coexist in the affected core space? |
| environmental comfort | Are relevant daylight, glare, ventilation/exhaust, privacy, noise, and odor effects handled or traded off honestly? |
| alteration risk | Is the proposed change proportionate to the user's tolerance and available evidence? |
| budget and buildability | Is the concept plausibly achievable within the expressed budget tier? |
| option distinctness | Does it test a genuinely different decision? |

Do not total scores mechanically when one dimension contains a hard failure. First reject or repair blockers, then compare the surviving design arguments and tradeoffs. Use the visual plausibility quality review instead of manufacturing a single objective winner.

## Alteration And Buildability Tiers

- `low`: furniture, storage, styling, lighting intent, and reversible elements; base structure remains unchanged.
- `medium`: local partitions, opening candidates, kitchen/dining reconfiguration, or service-sensitive furniture; require object operations and targeted checks.
- `high`: major reorganization, demolition candidates, wet-zone movement, uncertain structural work, or complex custom construction; present as exploratory until feasibility is confirmed.

For every medium or high change, state:

- what changes
- why it helps
- what evidence supports it
- what may block it
- what must be measured or professionally verified

## Decision Output

Present comparison in this order:

1. hard-constraint pass/fail
2. primary problem solved
3. meaningful spatial differences
4. tradeoffs and unresolved assumptions
5. alteration and budget risk
6. required geometry or site validation
7. recommendation with confidence

Keep facts, inference, and recommendation visibly separate. A visually exciting option with unresolved structural, service, clearance, or budget assumptions is an exploration candidate, not the default recommendation.
