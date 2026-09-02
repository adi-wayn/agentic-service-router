---
name: agentic-task-workflow
description: Enforces the strict 16-step Agentic Agile workflow for developing tasks from the Implementation Roadmap.
---

# Agentic Task Workflow

Invoke this skill whenever you start working on a new task from the Implementation Roadmap to ensure strict adherence to the project's Git and Agentic Agile workflow.

## The 16-Step Workflow

You MUST follow these steps precisely in order:

1. **Create Branch:** Create a new branch for this specific task (e.g., `feature/task-name`).
2. **Checkout:** Branch off `main` to this new branch.
3. **Isolation:** Work ONLY on this branch. The `main` branch is read-only.
4. **Context Gathering:** Read the files that need to be read for the full context of this task, including the SRS, SDD, and any other relevant `.md` files in `.agent/`.
5. **Roadmap Alignment:** Check the `docs/Implementation_Roadmap.md` for the specific requirements of the current task.
6. **Planning:** Create a dedicated implementation plan for this task (using the `/plan` artifact). Consider the full context and rules, and explicitly highlight the pros and cons of each architectural decision.
7. **Verification against Specs:** Make sure the decisions in the plan strictly align with the SRS and SDD. Modify the SRS/SDD if necessary and agreed upon.
8. **Step-by-Step Implementation:** Implement the plan step by step. If you need to stop, show the user the steps you made to keep them in the loop.
9. **Post-Implementation Verification:** Do another check to ensure everything implemented is aligned with the implementation roadmap and SRS/SDD, verifying no scope drift occurred during implementation.
10. **Documentation Update:** Update the corresponding tasks in the implementation plan/roadmap, and create a walkthrough file under `docs/walkthroughs/` (e.g., `task-1.2.md`) to document what was done.
11. **Knowledge Synchronization:** Extract all lessons learned and update relevant institutional knowledge files (`.agent/rules.md`, SDD, SRS, Roadmap). Ensure future agents will be strictly aligned with the latest architecture.
12. **User Review (CRITICAL):** STOP. Present the implemented code and documentation to the user. You MUST wait for the user to explicitly approve the changes. DO NOT run `git commit` before receiving this approval.
13. **Commit:** Only AFTER receiving explicit user approval, run `git commit` to save the updates to the feature branch.
14. **Merge:** Switch to `main` and merge the feature branch into `main`.
15. **Cleanup:** Delete the feature branch that you worked on.
16. **Close:** Close the task and inform the user.
