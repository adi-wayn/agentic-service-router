# Walkthrough: Task 3.2 - Node 6 (Finalize Decision Node)

## Overview
Successfully implemented Node 6 (Finalizer Node), which is responsible for satisfying FR-09 (Explainability). The node synthesizes a clear rationale for the routing decision and a counterfactual boundary condition, then compiles the final `ServiceRouterDecision`.

## Changes Made
1. **Refactored Models (`src/models.py`)**: 
   Extracted `decision_rationale` and `what_would_change_this_call` into a cleanly decoupled sub-model called `FinalizerSynthesis`. We updated `ServiceRouterDecision` to embed this sub-model, perfectly aligning Node 6's output structure with the patterns used for Nodes 1-5. This eliminated duplicate parameters and removed the need for temporary LLM wrapper structs.
2. **Prompts (`src/prompts/finalizer_prompt.py`)**: 
   Added the system prompt instructing the LLM to write a concise rationale based on the triage state.
3. **Node Logic (`src/nodes/finalizer_node.py`)**: 
   Implemented `finalize_decision_node`. It serializes the accumulated state (`ExtractedEntities`, `CatalogueMatchResult`, `GapAndConflictResult`, `ConfidenceAndRoutingResult`, `ClarificationState`) into a context prompt. After the LLM generates the `FinalizerSynthesis`, the node programmatically constructs the final `ServiceRouterDecision`, including the complete `audit_trace` list, and stores it in `state["final_decision"]`.

## Validation Results
- Code compilation passed successfully (`python -m py_compile`).
- Strict adherence to the Single Responsibility Principle: the node logic gathers the state, the LLM provides ONLY the subjective rationale, and the final deterministic payload is assembled correctly.
