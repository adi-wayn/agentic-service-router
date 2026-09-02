# Task 2.3 Walkthrough: Conflict & Gap Detection Node

## Overview
This task implements `src/nodes/gap_node.py` (Node 3), representing the pure algorithmic deterministic phase of the pipeline.

## Implementation Details

### 1. Deterministic Cross-Trade Collision Detector
Implemented the margin collision logic exactly as defined in SDD Section 5.1.
We analyze `match_result.candidates`:
- If `len >= 2`:
- Check if `top1.category != top2.category`
- Check if `top1.signal_score >= 0.65`
- Check if `(top1.signal_score - top2.signal_score) <= 0.15`
If all true, we flag `is_cross_trade_collision = True`.

### 2. Exact Missing Field Diff
Calculates the set difference between the required fields from the matched template and the fields populated by Node 1 in the `ExtractedEntities` model.
- Includes a dictionary mapping template field names (e.g., `access_window`) to normalized model properties (`access_window_or_availability`).
- Evaluates truthiness `not val` to reliably flag `None` or `""` strings.
- All missing required fields are now inherently treated as blocking to simplify the domain logic.

### 3. Pydantic State Encapsulation
Node 3 packages its entire output into the `GapAndConflictResult` model and assigns it directly to `TriageState["gap_result"]`, maintaining zero flat-variable duplication.

## Alignment with SRS/SDD
- The Node executes via strict Python and avoids LLM calls entirely, honoring the Deterministic Algorithmic boundary specified in SDD Section 5.
- The threshold values (`0.65` and `0.15`) match the exact specs in the SDD.
