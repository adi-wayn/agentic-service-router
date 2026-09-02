# Walkthrough: Task 1.4 - Multi-Provider LLM Abstraction Layer

## Context
This task implements the core cognitive engine interface for the FS-ID agent. By routing all LLM calls through an abstract `BaseLLMClient` instead of using SDKs directly inside LangGraph nodes, we achieve strict separation of concerns and enable zero-code model swapping (e.g., Gemini to Anthropic) via the `.env` file.

## What Was Implemented

1. **`src/llm/base.py` (The Interface)**:
   *   Created `BaseLLMClient` inheriting from `abc.ABC`.
   *   Defined the `generate_structured()` method for strict Pydantic parsing.
   *   Defined the `generate_text()` method for raw string generation.

2. **`src/llm/gemini_adapter.py` (The Concrete Adapter)**:
   *   Implemented the Gemini client using the official `google-genai` SDK.
   *   Configured `GenerateContentConfig` to forcibly set `temperature=0.0` inside the adapter. This enforces the determinism rule globally, preventing any individual LangGraph node from accidentally running at a higher temperature.

3. **`src/llm/factory.py` (The Factory)**:
   *   Implemented `LLMClientFactory.get_client()`.
   *   It reads `LLM_PROVIDER` from `src.config` and instantiates the correct adapter dynamically.
   *   Stubbed out Anthropic and OpenAI implementations to raise `NotImplementedError` until they are explicitly needed.

## Next Steps
The cognitive abstraction layer is now complete. Our next step is **Task 1.5: Service Catalogue Ingestion (`src/catalogue.py`)**, which will load the runtime definitions for our template matcher node.
