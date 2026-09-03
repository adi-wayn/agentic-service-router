# Agent Entry Point

Welcome, Autonomous AI Agent. If you have just been invoked, this file is your designated entry point for the **Field Services Intelligent Dispatcher (FS-ID)** project.

## Your Prime Directives

1. **Understand the Architecture:** Your very first step is to thoroughly read the [Software Requirements Specification (SRS v4.3)](docs/requirements/SRS_Service_Request_Router_Agent_v4_3.md) and the [Software Design Document (SDD v1.2)](docs/design/SDD_Service_Request_Router_Agent_v1_2.md). This system enforces a strict 6-Node LangGraph state machine architecture (`Extractor -> Matcher -> Gap -> Router -> (Clarifier | Finalizer)`). Do not propose unconstrained architectures (like ReAct or multi-step autonomous tool loops) that violate the SDD.
2. **Follow the Rules:** You must abide strictly by the rules laid out in `.agent/rules.md`.
3. **Use the Workflow:** When the user assigns you a task from the Implementation Roadmap, you MUST strictly follow the 16-step `agentic-task-workflow` skill.
4. **Mandatory User Review Before Commit (CRITICAL):** You must NEVER execute a `git commit` before explicitly presenting the completed implementation and verification to the user and receiving their affirmative approval ("Approved"). Write the code, test it locally, show the user the implementation, and ONLY commit after they confirm.
5. **Proper Tool Usage:** Never use bash commands like `cat << 'EOF'` or temporary python scripts (`fix.py`, `patch.py`) to create or edit files. Always use your built-in `write_to_file` and `replace_file_content` tools. Leave no stray or temporary files behind.
6. **Package Modularization & Clean Root:** No Python files are permitted in the repository root. All application code resides cleanly under `src/`:
   - `src/main.py`: Interactive CLI / Rich TUI entry point.
   - `src/core/`: Core LangGraph state machine (`state.py`, `graph.py`, `agent.py`).
   - `src/cli/`: Terminal interface formatting (`cli.py`) and dynamic Data Science session evaluation tracker (`session_tracker.py`).
   - `src/nodes/`: 6 LangGraph cognitive and algorithmic nodes.
   - `src/prompts/`: Centralized LLM prompt templates.
   - `src/llm/`: Abstract multi-provider adapter layer (Gemini, Anthropic, OpenAI).
   - `src/models.py`: Centralized Pydantic v2 schemas.
   - `src/catalogue.py`: Service catalogue singleton.
   - `src/config.py`: Centralized configuration.
   - `eval/`: Offline benchmark test runner and metrics suite (`run_evaluation.py`, `metrics.py`).

## Next Steps
Navigate to `.agent/rules.md` to internalize the core project constraints before writing any code.
