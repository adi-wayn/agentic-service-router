from typing import List
from src.core.state import TriageState
from src.models import ConfidenceAndRoutingResult


def calculate_calibrated_confidence(
    signal_score: float,
    conflicts: List[str],
    is_cross_trade_collision: bool,
    is_out_of_catalogue: bool,
    missing_fields: List[str],
) -> float:
    """
    Calculates the non-linear composite confidence score based on the strict formula.
    """
    if is_out_of_catalogue:
        return 0.10
    if is_cross_trade_collision:
        return 0.30

    # Base confidence strictly from the Matcher's signal score
    confidence = signal_score

    # Penalize confidence only for conflicts, not for simply missing fields
    conflict_penalty = min(0.40, len(conflicts) * 0.20)
    confidence = max(0.0, min(1.0, confidence - conflict_penalty))

    # If there are missing fields, we enforce that confidence must fall into the Clarification Band [0.45, 0.70]
    # because missing fields means we confidently know what to ask the user.
    if missing_fields:
        confidence = max(0.45, min(0.70, confidence))

    return round(confidence, 2)


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

    # Calculate calibrated confidence using the helper function
    top_candidate = match_result.candidates[0] if match_result.candidates else None
    signal_score = top_candidate.signal_score if top_candidate else 0.0

    confidence = calculate_calibrated_confidence(
        signal_score=signal_score,
        conflicts=gap_result.detected_conflicts,
        is_cross_trade_collision=gap_result.is_cross_trade_collision,
        is_out_of_catalogue=match_result.is_out_of_catalogue,
        missing_fields=gap_result.missing_required_fields,
    )

    # Apply Strict Banding Thresholds based on logic rules
    action = "ROUTE_TO_HUMAN"

    if match_result.is_out_of_catalogue or gap_result.is_cross_trade_collision:
        action = "ROUTE_TO_HUMAN"
    elif gap_result.missing_required_fields:
        action = "NEEDS_CLARIFICATION"
    else:
        if confidence >= 0.75:
            action = "CONFIDENT_RECOMMENDATION"
        elif 0.40 <= confidence < 0.75:
            action = "NEEDS_CLARIFICATION"
        else:
            action = "ROUTE_TO_HUMAN"

    routing_result = ConfidenceAndRoutingResult(
        confidence_score=confidence, routing_action=action
    )

    if "initial_routing_action" not in state:
        state["initial_routing_action"] = action

    state["routing_result"] = routing_result
    state["audit_trace"].append(
        f"Router Node complete: Score={confidence}, Action={action}"
    )

    return state
