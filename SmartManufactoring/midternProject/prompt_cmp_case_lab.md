# AI Build Prompt: SSMC CMP Dispatching Case Lab

Build a premium, English-language web application that fully simulates the SSMC CMP dispatching case as an interactive operations lab. This app should feel like a polished digital case-study product, not a classroom spreadsheet and not a toy animation.

This version is intentionally more ambitious than a simple 5-station line simulator. It must model the actual case structure of:

- `Sort`
- `CMP`
- `Clean`
- finite intermediate resources
- queue-time windows
- route-dependent cleaners
- water tank constraints
- cassette constraints
- changeovers
- push vs pull dispatching logic

At the same time, it must keep the experimental rigor of the original homework:

- fixed random schedules
- controlled A/B comparison
- scenario tabs
- reproducible results
- chartable outputs
- daily logs

The final result should feel like a serious case-lab app for manufacturing strategy, with strong storytelling, rigorous simulation logic, and high-end interface quality.

## Product Goal

Create an app that helps users understand the real managerial question behind the case:

> The core issue is not only which lot should run next, but which lot should be released now so that downstream capacity, queue-time constraints, buffer resources, and near-future feasibility remain under control.

The app must let users explore how `Push` and `Pull` dispatching perform under realistic CMP-stage constraints and under multiple controlled experiment scenarios derived from the case.

## Language and UX Requirements

The app UI must be entirely in English:

- page titles
- buttons
- filter labels
- legends
- tooltips
- chart titles
- table headers
- run summaries
- scenario descriptions

The overall feel should be premium, analytical, and industrial. It should look like a modern operations intelligence product for a semiconductor fab.

## Core Design Philosophy

This app has two layers and both must be visible in the final product:

1. `Case-faithful simulation layer`
   Model the real CMP stage with its coupled resources and constraints.

2. `Homework-style experiment layer`
   Package the case into controlled experiments with locked schedules, scenario tabs, comparisons, and report-ready metrics.

Do not build only one of these two layers. The value of this version is the combination.

## Hard Case Facts That Must Be Modeled

Treat the following as non-negotiable case facts.

### Stage Structure

The CMP stage includes:

1. `Sort`
2. `CMP`
3. `Clean`

### Sort

- There are `4 identical sorters`
- Sort converts wafers from normal cassettes into `Teflon cassettes`
- Sort time is approximately `3 minutes per lot`

### CMP

- CMP process time is approximately `45 minutes per lot`
- CMP tools are grouped as:
  - `APT`: `4 tools`
  - `APX`: `15 tools`
  - `APW`: `15 tools`
- CMP supports a `serial batch size of 4`
- Continuous cascading can save approximately `3 minutes per subsequent lot`
- Lot size is up to `25 wafers`

### Clean

- Clean time is approximately `30 minutes per lot`
- Cleaner routing is:
  - `AST/ASX` for lots from `APT/APX`
  - `ASW` for lots from `APW`
- `ASW` contains two sub-routes:
  - `ASW_1` for `NH4OH`
  - `ASW_2` for `HF`

### Queue-Time Constraints

Model the post-CMP queue-time windows exactly:

- `APT/APX -> AST/ASX`: maximum `6 hours`
- `APW -> ASW`: maximum `2 hours`

If a lot exceeds its queue-time limit, treat it as a serious service failure. The simulator should mark it clearly as a violation and optionally classify it as rework/scrap risk.

### Water Tanks

Model post-CMP water tank storage exactly:

- `8 water tanks`
- total capacity `52 lots`
- `6 tanks` with capacity `6 lots` each
- `2 tanks` with capacity `8 lots` each

Compatibility rule:

- `APT/APX` lots may share the same tank type
- `APW` lots may share the same tank type
- `APT/APX` lots and `APW` lots may not occupy the same tank simultaneously

Tank reassignment must include changeover time:

- tank arrangement changeover = `0.5 hours`

### Cleaner and Route Changeovers

Model cleaner flexibility and switching cost:

- some `ASX/ASW` switches take about `2 to 6 hours`
- `ASW_1 <-> ASW_2` switching takes `6 hours`
- more generally, cleaner-related changeovers are in the range of roughly `1.5 to 6 hours`

### Teflon Cassettes

Model shared cassette constraints:

- there are `200 shared Teflon cassettes`
- they are a finite shared resource across the CMP stage

### Structural Insights the App Must Respect

The case is not a local sequencing problem. It is a coupled stage-level control problem. The app must reflect these design principles:

- dispatch the stage, not the individual machine
- release work based on downstream feasibility
- protect bottleneck CMP capacity first
- treat water tanks as strategic resources, not passive storage
- consider changeovers in near-future planning
- preserve responsiveness before lots become locked into post-sort FIFO behavior
- exploit batching gains only when downstream feasibility is still safe

## Simulation Assumptions for Missing Inputs

The case documents do not provide every low-level distribution needed for a complete software simulation. Do not hide assumptions.

Any assumption not directly given by the case must be:

- explicit
- visible in the UI or run metadata
- fixed inside each experiment preset
- reproducible through locked seeds

Default assumptions may be preconfigured, but they must be documented clearly in an `Assumptions` panel or expandable drawer.

## Simulation Engine Requirements

This app should use a `discrete-event` or `event-driven` simulation model with time resolution in minutes, not a crude once-per-day aggregate loop. The case depends on queue-time windows, tool states, tank availability, and changeovers, so the engine must be time-aware.

### Time Horizon

- run length: `200 days`
- operation mode: `24/7 continuous fab behavior`

### Lot-Level Entities

Each lot should have explicit attributes such as:

- `lotId`
- `release timestamp`
- `family`: `APT`, `APX`, or `APW`
- `clean route`
- `chemistry route` when relevant, especially `NH4OH` or `HF`
- `priority class`
- `due-date slack`
- `queue-time limit`
- `current location`
- `current cassette status`
- `current tank status`
- violation markers if any

### Resource Entities

Model at minimum:

- sorters
- CMP tools by group
- cleaners by route
- water tanks
- Teflon cassettes

### Recommended Queue-Time Interpretation

Unless there is a stronger implementation reason otherwise, interpret queue time as:

- `time from CMP completion to clean start`

If a different interpretation is used, the app must state it explicitly in the assumptions metadata.

### CMP Batch Logic

Model CMP as a serial-batch resource with batch size up to `4 lots`.

When compatible lots are processed continuously on the same tool without idle break, apply the cascading efficiency effect:

- each additional lot after the first may gain about `3 minutes` of effective overlap savings

The implementation may represent this as reduced incremental lot time or reduced cumulative batch duration, but it must be consistent across all scenarios and clearly documented.

## Dispatching Policies to Compare

The app must support at least two dispatching philosophies:

### Policy A: Push

Push should reflect the legacy/current-practice logic described in the case:

- release lots according to upstream availability or move targets
- allow upstream movement with limited downstream awareness
- do not deeply gate release by real-time tank/clean feasibility

Push should not be intentionally sabotaged. It should be a plausible baseline, not a strawman.

### Policy B: Pull

Pull should reflect the managerial logic proposed in the case:

- release lots only when downstream feasibility is acceptable
- consider current cleaner capacity state
- consider water tank availability and compatibility
- consider queue-time risk
- consider cassette availability
- consider anticipated near-future changeover implications
- favor stage-level flow stability over purely local dispatch convenience

### Optional Advanced Pull Layer

If helpful, the app may add a more advanced pull mode such as:

- `Pull + Lookahead`

But the baseline comparison must always include clear `Push` vs `Pull`.

## Homework-Style Experiment Framework

This is where the case app should borrow the spirit of the original assignment.

The app must present the case as a controlled experiment lab with:

- fixed random seeds
- controlled scenario presets
- reproducible A/B policy comparisons
- experiment tabs
- report-ready charts and tables

## Locked Schedule Rules

The simulation must not redraw randomness every time the user changes a selection.

Generate locked schedules on initial load.

### Required Locked Data

For each experiment preset and each variation preset, pre-generate and lock:

- lot release schedule
- lot attribute schedule
- stochastic process-time draws
- stochastic changeover-time draws
- any burst-arrival pattern
- any urgency assignment

### Fair Comparison Rules

Within the same experiment preset:

- `Push` and `Pull` must use the exact same lot arrivals
- `Push` and `Pull` must use the exact same lot identities
- `Push` and `Pull` must use the exact same stochastic time draws

Across all tabs:

- each experiment preset may have its own locked scenario schedule because the purpose of each preset is different
- but once generated, that scenario schedule must remain fixed and reproducible

Animation playback must replay already computed simulation outcomes. It must not generate new outcomes.

## Variation Presets

To preserve the spirit of the homework’s large-variation versus small-variation comparison, include two variability modes for the case lab.

These are simulation assumptions rather than explicit case facts, so they must be clearly labeled as experiment presets.

### Small Variation

Use tighter operational noise:

- daily release multiplier range: `0.90 to 1.10`
- process-time jitter: approximately `±5%`
- changeover draws biased toward the lower end of the valid range
- smoother within-day lot arrivals
- due-date slack jitter: approximately `±10%`

### Large Variation

Use broader operational noise:

- daily release multiplier range: `0.75 to 1.25`
- process-time jitter: approximately `±15%`
- changeover draws may span the full valid range
- burstier within-day lot arrivals
- due-date slack jitter: approximately `±25%`

Do not treat these as hidden implementation details. They are part of the experimental design and should be visible to the user.

## Five Required Experiment Presets

Use `5 experiment tabs`, but unlike the original 5-station homework, these tabs now represent five case-derived CMP scenarios.

Each preset must have a clear goal, a fixed setup, and a report-ready description.

### Experiment 1: Baseline Stage Dynamics

Purpose:

- establish the normal case-study baseline
- compare Push vs Pull under balanced conditions

Default setup:

- product-family mix:
  - `APT: 15%`
  - `APX: 50%`
  - `APW: 35%`
- APW chemistry split:
  - `NH4OH: 60%`
  - `HF: 40%`
- urgent lots: `5%`
- standard tank compatibility rules
- standard cleaner flexibility

### Experiment 2: APW Queue-Time Stress

Purpose:

- stress the most queue-time-sensitive path
- expose the risk of blocking when APW output overwhelms ASW feasibility

Default setup:

- product-family mix:
  - `APT: 10%`
  - `APX: 30%`
  - `APW: 60%`
- APW chemistry split:
  - `NH4OH: 50%`
  - `HF: 50%`
- urgent lots: `5%`
- same hard resource counts as the case
- emphasize the `2-hour` APW-to-ASW queue-time constraint

### Experiment 3: Cleaner Changeover Stress

Purpose:

- test whether pull logic can reduce loss from reactive cleaner switching
- show why near-future planning matters

Default setup:

- product-family mix:
  - `APT: 15%`
  - `APX: 40%`
  - `APW: 45%`
- APW chemistry split alternates in a forcing pattern to trigger `ASW_1` and `ASW_2` tension
- urgent lots: `5%`
- cleaner switches must obey their full changeover durations
- the scenario should visibly demonstrate the cost of late reconfiguration

### Experiment 4: Water Tank and Cassette Stress

Purpose:

- show that finite intermediate resources can block the entire stage
- highlight resource coupling between post-CMP storage and carrier circulation

Default setup:

- product-family mix:
  - `APT: 20%`
  - `APX: 45%`
  - `APW: 35%`
- urgent lots: `5%`
- within-day arrivals should be more clustered than baseline
- enforce all water tank compatibility rules strictly
- enforce the shared `200` Teflon cassette limit strictly
- show how tank occupancy and cassette scarcity can reduce CMP effectiveness

### Experiment 5: Urgent Lot Responsiveness

Purpose:

- show why decisions made before or at sort matter
- compare responsiveness before lots become hard to reprioritize downstream

Default setup:

- use the same product-family mix as Experiment 1
- APW chemistry split same as Experiment 1
- urgent lots: `20%`
- tighter due-date slack than baseline
- highlight how post-sort FIFO behavior reduces agility

## Required Outputs and Metrics

Each experiment tab must show report-ready outputs for the currently selected variation and policy state.

### Minimum KPI Cards

Show at least:

- `Total Throughput`
- `Average Cycle Time`
- `Average Queue Time`
- `Queue-Time Violations`
- `Average WIP`
- `Average Water Tank Occupancy`
- `Cassette Utilization`
- `CMP Utilization`
- `Cleaner Utilization`

### Charts

Include at minimum:

1. `Cumulative Throughput Over Time`
2. `WIP by Stage Over Time`
3. `Queue-Time Violation Trend`
4. `Resource Utilization by Group`
5. `Water Tank Occupancy`
6. `Teflon Cassette Usage`

### Tables

Provide a detailed log table that can be filtered or scrolled. Include fields such as:

- day
- timestamp
- lotId
- lot family
- route
- priority
- current event
- selected tool
- selected cleaner
- tank assignment
- queue-time age
- violation status
- cycle-time status

Also provide a daily summary table with:

- lots released
- lots completed
- WIP totals
- queue-time violations
- average tank occupancy
- average cassette usage
- resource utilizations

## Recommended Compare Modes

The app should support one or both of these views:

1. `Single Policy View`
   Explore one policy at a time with full detail.

2. `A/B Compare View`
   Show `Push` and `Pull` side by side under the exact same locked schedule.

If only one view is implemented, prefer the compare view because the experimental value of the app depends on controlled comparison.

## Narrative and Storytelling Layer

This app should teach the case, not just simulate it.

Include short English narrative text blocks that explain:

- why CMP is difficult
- why finite buffers matter
- why APW is especially sensitive
- why changeovers matter
- why Push can overload downstream feasibility
- why Pull is a stage-level control idea, not just a different priority rule

These short narratives should feel editorial and clear, not academic and dense.

## Visual Design Direction

Aim for a premium industrial-lab interface with a semiconductor-operations feel.

Good direction:

- clean, dark-neutral or stone-neutral base
- restrained metallic or process-inspired accents
- subtle gradients and layered panels
- strong typography hierarchy
- technical but elegant data graphics
- high-contrast dashboards that still feel calm

Do not make it look like:

- a default admin template
- a spreadsheet pasted into a browser
- a neon cyberpunk gimmick
- a casino interface
- a childish factory game

## Animation and Motion Direction

Motion should improve comprehension and quality perception, not distract from the simulation.

### Suggested Animated Elements

- lots moving through `Sort -> CMP -> Tank -> Clean`
- active tool highlighting when a lot starts or finishes processing
- tank occupancy smoothly filling and draining
- cassette circulation shown through subtle token movement
- queue-time risk states shifting from normal to warning to violation
- side-by-side compare transitions that preserve context
- chart draw-ins when results first appear

### Interaction Quality

Use restrained and thoughtful motion:

- smooth but not flashy
- precise timing
- no excessive particle noise
- no fake randomness in animation that conflicts with the actual data

### Recommended Playback Tools

Provide:

- `Run Simulation`
- `Replay Selected Day`
- `Replay Queue-Time Failure`
- `Focus on APW Route`

These tools should help the user understand why the system behaved the way it did.

## Control Panel Requirements

At the top of the app, include controls such as:

- `Variation Preset`
  - `Small Variation`
  - `Large Variation`
- `Dispatch Policy`
  - `Push`
  - `Pull`
- `Compare Mode`
  - `Single`
  - `A/B`
- `Run Simulation`
- `Replay Day`
- `Reset to Locked Schedules`

If useful, also include:

- `Show Assumptions`
- `Show Event Timeline`
- `Highlight Violations`

## Acceptance Criteria

Treat the following as hard requirements:

1. The app models the real CMP stage structure: `Sort`, `CMP`, `Clean`, tanks, cassettes, and route constraints.
2. The simulation is event-driven enough to support queue-time windows and changeovers meaningfully.
3. `Push` and `Pull` are both implemented as serious, comparable policies.
4. All experiment presets use locked schedules and reproducible seeds.
5. Push vs Pull comparison inside the same experiment uses exactly the same underlying arrivals and stochastic draws.
6. Water tank compatibility and capacity limits are enforced.
7. Teflon cassette scarcity is enforced.
8. Queue-time violations are explicitly tracked and surfaced.
9. Cleaner and tank changeovers consume time and affect feasibility.
10. CMP batching/cascading effects are represented consistently.
11. The app contains 5 case-derived experiment tabs, not just one generic view.
12. All visible product UI is in English.
13. The app looks premium and intentional, not merely functional.
14. Motion supports understanding without altering the underlying numbers.

## What Not to Do

Do not:

- reduce the case to a simple linear 5-station toy model
- hide key assumptions that were invented for the simulator
- redraw randomness whenever the user switches controls
- fake Push by making it obviously foolish
- fake Pull by giving it impossible clairvoyance
- ignore tank compatibility
- ignore queue-time windows
- ignore changeovers
- build a flat spreadsheet-style interface with no product quality

## Final Build Instruction

Build a refined English-language digital case lab that simulates the SSMC CMP dispatching problem with real resource coupling, real control tradeoffs, and homework-level experimental rigor. The app should help a user both understand the case and analyze it through reproducible scenario experiments.
