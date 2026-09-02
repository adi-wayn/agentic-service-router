# Walkthrough: Task 1.5 - Service Catalogue Ingestion

## Context
This task implements the dynamic loading of `service_catalogue.json`. Following the SDD mandate ("No Mocks"), the catalogue acts as the sole source of truth for the system's runtime parameters, completely eliminating hardcoded template IDs or logic inside the LangGraph nodes.

## What Was Implemented

1. **`ServiceCatalogue` Singleton Pattern**:
   *   Created the `ServiceCatalogue` class in `src/catalogue.py`.
   *   Utilized the Singleton pattern (`__new__`) so the JSON file is parsed into memory only once during the application lifecycle.
   *   It natively loads `CATALOGUE_PATH` defined dynamically in the `config.py`.

2. **Utility Methods**:
   *   `get_template_by_id()`: Fetches the raw dictionary structure for any given template ID.
   *   `get_required_fields()`: Extracts the `required_intake_fields` array. This will be critical for Node 3 (Gap Detection Node) to compute what's missing using mathematical set difference.
   *   `get_signals()`: Extracts the symptom strings which Node 2 (Template Matcher) will cross-reference against the LLM's extracted symptoms.
   *   `get_trade_definition()`: Returns the `category` string (e.g., "HVAC", "Plumbing"). Node 3 requires this to detect Cross-Trade margin collisions.

## Next Steps
This concludes Phase 1. We are now fully equipped to move into **Phase 2: Core Triage Nodes** and begin building the LangGraph pipeline, starting with **Task 2.1: Node 1 - Extractor & Hazard Node**.
