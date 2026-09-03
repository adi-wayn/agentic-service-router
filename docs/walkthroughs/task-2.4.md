# Task 2.4 Walkthrough: Node 4 (Confidence & Routing Node)

## Overview
Implemented `src/nodes/router_node.py` to act as the deterministic mathematical gatekeeper for the triage pipeline. It evaluates the outputs from Nodes 1, 2, and 3, applies the strictly defined non-linear confidence formula, and maps the final score into a specific routing action.

## Implementation Details

### 1. Non-Linear Confidence Formula
Created `calculate_calibrated_confidence`, a pure Python function that computes the final confidence score without LLM intervention:
- **Base Formula**: `(0.60 * signal_score) + (0.40 * completeness_ratio)`. The ratio of present vs required fields is strictly computed here.
- **Overrides**: Hard overrides for out-of-catalogue (`0.10`) and cross-trade collisions (`0.30`).
- **Penalties**: 
  - Conflict penalty (`-0.20` per conflict, capped at `0.40`).
  - Missing field penalty (`-0.25` per missing required field) acting as the non-linear driver to pull scores down sharply if requirements are unmet.

### 2. Routing Logic & State Management
- Fetches dependencies (`extracted_entities`, `match_result`, `gap_result`) from the LangGraph `TriageState`.
- Dynamically retrieves `required_intake_fields` in $O(1)$ from the `ServiceCatalogue` singleton.
- Strict threshold banding applied to assign `CONFIDENT_RECOMMENDATION` ($\ge 0.75$), `NEEDS_CLARIFICATION` ($0.40 \le C < 0.75$), or `ROUTE_TO_HUMAN` ($< 0.40$).
- Instantiates the `ConfidenceAndRoutingResult` Pydantic model and attaches it to the state.

## Architectural Changes
- Dropped the over-engineered "Strategy Pattern" previously mentioned in the SDD in favor of a clean, single functional implementation.
- Refactored `ServiceRouterDecision` assembly to be strictly deferred to Node 6 (`finalizer_node`), as Node 4's single responsibility is to route.

## Verification
- Verified formula math mathematically matches the exact penalties described in the updated SDD/SRS.
- Passed `python3 -m py_compile src/nodes/router_node.py` with zero errors.
