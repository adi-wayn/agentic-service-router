# Field Services Intelligent Dispatcher (FS-ID)

An autonomous LangGraph-based AI agent that acts as a cognitive routing engine for inbound field service requests. It ingests raw textual maintenance requests, performs semantic entity extraction, identifies safety hazards, scores the symptoms against a dynamic service catalogue, and issues deterministic dispatch routing decisions with confidence intervals.

## Core Features
* **Hybrid Cognitive/Algorithmic Pipeline:** Uses LLMs (Gemini, Claude, OpenAI) for semantic reasoning and Python for deterministic business rules (Pydantic validation, margin collisions).
* **Zero-Hallucination Guardrails:** Employs a strict 6-Node StateGraph (FSM) architecture guaranteeing deterministic SLA bounds and exact schema compliance.
* **Closed-Loop Clarification:** Automatically generates targeted clarifying questions if critical intake info is missing, maintaining state across a bounded number of conversational turns.
* **Safety First:** Hardcoded "P1 Hazard Dominance" ensures critical physical threats (e.g., active fires, flooding) immediately override polite customer sentiment.
* **Abstract LLM Provider:** Seamlessly switch between LLM providers using the abstract `BaseLLMClient` adapter without rewriting cognitive node logic.

## Documentation
* [Software Requirements Specification (SRS)](docs/requirements/SRS_Service_Request_Router_Agent_v4_3.md) - The domain rules and functional requirements.
* [Software Design Document (SDD)](docs/design/SDD_Service_Request_Router_Agent_v1.md) - The architecture, state machine flowchart, and technical blueprint.
* [Implementation Roadmap](docs/IMPLEMENTATION_ROADMAP.md) - **Pending**.

## Setup & Execution
*(Implementation is pending based on the SDD blueprint.)*
