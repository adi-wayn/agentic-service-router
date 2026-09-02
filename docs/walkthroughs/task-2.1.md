# Task 2.1: Node 1 - Extractor & Hazard Node

## Objective
Implement the first node in the 6-Node LangGraph architecture: the Extractor & Hazard Node. This node parses raw unstructured requests and populates the `ExtractedEntities` structured schema, properly decoupling stated urgency from physical hazards.

## Implementation Details
1. **Prompt Engineering (`src/prompts/extractor_prompt.py`)**:
   - Defined `EXTRACTOR_SYSTEM_PROMPT` containing strict rules for "Hazard Dominance".
   - Explicitly provided urgency tiers (P1, P2, P3) and conflict detection guidelines.
   - Designed `build_extractor_user_prompt(request_text: str)` to format the incoming request into the prompt context.

2. **Node Logic (`src/nodes/extractor_node.py`)**:
   - Created `extract_and_analyze_node(state: TriageState) -> TriageState`.
   - Utilizes `LLMClientFactory.get_client()` and `generate_structured(..., schema=ExtractedEntities)`.
   - Gracefully handles missing `raw_text` and sets an `error_state` if an exception bubbles up.
   - Pushes extracted values directly into the immutable `TriageState`, matching expected keys (`extracted_entities`, `stated_urgency`, `assessed_real_urgency`, `urgency_rationale`, `has_safety_hazard`, `hazard_type`).
   - Appends node execution to `audit_trace`.

## Testing & Usage
Downstream nodes will use the output (particularly `assessed_real_urgency` and the full `extracted_entities` dict dump) to compute gaps, score against the `service_catalogue.json`, and make routing decisions.

## Review Status
Pending User Approval.
