# Field Services Intelligent Dispatcher (FS-ID) - Agent Rules

## 1. Architectural Integrity
*   **Strict 6-Node Flow:** The system must adhere perfectly to the 6-Node LangGraph StateMachine defined in the SDD (`Extractor -> Matcher -> Gap -> Router -> (Clarifier | Finalizer)`).
*   **No ReAct Patterns:** Do not use `langgraph.prebuilt.ToolNode` or dynamic multi-step ReAct agents. The graph flow must be 100% deterministic and strictly defined.
*   **LLM Abstraction & Multi-Provider Support:** Do not use provider-specific SDKs inside the LangGraph nodes. All cognitive calls must route through the `BaseLLMClient` adapter. The system supports **Google Gemini**, **Anthropic Claude**, and **OpenAI GPT** as first-class providers with zero hardcoded vendor bias.
*   **Clean Root & Modular Subpackages:** No Python scripts or entry points are permitted in the repository root. All application logic resides in `src/`:
    *   `src/main.py`: Interactive CLI entry point.
    *   `src/core/`: LangGraph state machine, state definition, and agent orchestrator (`state.py`, `graph.py`, `agent.py`).
    *   `src/cli/`: Terminal interface presentation (`cli.py`) and batch Data Science evaluation tracker (`session_tracker.py`).
    *   `src/nodes/`: 6 cognitive nodes.
    *   `src/prompts/`: Centralized LLM prompt templates.
    *   `src/llm/`: Abstract LLM provider adapters.

## 2. Determinism & Reliability
*   **No Mocks:** The `service_catalogue.json` must be dynamically loaded and queried via standard Python, not faked or hardcoded inside the nodes.
*   **Pydantic Enforcement:** All LLM outputs must be coerced via `with_structured_output` using strict Pydantic schemas (e.g., `ServiceRouterDecision`, `ExtractedEntities`).
    *   *Strict Schema Adherence:* Do not hallucinate or access dynamic properties on Pydantic models. Only use fields explicitly defined in `src/models.py`.
    *   *Centralized Schemas:* ALL model schemas must reside exclusively in `src/models.py` to maintain a decoupled system. Do not declare ad-hoc or temporary Pydantic models inside node or logic files.
*   **Centralized Prompts:** ALL system prompts and prompt templates must reside in dedicated files within the `src/prompts/` directory.
*   **Temperature:** All cognitive node LLM calls must be executed at `Temperature = 0.0` to maximize determinism.

## 3. Workflow
*   **Agentic Task Workflow:** You must use the `agentic-task-workflow` skill for all feature development.
*   **Implementation Roadmap:** Follow `docs/Implementation_Roadmap.md` sequentially. Do not jump ahead.

## 4. Documentation Maintenance
*   **Single Source of Truth:** The SDD and SRS are living documents. If you hit a technical limitation or execute an architectural refactor, you must update the SDD and SRS to reflect the change.

## 5. Mandatory User Review
*   **NEVER COMMIT UNAPPROVED CODE:** You must NEVER run `git commit` without explicitly waiting for and receiving user approval. This applies to EVERYTHING—including small refactors, minor bug fixes, or architecture reorganizations between tasks. Implement the changes, pause, ask for review, and ONLY commit after the user explicitly says "Approved".

## 6. Proper Tool Usage
*   **NO BASH HACKS:** Do not use bash commands like `cat << 'EOF'` or create temporary Python scripts (`fix.py`, `patch.py`, `new_skill.py`) to create or edit files. 
*   **USE NATIVE TOOLS:** You must exclusively use your native `write_to_file` and `replace_file_content` tools for all file manipulation. No unnecessary files should ever be left in the repository.

## 7. Data Governance & Evaluation Integrity
*   **ASSIGNMENT DATA FILES ARE READ-ONLY**: The files `data/service_catalogue.json` and `data/test_requests.json` are strictly read-only. They are provided by the assignment creators and must NEVER be modified to fit the code or improve evaluation metrics. Code must adapt to these data files, not the other way around.
*   **CUSTOM DATA FILES ARE READ/WRITE**: The file `data/custom-hard-requests.json` is read/write. You are expected to create, modify, or expand this file with custom edge cases to improve evaluation and coverage (at least 3 cases required).
*   **EVALUATION RE-USE**: In-session evaluation tracking must re-use the exact mathematical metric definitions from `eval/metrics.py` (Confusion Matrix, Macro/Weighted F1, P1 Safety Recall, Template Accuracy, Jaccard IoU, Brier Score, ECE) evaluated in batches of 3 cases.
