# Implementation Roadmap: Field Services Intelligent Dispatcher (FS-ID)

This roadmap outlines the iterative, step-by-step implementation plan for the FS-ID system, strictly adhering to the architectural constraints established in the **Software Design Document (SDD)** and fulfilling all functional requirements in the **Software Requirements Specification (SRS)**. 

Each task below is designed to be executed as a single, atomic development unit using the `agentic-task-workflow` skill.

---

## Phase 1: Environment & Foundational Contracts (Hours 0 – 3)
*Objective: Establish project structure, data contracts, state representations, and LLM communication.*

*   [x] **Task 1.1: Initialize Project Structure & Configuration**
    *   Set up Python environment (using `uv` or `requirements.txt` for Python 3.11+).
    *   Create directory structure (`src/`, `src/llm/`, `src/nodes/`, `eval/`, `data/`).
    *   Implement `.env` loading and configure constants (e.g., `LLM_PROVIDER`, API keys).
*   [x] **Task 1.2: Implement Pydantic Data Models (`src/models.py`)**
    *   Implement `SafetyRiskAssessment` (enforcing life-safety booleans).
    *   Implement `ExtractedEntities` (trade, symptom, stated urgency vs real urgency).
    *   Implement `ClarificationQuestion` and `ServiceRouterDecision`.
*   [x] **Task 1.3: Define LangGraph State (`src/state.py`)**
    *   Create the `TriageState` TypedDict to encapsulate inbound payload, dynamic catalogue, and states for all 6 nodes (e.g., `extracted_entities`, `missing_required_fields`, `loop_count`).
*   [x] **Task 1.4: Multi-Provider LLM Abstraction Layer (`src/llm/`)**
    *   Define the `BaseLLMClient` interface with `generate_structured` and `generate_text`.
    *   Implement the `GeminiLLMAdapter` (and optionally Anthropic/OpenAI equivalents).
    *   Implement `LLMClientFactory` to dynamically inject the correct provider.
*   [ ] **Task 1.5: Service Catalogue Ingestion (`src/catalogue.py`)**
    *   Load and parse `service_catalogue.json` into memory.
    *   Create utility methods to retrieve required fields, signal arrays, and trade definitions by Template ID.

## Phase 2: Core Triage Nodes - Cognitive & Algorithmic (Hours 3 – 8)
*Objective: Build the isolated pipeline stages following the Single Responsibility Principle (SRP) mapped in the SDD.*

*   [ ] **Task 2.1: Node 1 - Extractor & Hazard Node (`src/nodes/extractor_node.py`)**
    *   Inject the "Hazard Dominance Directive" prompt.
    *   Use `generate_structured` to populate `ExtractedEntities` and assess physical risk, overriding polite customer sentiment if life-safety is threatened.
*   [ ] **Task 2.2: Node 2 - Template Matcher Node (`src/nodes/matcher_node.py`)**
    *   Compare extracted symptoms against the JSON catalogue template signals.
    *   Calculate semantic similarity scores. Flag `is_out_of_catalogue` if max match $< 0.40$.
*   [ ] **Task 2.3: Node 3 - Conflict & Gap Detection Node (`src/nodes/gap_node.py`)**
    *   Compute exact missing required fields using set difference logic.
    *   Implement the **Algorithmic Cross-Trade Collision Detector**: Flag fatal ties if $|S_1 - S_2| \le 0.15$ across different trades.
*   [ ] **Task 2.4: Node 4 - Confidence & Routing Node (`src/nodes/router_node.py`)**
    *   Implement the non-linear composite confidence scoring formula.
    *   Apply dynamic penalties for missing fields and conflicts.
    *   Assign strictly banded routing actions: `CONFIDENT_RECOMMENDATION` ($\ge 0.75$), `NEEDS_CLARIFICATION` ($0.40-0.74$), or `ROUTE_TO_HUMAN` ($< 0.40$).

## Phase 3: Agentic Loop & Graph Orchestration (Hours 8 – 13)
*Objective: Enable closed-loop clarification and wire the state machine together.*

*   [ ] **Task 3.1: Node 5 - Clarifier & Feedback Nodes (`src/nodes/clarifier_node.py`)**
    *   Implement `clarifier_node` to generate 1-3 targeted questions via LLM text generation if state is `NEEDS_CLARIFICATION`.
    *   Implement `feedback_node` to ingest user answers, update `clarification_history`, and increment `loop_count`.
*   [ ] **Task 3.2: Node 6 - Finalize Decision Node (`src/nodes/finalizer_node.py`)**
    *   Synthesize the 4-part concise rationale (Selected template, Causal justification, Missing intake, Counterfactual boundary condition).
    *   Format and output the finalized `ServiceRouterDecision`.
*   [ ] **Task 3.3: LangGraph Compilation (`src/graph.py` & `src/agent.py`)**
    *   Initialize `StateGraph(TriageState)`.
    *   Add nodes and configure transitions (`extractor -> matcher -> gap -> router`).
    *   Implement `route_conditional_edge` for loop recursion bounded at $K \le 2$ turns.
    *   Compile the graph and expose a primary `TriageAgent.run()` method.

## Phase 4: Evaluation, Benchmarking & Refinement (Hours 13 – 17)
*Objective: Prove the system satisfies SRS operational requirements via the 11-case benchmark.*

*   [ ] **Task 4.1: Evaluation Test Suite (`eval/ground_truth.py`)**
    *   Transcribe the 11 edge-case scenarios (REQ-001 to REQ-011) from the SRS into JSON/Python arrays.
    *   Define the ground truth assertions for Routing Action and P1 Recall for each case.
*   [ ] **Task 4.2: Execute Benchmark (`eval/run_evaluation.py`)**
    *   Implement an asynchronous evaluation script to run all 11 cases through the compiled LangGraph.
    *   Automatically compute $Acc_{\text{action}}$, $Rec_{P1}$, $F1_{\text{macro}}$, and Brier Score / ECE.
*   [ ] **Task 4.3: Metric Alignment & Adjustments**
    *   Review metrics against the target v2 goals outlined in SRS Section 9.3.
    *   Fine-tune prompt directives (e.g., Sub-Clause Safety Masking fixes) or confidence weights to ensure the agent achieves $90.9\%$ routing accuracy and $100\%$ P1 safety recall.

## Phase 5: Delivery & Polish (Hours 17 – 24)
*Objective: Finalise the deliverables for presentation and integration.*

*   [ ] **Task 5.1: Command-Line Interface (CLI)**
    *   Create a clean entry point (`main.py`) allowing a user to run the agent interactively in the terminal.
*   [ ] **Task 5.2: Final Documentation (`WRITEUP.md`)**
    *   Produce the final architectural summary covering the hybrid approach, the MCP analysis, the evaluation proof, and design trade-offs.
*   [ ] **Task 5.3: Packaging & QA**
    *   Clean up all debug logging, format codebase, and ensure zero-configuration execution via standard `python -m` commands. Ensure GitHub repo readiness.
