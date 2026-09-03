# Task 4.2: Execute Benchmark

## Overview
This task focused on implementing the autonomous benchmarking script to evaluate the `TriageAgent` against the 11 edge cases using a live LLM API (Google Gemini).

## Accomplishments
1. **API Integration & `.env` Support:**
   Configured the system to securely ingest the `GEMINI_API_KEY` via the `.env` file using `python-dotenv`. Added safeguards to detect missing keys.
   
2. **Rate Limit Protection:**
   Because we are using the free tier of the Gemini API (which is typically capped at 15 Requests Per Minute), the script processes the 11 cases sequentially and applies a 5-second `time.sleep()` pause between each request. This guarantees we will not hit a `429 Resource Exhausted` error during the evaluation.

3. **Evaluation Runner (`eval/run_evaluation.py`):**
   * Loaded the `test_requests.json` and `custom-hard-requests.json`.
   * Invoked the compiled LangGraph agent for each case.
   * Extracted the predicted Action, Urgency, Template, Missing Fields, Confidence, and Clarification Questions.
   * Piped these directly into the mathematical evaluators from Task 4.1.

4. **Data Science Report Generation:**
   The script outputs a comprehensive console report comparing our metrics against the SRS Phase 2 goals:
   * Macro/Weighted F1
   * P1 Safety Recall & Cost
   * Template Accuracy
   * Mean Jaccard IoU
   * Brier Score & ECE
   * Question Specificity
   
   It also logs every detailed prediction to `data/evaluation_results.json` so we can perform error analysis.

## Next Steps
We must inject the real Gemini API key into the `.env` file and actually execute the script via `python3 -m eval.run_evaluation --verbose`. The results will dictate the adjustments needed in Task 4.3.
