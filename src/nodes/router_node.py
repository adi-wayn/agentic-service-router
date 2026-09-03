from typing import List, Dict, Any
from src.state import TriageState
from src.models import ConfidenceAndRoutingResult
from src.catalogue import ServiceCatalogue

def calculate_calibrated_confidence(
    signal_score: float,
    required_fields: List[str],
    extracted_fields: Dict[str, Any],
    conflicts: List[str],
    is_cross_trade_collision: bool,
    is_out_of_catalogue: bool
) -> float:
    """
    Calculates the non-linear composite confidence score based on the strict formula
    defined in the SDD/SRS.
    """
    if is_out_of_catalogue:
        return 0.10
    if is_cross_trade_collision:
        return 0.30
        
    if not required_fields:
        completeness_ratio = 1.0
        missing_count = 0
    else:
        present_count = sum(1 for f in required_fields if extracted_fields.get(f))
        missing_count = len(required_fields) - present_count
        completeness_ratio = present_count / len(required_fields)
        
    w_signal = 0.60
    w_fields = 0.40
    base_confidence = (w_signal * signal_score) + (w_fields * completeness_ratio)
    
    conflict_penalty = min(0.40, len(conflicts) * 0.20)
    
    intake_penalty = 0.0
    if missing_count > 0:
        intake_penalty += 0.25 * missing_count
        
    final_score = base_confidence - conflict_penalty - intake_penalty
    return max(0.0, min(1.0, round(final_score, 2)))

def confidence_and_routing_node(state: TriageState) -> TriageState:
    """
    Node 4: Confidence & Routing Node
    Aggregates upstream data to compute final confidence and assigns a strict routing action.
    """
    if "audit_trace" not in state:
        state["audit_trace"] = []
        
    extracted = state.get("extracted_entities")
    match_result = state.get("match_result")
    gap_result = state.get("gap_result")
    
    if not extracted or not match_result or not gap_result:
        state["audit_trace"].append("Router Node aborted: Missing prerequisite state.")
        return state

    # Extract dynamic payload to check for completeness
    extracted_dict = extracted.model_dump(exclude_none=True, exclude_unset=True)

    # Retrieve required fields based on the selected template (if any)
    required_fields = []
    if match_result.top_template_id:
        catalogue = ServiceCatalogue()
        required_fields = catalogue.get_required_fields(match_result.top_template_id)
        
    # Calculate non-linear confidence
    top_candidate = match_result.candidates[0] if match_result.candidates else None
    signal_score = top_candidate.signal_score if top_candidate else 0.0
    
    confidence = calculate_calibrated_confidence(
        signal_score=signal_score,
        required_fields=required_fields,
        extracted_fields=extracted_dict,
        conflicts=gap_result.detected_conflicts,
        is_cross_trade_collision=gap_result.is_cross_trade_collision,
        is_out_of_catalogue=match_result.is_out_of_catalogue
    )
    
    # Apply Strict Banding Thresholds
    action = "ROUTE_TO_HUMAN"
    if confidence >= 0.75:
        action = "CONFIDENT_RECOMMENDATION"
    elif 0.40 <= confidence < 0.75:
        action = "NEEDS_CLARIFICATION"
        
    routing_result = ConfidenceAndRoutingResult(
        confidence_score=confidence,
        routing_action=action
    )
    
    state["routing_result"] = routing_result
    state["audit_trace"].append(f"Router Node complete: Score={confidence}, Action={action}")
    
    return state
