# Walkthrough: Task 3.1 - Node 5 (Clarifier & Feedback Nodes)

## Overview
Successfully implemented the stateful conversational loop logic required for Phase 3. The `clarifier_node` and `feedback_node` now enable the agent to securely ask for missing critical information, ingest simulated answers, and increment loop constraints before routing back for extraction.

## Changes Made
1. **Added Schema to `src/models.py`:**
   Appended `ClarificationLLMOutput` to structurally enforce that the Clarifier Node's LLM *only* outputs a maximum of 3 targeted questions, preventing it from hallucinating or overwriting system-managed state variables like `loop_count` and `clarification_history`.

2. **Created Prompts:**
   - **`src/prompts/clarifier_prompt.py`**: Added `CLARIFIER_SYSTEM_PROMPT` to instruct the LLM on being courteous, targeted, and reviewing history to avoid asking repetitive questions.
   - **`src/prompts/simulated_answers.py`**: Added a dictionary and utility function `get_simulated_answer()` to provide diverse test data for edge-cases (like REQ-002 and REQ-004), dynamically returning answers based on keyword matches in the question text or target fields.

3. **Implemented Node Logic (`src/nodes/clarifier_node.py`):**
   - **`clarifier_node`**: Checks routing pre-conditions (`NEEDS_CLARIFICATION`). Uses the `LLMClientFactory` and `ClarificationLLMOutput` schema to generate 1-3 questions regarding missing gaps or conflicts.
   - **`feedback_node`**: Iterates over generated questions, uses `get_simulated_answer` to mock customer replies, appends these to `clarification_history`, increments the `loop_count`, and injects the Q&A text back into `raw_text` so Node 1 can extract the updated context.

## Validation Results
- Python compiler ran cleanly (`python -m py_compile ...`).
- Single-responsibility principle strictly adhered to (schema decoupled into models, prompts into `src/prompts`, node logic into `src/nodes/clarifier_node.py`).
- Ready to be wired up into the LangGraph in Task 3.3.
