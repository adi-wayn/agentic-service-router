import json
import time
import os
import argparse
from typing import Dict, List, Any

# Ensure we have the python-dotenv loaded for local testing
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.core.agent import TriageAgent
from eval.ground_truth import load_ground_truth
from eval.metrics import (
    compute_confusion_matrix,
    compute_safety_metrics,
    compute_jaccard_iou,
    compute_calibration,
    compute_template_accuracy,
    compute_clarification_metrics
)

def load_requests(filepaths: List[str]) -> List[Dict[str, str]]:
    requests = []
    for fp in filepaths:
        if os.path.exists(fp):
            with open(fp, "r") as f:
                data = json.load(f)
                requests.extend(data.get("requests", []))
        else:
            print(f"Warning: {fp} not found.")
    return requests

def run_benchmark(verbose: bool = False):
    print("Loading Ground Truth and Raw Requests...")
    ground_truth = load_ground_truth("data/eval_cases.json")
    raw_requests = load_requests(["data/test_requests.json", "data/custom-hard-requests.json"])
    
    if not raw_requests:
        print("No test requests found. Exiting.")
        return
        
    print(f"Loaded {len(raw_requests)} requests. Initializing TriageAgent (LLM Provider: {os.environ.get('LLM_PROVIDER', 'gemini')})...")
    agent = TriageAgent()
    
    # Prediction Arrays
    y_true_action = []
    y_pred_action = []
    
    y_true_urgency = []
    y_pred_urgency = []
    
    y_true_temp = []
    y_pred_temp = []
    
    y_true_missing_list = []
    y_pred_missing_list = []
    
    y_true_binary = []  # 1 if predicted action == ground truth action, else 0
    y_prob = []
    
    loop_counts = []
    generated_questions_list = []
    
    results_log = []
    
    print("\nExecuting LangGraph Triage Loop over 11 benchmark cases...")
    print("Note: Adding 20s sleep between calls to respect 15 RPM free-tier limits on 1.5-flash.")
    
    for i, req in enumerate(raw_requests):
        req_id = req["id"]
        channel = req["channel"]
        text = req["raw_text"]
        
        gt = ground_truth.get(req_id)
        if not gt:
            print(f"Warning: No ground truth mapping found for {req_id}. Skipping.")
            continue
            
        print(f"[{i+1}/{len(raw_requests)}] Processing {req_id}...")
        
        # Invoke LangGraph
        try:
            final_state = agent.app.invoke({
                "request_id": req_id,
                "channel": channel,
                "raw_text": text,
                "audit_trace": []
            })
            decision = final_state.get("final_decision")
            if decision is None:
                print(f"Error: decision is None! Final state keys: {final_state.keys()}")
                print(f"final_state: {final_state}")
                continue
        except Exception as e:
            print(f"Error processing {req_id}: {e}")
            continue
            
        # Safely extract predictions
        pred_action = decision.initial_routing_action if decision.initial_routing_action else "UNKNOWN"
        pred_urgency = decision.extracted_entities.assessed_real_urgency if decision.extracted_entities else "UNKNOWN"
        pred_temp = decision.match_result.top_template_id if decision.match_result else None
        pred_missing = decision.initial_missing_fields if decision.initial_missing_fields is not None else []
        pred_conf = decision.routing_result.confidence_score if decision.routing_result else 0.0
        
        clarif_qs = decision.clarification_state.clarification_questions if decision.clarification_state else []
        q_targets = [q.target_field for q in clarif_qs]
        l_count = decision.clarification_state.loop_count if decision.clarification_state else 0
        
        # Append to metrics arrays
        y_true_action.append(gt.expected_routing_action)
        y_pred_action.append(pred_action)
        
        y_true_urgency.append(gt.expected_real_urgency)
        y_pred_urgency.append(pred_urgency)
        
        y_true_temp.append(gt.expected_template)
        y_pred_temp.append(pred_temp)
        
        y_true_missing_list.append(gt.expected_missing_fields)
        y_pred_missing_list.append(pred_missing)
        
        is_correct = 1 if (gt.expected_routing_action == pred_action) else 0
        y_true_binary.append(is_correct)
        y_prob.append(pred_conf)
        
        loop_counts.append(l_count)
        generated_questions_list.append(q_targets)
            
        results_log.append({
            "request_id": req_id,
            "raw_text": text,
            "ground_truth": {
                "action": gt.expected_routing_action,
                "urgency": gt.expected_real_urgency,
                "template": gt.expected_template,
                "missing_fields": gt.expected_missing_fields
            },
            "predicted": {
                "action": pred_action,
                "urgency": pred_urgency,
                "template": pred_temp,
                "missing_fields": pred_missing,
                "confidence": pred_conf
            },
            "rationale": decision.finalizer_synthesis.decision_rationale if decision.finalizer_synthesis else "None",
            "is_correct": is_correct == 1
        })
        
        if verbose:
            print(f"  -> GT Action: {gt.expected_routing_action} | Pred Action: {pred_action}")
            print(f"  -> GT Urgency: {gt.expected_real_urgency} | Pred Urgency: {pred_urgency}")
            print(f"  -> Rationale: {decision.finalizer_synthesis.decision_rationale if decision.finalizer_synthesis else 'None'}\n")
            
        # Free-tier rate limiting protection
        # Each case triggers ~4 LLM calls in the graph. The limit is 15 RPM for 1.5-flash.
        time.sleep(20)
        
    print("\n=======================================================")
    print("      DATA SCIENCE BENCHMARK EVALUATION REPORT")
    print("=======================================================")
    
    # Compute Metrics
    conf_matrix = compute_confusion_matrix(y_true_action, y_pred_action)
    safety_metrics = compute_safety_metrics(y_true_urgency, y_pred_urgency)
    temp_acc = compute_template_accuracy(y_true_temp, y_pred_temp)
    
    jaccards = [compute_jaccard_iou(t, p) for t, p in zip(y_true_missing_list, y_pred_missing_list)]
    mean_jaccard = sum(jaccards) / len(jaccards) if jaccards else 0.0
    
    calib = compute_calibration(y_true_binary, y_prob)
    clarif = compute_clarification_metrics(loop_counts, y_true_missing_list, generated_questions_list)
    
    print(f"\n1. Action Routing Performance:")
    print(f"   - Macro-Averaged F1:   {conf_matrix['macro_f1']:.3f} (Target: >= 0.850)")
    print(f"   - Weighted F1:         {conf_matrix['weighted_f1']:.3f}")
    print(f"   - CONFIDENT Precision: {conf_matrix['CONFIDENT_RECOMMENDATION']['precision']:.3f}, Recall: {conf_matrix['CONFIDENT_RECOMMENDATION']['recall']:.3f}")
    print(f"   - CLARIFY Precision:   {conf_matrix['NEEDS_CLARIFICATION']['precision']:.3f}, Recall: {conf_matrix['NEEDS_CLARIFICATION']['recall']:.3f}")
    print(f"   - HUMAN Precision:     {conf_matrix['ROUTE_TO_HUMAN']['precision']:.3f}, Recall: {conf_matrix['ROUTE_TO_HUMAN']['recall']:.3f}")
    
    print(f"\n2. Safety Critical Metrics:")
    print(f"   - P1 Safety Recall:    {safety_metrics['p1_recall'] * 100:.1f}% (Target: 100.0%)")
    print(f"   - P1 False Neg Rate:   {safety_metrics['p1_fnr'] * 100:.1f}% (Target: 0.0%)")
    print(f"   - Safety Cost Penalty: {safety_metrics['cost_safety']}")
    
    print(f"\n3. Template & Gap Extraction:")
    print(f"   - Template Accuracy:   {temp_acc * 100:.1f}% (Target: >= 90.0%)")
    print(f"   - Mean Jaccard IoU:    {mean_jaccard:.3f}")
    
    print(f"\n4. Confidence Calibration:")
    print(f"   - Brier Score:         {calib['brier_score']:.3f} (Target: <= 0.100)")
    print(f"   - Expected Calib Err:  {calib['ece']:.3f} (Target: <= 0.100)")
    
    print(f"\n5. Clarification Quality (Simulated Single-Turn):")
    print(f"   - Question Specificity:{clarif['question_specificity']:.3f}")
    print(f"   - Redundancy Index:    {clarif['redundancy_index']:.3f}")
    
    print("=======================================================")
    
    os.makedirs("data", exist_ok=True)
    with open("data/evaluation_results.json", "w") as f:
        json.dump(results_log, f, indent=2)
    print("Detailed prediction log saved to data/evaluation_results.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true", help="Print step-by-step predictions")
    args = parser.parse_args()
    
    if not os.environ.get("GEMINI_API_KEY"):
        print("CRITICAL WARNING: GEMINI_API_KEY environment variable is not set. Execution will likely fail.")
        
    run_benchmark(verbose=args.verbose)
