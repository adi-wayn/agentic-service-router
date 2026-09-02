# Task 2.2: Node 2 - Template Matcher Node

## Objective
Implement the second node in the LangGraph architecture. The Template Matcher node compares extracted entities against the dynamic Service Catalogue to produce a semantic similarity score, ranking the candidate templates and identifying if the request is out-of-scope or spans multiple trades.

## Implementation Details

1. **Deterministic Pre-Filtering (`src/nodes/matcher_node.py`)**:
   - To optimize efficiency and reduce token overhead, the node first performs a deterministic pre-filter. It isolates templates from the catalogue where the `category` matches the `primary_trade` (and `secondary_trade` if present) extracted in Node 1.
   - If the trade is "Unknown" or if the filter returns empty, it safely falls back to evaluating the entire catalogue.

2. **Schema Definition (`src/models.py`)**:
   - Added the `CandidateMatch` and `CatalogueMatchResult` Pydantic models. These models enforce strict scoring boundaries and ensure the LLM returns `is_out_of_catalogue` and `cross_trade_detected` boolean flags.

3. **Prompt Engineering (`src/prompts/matcher_prompt.py`)**:
   - Created the `MATCHER_SYSTEM_PROMPT` containing a precise Scoring Rubric:
     - 0.85 - 1.00: DIRECT / STRONG MATCH
     - 0.65 - 0.84: PLAUSIBLE / COMPETING CANDIDATE
     - 0.40 - 0.64: WEAK / AMBIGUOUS MATCH
     - 0.00 - 0.39: OUT-OF-CATALOGUE
   - Includes specific guidance on near-duplicate discrimination and cross-trade detection.

4. **Node Execution Integration**:
   - The LLM's response is deterministically sorted by score, and threshold checks are re-verified in Python (`max_score < 0.40`) to guarantee deterministic routing boundaries.
   - Updates `candidate_matches`, `selected_candidate_id`, `is_out_of_catalogue`, and `is_cross_trade_collision` in the `TriageState`.

## Review Status
Pending User Approval.
