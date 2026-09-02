# Field Services Intelligent Dispatcher (FS-ID) - Agent Rules

## 1. Architectural Integrity
*   **Strict 6-Node Flow:** The system must adhere perfectly to the 6-Node LangGraph StateMachine defined in the SDD (`Extractor -> Matcher -> Gap -> Router -> (Clarifier | Finalizer)`).
*   **No ReAct Patterns:** Do not use `langgraph.prebuilt.ToolNode` or dynamic multi-step ReAct agents. The graph flow must be 100% deterministic and strictly defined.
*   **LLM Abstraction:** Do not use provider-specific SDKs inside the LangGraph nodes. All cognitive calls must route through the `BaseLLMClient` adapter.

## 2. Determinism & Reliability
*   **No Mocks:** The `service_catalogue.json` must be dynamically loaded and queried via standard Python, not faked or hardcoded inside the nodes.
*   **Pydantic Enforcement:** All LLM outputs must be coerced via `with_structured_output` using strict Pydantic schemas (e.g., `ServiceRouterDecision`, `ExtractedEntities`).
*   **Temperature:** All cognitive node LLM calls must be executed at `Temperature = 0.0` to maximize determinism.

## 3. Workflow
*   **Agentic Task Workflow:** You must use the `agentic-task-workflow` skill for all feature development.
*   **Implementation Roadmap:** *Placeholder for future roadmap.* You will follow the Roadmap sequentially once it is created. Do not jump ahead.

## 4. Documentation Maintenance
*   **Single Source of Truth:** The SDD and SRS are living documents. If you hit a technical limitation that requires an architectural shift, you must update the SDD *first* before changing the code.

## 5. Mandatory User Review
*   **NEVER COMMIT UNAPPROVED CODE:** You must never run `git commit` without explicitly waiting for and receiving user approval on the implemented code. Implement the task, pause, ask for review, and only commit after the user says "Approved".

## 6. Proper Tool Usage
*   **NO BASH HACKS:** Do not use bash commands like `cat << 'EOF'` or create temporary Python scripts (`fix.py`, `patch.py`, `new_skill.py`) to create or edit files. 
*   **USE NATIVE TOOLS:** You must exclusively use your native `write_to_file` and `replace_file_content` tools for all file manipulation. No unnecessary files should ever be left in the repository.
