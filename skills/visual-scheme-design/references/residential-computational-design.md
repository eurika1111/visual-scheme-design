# Residential Computational Design

Use this reference when explicit relationships help prevent an obvious spatial contradiction or keep the approved option set genuinely different. Apply computation as a guardrail for logical plausibility, not as proof that a visual proposal is mathematically optimal or construction-ready.

## Contents

- Feasibility, relationships, and access
- Furniture and concurrent use
- Constraint propagation and option distinctness
- Comparison output and scope boundary

## Core Sequence

```text
locked base
-> user problem and fixed relationships
-> feasible option operations
-> adjacency, access, and furniture-use checks
-> option distinctness
-> scheme logic manifest
-> visual plausibility review
```

Prefer transparent rules and bounded enumeration for ordinary residential layouts. Do not introduce formal optimization when a small number of understandable alternatives can be reviewed directly.

## Feasibility First

Reject or repair an option before comparison when it contains a confirmed contradiction:

- unauthorized base change
- missing required function
- blocked opening or destination
- furniture crossing structure or lacking a believable use side
- fixed-service or protected-object conflict
- core move that cannot be shown without contradicting the base

Use geometry and dimensions where they can establish these failures. When only visual evidence exists, label the review qualitative rather than inventing precision.

## Relationship Map

Represent relevant functions or activities as a small explained graph:

```json
{
  "from": "kitchen",
  "to": "dining",
  "relation": "required_near|preferred_near|neutral|preferred_apart|must_separate",
  "reason": "confirmed routine",
  "evidence": "confirmed_fact|user_preference|design_heuristic"
}
```

Create only relationships that change the option. The current user routine overrides a generic room-type template.

## Access And Circulation Story

Check named journeys rather than producing one abstract circulation score:

- entry to primary living space
- entry to bathroom and bedrooms
- kitchen to dining or serving position
- door approach and swing
- access to balcony, storage, work position, and major furniture
- child, elder, guest, or accessibility route when relevant to the brief

Record the result as `pass`, `warning`, `fail`, or `unknown`, with visible conflicts and evidence. Route length is optional; the main question is whether a user can understand and plausibly complete the journey.

## Furniture Use Logic

Check furniture as an activity relationship, not only as a collision rectangle:

- bed approach and storage access
- sofa orientation and conversation or viewing relationship
- dining seating, pull-out space, and serving route
- desk chair use side and daylight or privacy intent
- wardrobe, drawer, appliance, and cabinet opening side
- bathroom fixture access and sequence
- island or counter work side and passage relationship

Use exact clearance tools when available, but block any obvious visual contradiction even when no numeric threshold is known.

## Concurrent Use Scenarios

For an affected core space, test only one to three simultaneous activities that occur in the user's routine or carry the option's promise. Examples include:

- one person cooking while another opens the refrigerator
- dining chairs pulled out while the balcony route remains usable
- wardrobe open while bed-side access remains possible
- child or elder assistance while a bathroom fixture is in use

Record involved objects, active envelopes, named route, result, and evidence. Do not simulate every theoretical combination; target the conflict that could make the proposal feel obviously unworkable.

## Constraint Propagation

After a wall, opening, furniture, or fixed-zone change:

1. rerun affected opening and room-boundary checks
2. rerun door, collision, and named access checks
3. update the relationship map and furniture-use logic
4. mark the scheme logic manifest stale if its story changed
5. mark dependent drafts and image handoffs stale

Do not carry a passing visual review across a changed option version.

## Option Distinctness

Compare decisions rather than pixels, palettes, or furniture models. Use axes such as:

- primary user problem
- zoning and functional relationship
- circulation story
- storage and furniture-use strategy
- kitchen and dining relationship
- privacy and openness
- alteration scope
- explicit tradeoff

Require at least two meaningful changed axes and a different `core_move` or tradeoff. If only decorative language changes, label the outputs visual variants of one scheme.

## Comparison Output

For each surviving option report:

```text
primary problem
core move
main routine supported
relationship or circulation consequence
furniture-use consequence
concurrent-use consequence when relevant
fixed elements preserved
tradeoff
blocking unknowns
visual proof required
```

Do not force a weighted total. Recommend an option only when its logic is coherent and its tradeoff matches the user's priority. If options make different valid tradeoffs, present the choice instead of declaring a false optimum.

## Out Of Scope

Do not add genetic algorithms, NSGA-II, PSO, topology optimization, complex NURBS workflows, simulation engines, fabrication systems, or Rhino/Grasshopper/Dynamo dependencies merely to resemble a broad computational-design toolkit. Introduce a separate workflow only when the actual project requires it.
