# Task 5.1: Command-Line Interface (CLI) & Terminal User Interface (TUI)

## Objective
Build a professional, interactive Command-Line Interface (CLI) / Terminal User Interface (TUI) in `src/main.py` using `rich` for formatting, styling, and status spinners. Provide real-time dynamic evaluation tracking within the CLI so that user-submitted queries in runtime can be evaluated, Data Science metrics from `eval.metrics` can be calculated dynamically in batches of 3 cases, and reports can be exported.

## Steps Completed

1. **Dependency Integration:**
   - Added `rich` to `requirements.txt` and installed it into the virtual environment (`.venv`).

2. **Session Evaluation Tracker (`src/session_tracker.py`):**
   - Implemented `SessionCase` dataclass to encapsulate per-case query inputs, predicted templates, routing actions, assessed urgencies, predicted missing fields, confidence scores, user ground truth feedback, loop counts, and timestamps.
   - Implemented `SessionTracker` class featuring:
     - Opt-in evaluation toggle (`toggle_eval()`)
     - Null-safe case recording from `ServiceRouterDecision` objects (`record_case()`)
     - Ground truth feedback logging (`record_feedback()`) supporting correction of template, action, urgency, and missing fields
     - Real-time computation of the complete Data Science evaluation metrics suite directly via `eval.metrics`:
       - **Action Routing Performance:** 3x3 Confusion Matrix, Precision, Recall, Macro-Averaged F1, and Weighted F1 for `CONFIDENT_RECOMMENDATION`, `NEEDS_CLARIFICATION`, and `ROUTE_TO_HUMAN`.
       - **Safety Critical Metrics:** P1 Safety Recall, P1 False Negative Rate, and Safety Cost Penalty.
       - **Template & Gap Extraction:** Template Accuracy and Mean Jaccard IoU.
       - **Confidence Calibration:** Brier Score and Expected Calibration Error (ECE).
       - **Clarification Quality:** Question Specificity, Redundancy Index, Loop Convergence Rate (CR), and Mean Turns to Resolution (MTTR).
     - **Batching Engine:** Automatically triggers full metric recalculation and report generation in batches of 3 evaluated cases (`batch_size=3`), as well as on-demand via `/metrics` or `/report`.
     - JSON session and batch report persistence (`export_report()`) to `data/session_batch_<batch>_<timestamp>.json` and `data/session_report_<timestamp>.json`.

3. **Rich TUI Presentation Layer (`src/cli.py`):**
   - Built a comprehensive formatting module using `rich`:
     - `display_welcome_banner()`: Styled ASCII art title and pipeline metadata.
     - `display_service_catalogue()`: Formatted table of available service workflow templates with urgency tier color coding.
     - `display_routing_result()`: Full decision panel with color-coded routing actions, block-character confidence progress bar, extracted entities, causal rationales, counterfactual boundary conditions, and 6-node audit traces.
     - `display_metrics()`: Full Data Science benchmark evaluation report mirroring the 5 sections from `eval/run_evaluation.py`.
     - `display_batch_notification()`: Notification banner displayed whenever a 3-case evaluation batch completes.
     - `display_session_history()`: History table of all cases processed during the session.
     - `prompt_feedback()`: Interactive feedback prompt for user-in-the-loop ground truth collection.
     - `get_thinking_status()`: Spinner context manager indicating live LangGraph execution.

4. **Interactive Entry Point (`src/main.py` & root launcher `main.py`):**
   - Implemented the primary application in `src/main.py` (with a clean forwarder at root `main.py`).
   - Implemented command routing:
     - `/eval`: Toggle evaluation mode on/off (evaluates in batches of 3).
     - `/metrics`: Display current Data Science benchmark metrics on demand.
     - `/history`: Review all cases processed in the current session.
     - `/report`: Export the session evaluation report to JSON on demand.
     - `/catalogue`: Redisplay the service catalogue.
     - `/help`: Show command documentation.
     - `quit` / `exit` / `q`: Exit gracefully, automatically displaying final metrics and exporting the final report if cases were evaluated.

5. **End-to-End Verification:**
   - Tested interactive query execution against the live Gemini 6-node LangGraph pipeline.
   - Tested batch triggering: verified that every 3 evaluated cases automatically compute the full Data Science metrics suite, render the benchmark report, and export a batch report.
   - Verified that ground truth feedback logging recalculates the exact confusion matrix, F1-scores, safety metrics, and calibration errors in real time.
   - Added `data/session_report_*.json` and `data/session_batch_*.json` to `.gitignore`.

## Conclusion
Task 5.1 delivers an intuitive, visually polished terminal interface that enables operational dispatchers and developers to interact with the FS-ID agent, observe the full 6-node reasoning chain, and dynamically assess model performance using the official Data Science benchmark suite across batches of live inputs.
