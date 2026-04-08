# AI Build Prompt: 5-Station Production Line Simulation Dashboard

Build a polished, English-language web app that simulates a 5-station serial production line for a Smart Manufacturing case study. This is not a toy demo. The app must be scientifically consistent enough to support report writing and experiment comparison, while also feeling like a refined, modern product.

The outcome should be a high-quality simulation dashboard with clear English UI copy, deterministic experiment control, elegant motion, and rigorous data handling.

## Core Objective

Create a browser-based dashboard that simulates 200 days of production for a 5-station line under:

- 2 variation conditions: `Large Variation` and `Small Variation`
- 2 system conditions: `Push` and `Kanban`
- 5 experiments with different bottleneck positions

The app must let the user compare throughput, buffer WIP, and daily flow behavior across all experiments under the exact same locked random schedules.

## Non-Negotiable Interpretation of the Assignment

There is a source-label conflict in the original materials. Resolve it exactly like this:

- `Case (1)` = `Large Variation`
- `Case (2)` = `Small Variation`
- `Case (a)` = `Push`
- `Case (b)` = `Kanban`

Use this interpretation because the actual card-limit templates and the original prompt logic agree on:

- `Push`: Buffers 2-5 are unlimited
- `Kanban`: Buffers 2-5 are capped at 9

Do not invert these definitions.

Also treat spreadsheet-specific notes such as paste instructions, pink-cell hints, and embedded-formula warnings as spreadsheet workflow details, not simulation rules.

Do not implement a warm-up exclusion period. Simulate and log all days from Day 1 through Day 200.

## Product Framing

This app should feel like a well-designed analytical product, not a classroom spreadsheet clone. It must balance:

1. Experimental rigor
2. Visual clarity
3. High-end UI quality
4. Purposeful animation

The UI language must be English throughout:

- Buttons
- Labels
- Legends
- Chart titles
- Table headers
- Status text
- Tooltips
- Empty states

## Simulation Model

Model a production line with 5 single stations in strict series:

- `Station 1`
- `Station 2`
- `Station 3`
- `Station 4`
- `Station 5`

Jobs must flow in this order:

`Buffer 1 -> Station 1 -> Buffer 2 -> Station 2 -> Buffer 3 -> Station 3 -> Buffer 4 -> Station 4 -> Buffer 5 -> Station 5 -> Output`

Definitions:

- `Buffer 1` is the release buffer before Station 1 and may also be interpreted as the supplier side
- `Buffers 2-5` are intermediate WIP buffers
- `Output` is an infinite-capacity sink after Station 5
- Each station may process at most one batch per day
- Exactly one release batch is added to `Buffer 1` at the start of each day

## Experiment Matrix

You must support 5 experiments. The only difference between them is bottleneck position.

### Bottleneck Location by Experiment

- `Experiment 1`: bottleneck at `Station 5`
- `Experiment 2`: bottleneck at `Station 4`
- `Experiment 3`: bottleneck at `Station 3`
- `Experiment 4`: bottleneck at `Station 2`
- `Experiment 5`: bottleneck at `Station 1`

### Variation Rules

`Job Release` range for all cases:

- random integer from `3` to `13`, inclusive

`Large Variation`:

- normal stations: random integer from `7` to `13`, inclusive
- bottleneck station: random integer from `6` to `12`, inclusive

`Small Variation`:

- normal stations: random integer from `9` to `11`, inclusive
- bottleneck station: random integer from `8` to `10`, inclusive

### System Rules

`Push`:

- `Buffer 1 = Infinity`
- `Buffer 2 = Infinity`
- `Buffer 3 = Infinity`
- `Buffer 4 = Infinity`
- `Buffer 5 = Infinity`

`Kanban`:

- `Buffer 1 = Infinity`
- `Buffer 2 = 9`
- `Buffer 3 = 9`
- `Buffer 4 = 9`
- `Buffer 5 = 9`

### Official Case Mapping

- `(1)+(a)` = `Large Variation + Push`
- `(1)+(b)` = `Large Variation + Kanban`
- `(2)+(a)` = `Small Variation + Push`
- `(2)+(b)` = `Small Variation + Kanban`

## Scientific Control and Locked Random Data

This is critical. The app must preserve fair comparisons.

On initial load, pre-generate and lock the schedules used by the simulation. Do not regenerate them when the user switches tabs, changes dropdowns, replays animation, or reruns the view.

### Required Locked Schedules

Generate:

- one shared `200-day job release schedule`
- one locked `200-day Large Variation capacity schedule`
- one locked `200-day Small Variation capacity schedule`

Each day must contain:

- `jobRelease`
- `normalCaps`: an array of 4 integers
- `bnCap`: one integer for the bottleneck-capacity draw

### Comparison Rules

The app must preserve these controls exactly:

- The same `jobRelease` sequence must be used across all variations, all systems, and all 5 experiments
- `Push` and `Kanban` must use the exact same daily capacity draws within the same variation
- `Experiment 1-5` must use the exact same daily `normalCaps + bnCap` values, only changing the bottleneck insertion position
- Switching between `Push` and `Kanban` must never trigger new random draws
- Switching between experiments must never trigger new random draws
- Animation playback must replay precomputed results, not re-simulate with fresh randomness

## Capacity Construction by Experiment

For each day, start from:

- `jobRelease`
- `normalCaps` with length 4
- `bnCap` with length 1

To build the actual station capacities for a given experiment, insert `bnCap` into `normalCaps` at the bottleneck index.

### Required Insertion Indices

- `Experiment 1`: insert `bnCap` at index `4`
- `Experiment 2`: insert `bnCap` at index `3`
- `Experiment 3`: insert `bnCap` at index `2`
- `Experiment 4`: insert `bnCap` at index `1`
- `Experiment 5`: insert `bnCap` at index `0`

This means:

- `Experiment 1`: `[N, N, N, N, BN]`
- `Experiment 2`: `[N, N, N, BN, N]`
- `Experiment 3`: `[N, N, BN, N, N]`
- `Experiment 4`: `[N, BN, N, N, N]`
- `Experiment 5`: `[BN, N, N, N, N]`

### Explicit Station Ranges by Experiment

| Experiment | Bottleneck Station | Large Variation S1-S5 | Small Variation S1-S5 |
| --- | --- | --- | --- |
| 1 | S5 | 7-13, 7-13, 7-13, 7-13, 6-12 | 9-11, 9-11, 9-11, 9-11, 8-10 |
| 2 | S4 | 7-13, 7-13, 7-13, 6-12, 7-13 | 9-11, 9-11, 9-11, 8-10, 9-11 |
| 3 | S3 | 7-13, 7-13, 6-12, 7-13, 7-13 | 9-11, 9-11, 8-10, 9-11, 9-11 |
| 4 | S2 | 7-13, 6-12, 7-13, 7-13, 7-13 | 9-11, 8-10, 9-11, 9-11, 9-11 |
| 5 | S1 | 6-12, 7-13, 7-13, 7-13, 7-13 | 8-10, 9-11, 9-11, 9-11, 9-11 |

## Daily Simulation Algorithm

All values are integers. The simulation must run for exactly 200 days.

### Initial State Before Day 1

- `B1 = 0`
- `B2 = 0`
- `B3 = 0`
- `B4 = 0`
- `B5 = 0`
- `cumulativeOutput = 0`

### Start of Each Day

At the start of each day:

1. Add the day’s `jobRelease` to `Buffer 1`
2. Build the day’s station capacities using the selected variation schedule and experiment insertion logic

### Processing Order

You must process stations in this exact order:

- `Station 5`
- `Station 4`
- `Station 3`
- `Station 2`
- `Station 1`

### Processing Formula

For each station `i`, compute:

`Processed_i = min(StationCapacity_i, CurrentBufferWIP_i, NextBufferRemainingSpace)`

Where:

- `CurrentBufferWIP_i` is the current amount in `Buffer i`
- `NextBufferRemainingSpace` is:
  - `Infinity` for Station 5 because downstream is the output sink
  - otherwise `bufferCapacity(i+1) - currentWIP(i+1)`

### Immediate Update Rule

This must be implemented exactly and is one of the most important correctness conditions.

Inside the backward loop, as soon as `Processed_i` is computed, update state immediately:

- subtract `Processed_i` from `Buffer i`
- if `i < 5`, add `Processed_i` immediately to `Buffer i+1`
- if `i = 5`, add `Processed_i` immediately to `Output`

Do not compute all stations first and then apply updates in a batch.

The reason is:

- upstream stations must be able to use downstream space that was just freed on the same day
- downstream stations must not consume material that arrives later that same day from upstream

That is why the correct order is `Station 5 -> Station 1`.

## Daily Log Requirements

For every day, record a complete row with:

- `Day`
- `Job Release`
- `Cap S1`
- `Cap S2`
- `Cap S3`
- `Cap S4`
- `Cap S5`
- `WIP B1`
- `WIP B2`
- `WIP B3`
- `WIP B4`
- `WIP B5`
- `Processed P1`
- `Processed P2`
- `Processed P3`
- `Processed P4`
- `Processed P5`
- `Cumulative Output`

Interpretation:

- `WIP B1-B5` must be end-of-day buffer levels
- `Processed P1-P5` must be actual same-day processed quantities
- `Cumulative Output` must equal the cumulative sum of `P5`

## Required Application Structure

Build this as a polished single-page dashboard. Desktop-first is acceptable, but it must remain usable on smaller screens.

### Top Control Bar

Include:

- `Variation` dropdown
  - `Large Variation`
  - `Small Variation`
- `System` dropdown
  - `Push`
  - `Kanban`
- `Run Simulation` button
- `Play 1-Day Animation` button

Recommended behavior:

- `Run Simulation` computes all 5 experiments for the currently selected variation and system using the locked schedules
- `Play 1-Day Animation` replays one day from the already computed results without changing any numbers

### Main Visualization Area

Show:

- 5 stations
- 5 buffers
- 1 output area

Use visual metaphors inspired by the assignment:

- playing cards or card faces to reveal `job release` and station capacities
- pumpkin seeds or sunflower seeds as animated WIP particles

### Bottom Analysis Area

Use 5 experiment tabs:

- `Experiment 1`
- `Experiment 2`
- `Experiment 3`
- `Experiment 4`
- `Experiment 5`

Each tab must display the results for one bottleneck configuration under the currently selected variation and system.

The active tab must include:

1. `Cumulative Output` line chart
2. `Average WIP by Buffer` bar chart for `B1-B5`
3. `Daily Log` table with 200 rows

## Chart and Metric Definitions

### Cumulative Output

- X-axis: `Day 1` to `Day 200`
- Y-axis: cumulative output
- Definition: cumulative sum of daily `P5`

### Average WIP by Buffer

Define this strictly as the arithmetic mean of end-of-day WIP over all 200 days:

- `Avg B1 = mean(B1_end_of_day over Day 1-200)`
- `Avg B2 = mean(B2_end_of_day over Day 1-200)`
- `Avg B3 = mean(B3_end_of_day over Day 1-200)`
- `Avg B4 = mean(B4_end_of_day over Day 1-200)`
- `Avg B5 = mean(B5_end_of_day over Day 1-200)`

### Helpful Summary KPIs

In addition to the required charts, show compact summary KPIs for the active experiment if it improves readability:

- `Final Output`
- `Average Total WIP`
- `Bottleneck Station`
- `System Type`
- `Variation Type`

Do not let these extra summaries replace the required charts or table.

## Motion and Animation Requirements

The app should feel premium, but the animation must never distort the experiment logic.

Use animation as a presentation layer on top of deterministic simulation results.

### Required Animation Ideas

- A card-flip reveal for daily `Job Release` and `Cap S1-S5`
- A subtle highlight sweep from `Station 5` back to `Station 1` during daily processing playback
- Seed particles or seed clusters moving between buffers to represent processed flow
- Smooth buffer fill transitions when WIP levels rise or fall
- A soft chart draw-in or transition when simulation results appear
- Refined tab switching transitions that preserve context without feeling flashy

### Animation Rules

- `Play 1-Day Animation` must replay a real computed day, not a new simulation
- Motion should be smooth, restrained, and readable
- Avoid noisy particle overload
- Avoid gimmicky casino styling even though cards are used as a metaphor
- The UI should feel analytical, tactile, and premium

### Suggested Daily Animation Sequence

For one-day playback, a good sequence is:

1. Reveal the day number and `Job Release`
2. Flip in the 5 capacity cards
3. Animate station processing in backward order from `S5` to `S1`
4. Update buffer quantities visually after each station step
5. Commit the end-of-day state and refresh the charts/table highlights

## Visual Design Direction

Aim for a polished industrial-lab aesthetic with a calm, premium tone.

Suggested direction:

- English-first product UI
- Sophisticated neutral base with warm accent colors
- A restrained palette such as charcoal, stone, muted brass, copper, or olive accents
- Layered panels, subtle gradients, and high-quality spacing
- Crisp typography with strong hierarchy
- Clean data visualization with excellent contrast

Do not make it look like:

- a generic Bootstrap admin page
- a childish classroom game
- a loud casino or arcade interface
- a flat spreadsheet dump with no visual identity

The best result should feel like a modern operations intelligence dashboard that happens to use cards and seeds as elegant metaphors.

## Quality Bar

The app must feel production-quality in both interaction and clarity:

- clean layout
- deliberate typography
- consistent spacing
- meaningful hover states
- readable table design
- chart colors that match the product visual system
- responsive behavior that does not break the information hierarchy

If there is a tradeoff, preserve simulation correctness first, then preserve clarity, then polish the motion and styling.

## Acceptance Criteria

Treat the following as hard requirements:

1. All random schedules are generated once on initial load and remain locked.
2. The same `jobRelease` sequence is shared across all cases and experiments.
3. `Push` and `Kanban` differ only in buffer-capacity constraints for `Buffers 2-5`.
4. `Buffer 1` is unlimited in all cases.
5. `Station 5` always processes into an infinite output sink.
6. Daily processing always runs in the order `S5 -> S4 -> S3 -> S2 -> S1`.
7. Buffer updates happen immediately inside the backward loop.
8. `Experiment 1-5` reuse the same daily capacity draws and only change the bottleneck insertion position.
9. `Large Variation` and `Small Variation` each use their own locked capacity schedule.
10. `Cumulative Output` always equals the cumulative sum of daily `P5`.
11. Every experiment tab shows a full 200-day result set.
12. All visible UI copy is in English.
13. Animation never changes the underlying numbers.
14. The app is visually refined, not just functionally correct.

## What Not to Do

Do not:

- regenerate random values when switching system, variation, experiment, or replay mode
- simplify the project to only one experiment
- use the wrong Push/Kanban mapping
- batch-apply updates after all stations are calculated
- hide the daily data needed for analysis
- make animation more important than correctness
- produce a low-effort spreadsheet-like interface

## Final Instruction

Build a beautiful English-language simulation dashboard that is analytically trustworthy. It should be rigorous enough for a manufacturing experiment report and polished enough to look like a premium interactive case-study app.
