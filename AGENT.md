# Agent Entry Point

Welcome, Autonomous AI Agent. If you have just been invoked, this file is your designated entry point for the **Field Services Intelligent Dispatcher (FS-ID)** project.

## Your Prime Directives
1. **Understand the Architecture:** Your very first step is to thoroughly read the [Software Requirements Specification (SRS)](docs/requirements/SRS_Service_Request_Router_Agent_v4_3.md) and the [Software Design Document (SDD)](docs/design/SDD_Service_Request_Router_Agent_v1.md). This system enforces a strict 6-Node LangGraph architecture. Do not propose architectures (like ReAct or Planner-Executor) that violate the SDD.
2. **Follow the Rules:** You must abide by the rules laid out in `.agent/rules.md`.
3. **Use the Workflow:** When the user assigns you a task from the Implementation Roadmap, you MUST strictly use the `agentic-task-workflow` skill. 

## Next Steps
Navigate to `.agent/rules.md` to internalize the core project constraints before writing any code.
