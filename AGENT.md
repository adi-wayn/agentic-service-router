# Agent Entry Point

Welcome, Autonomous AI Agent. If you have just been invoked, this file is your designated entry point for the **Field Services Intelligent Dispatcher (FS-ID)** project.

## Your Prime Directives
1. **Understand the Architecture:** Your very first step is to thoroughly read the [Software Requirements Specification (SRS)](docs/requirements/SRS_Service_Request_Router_Agent_v4_3.md) and the [Software Design Document (SDD)](docs/design/SDD_Service_Request_Router_Agent_v1.md). This system enforces a strict 6-Node LangGraph architecture. Do not propose architectures (like ReAct or Planner-Executor) that violate the SDD.
2. **Follow the Rules:** You must abide by the rules laid out in `.agent/rules.md`.
3. **Use the Workflow:** When the user assigns you a task from the Implementation Roadmap, you MUST strictly use the `agentic-task-workflow` skill. 
4. **Mandatory User Review Before Commit:** You must NEVER execute a `git commit` before explicitly presenting the code to the user and receiving their approval. Write the code, test it locally, show the user the implementation (or stop and wait for them to review the files), and ONLY commit after they confirm.
5. **Proper Tool Usage:** Never use bash commands like `cat` or temporary python scripts to create or edit files. Always use your built-in `write_to_file` and `replace_file_content` tools. Leave no unnecessary files behind.

## Next Steps
Navigate to `.agent/rules.md` to internalize the core project constraints before writing any code.
