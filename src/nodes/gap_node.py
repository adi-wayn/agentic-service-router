from typing import List, Dict, Any, Optional
from src.state import TriageState
from src.models import GapAndConflictResult
from src.catalogue import ServiceCatalogue

# Schema Bridge: Maps the read-only legacy catalog fields to our strict Pydantic model
FIELD_MAPPING = {
    "site_location": "site_location",
    "affected_area": "affected_area_or_room",
    "symptom": "symptom_description",
    "access_window": "access_window_or_availability",
    "on_site_contact": "on_site_contact_info",
    "unit_type": "specific_equipment",
    "preferred_dates": "access_window_or_availability"
}

def gap_and_conflict_node(state: TriageState) -> TriageState:
    """
    Node 3: Conflict & Gap Detection Node
    Purely deterministic Python algorithm. No LLM used.
    Calculates exact missing fields and algorithmic cross-trade collision margin.
    """
    if "audit_trace" not in state:
        state["audit_trace"] = []
        
    extracted = state.get("extracted_entities")
    match_result = state.get("match_result")
    
    if not extracted or not match_result:
        state["audit_trace"].append("Gap Node aborted: Missing required state (extracted_entities or match_result).")
        return state

    missing_fields: List[str] = []
    detected_conflicts: List[str] = list(extracted.detected_conflicts)
    is_cross_trade = False

    # 1. Evaluate Algorithmic Cross-Trade Collision Detector
    candidates = match_result.candidates
    if len(candidates) >= 2:
        top1 = candidates[0]
        top2 = candidates[1]
        
        # Cross-Trade Tie Logic from SDD 5.1
        if top1.category != top2.category and top1.signal_score >= 0.65 and (top1.signal_score - top2.signal_score) <= 0.15:
            is_cross_trade = True
            conflict_msg = f"Cross-trade collision detected between {top1.category} ({top1.signal_score}) and {top2.category} ({top2.signal_score})."
            detected_conflicts.append(conflict_msg)
            state["audit_trace"].append(conflict_msg)

    # 2. Evaluate Missing Required Fields Diff
    if match_result.is_out_of_catalogue or not match_result.top_template_id:
        state["audit_trace"].append("Gap Node: Bypassing field diff because request is out-of-catalogue.")
    else:
        # Find the selected template in O(1) via the singleton hash map
        catalogue = ServiceCatalogue()
        
        # Verify the template exists in O(1)
        if catalogue.get_template_by_id(match_result.top_template_id):
            # Fetch just the required fields list using the helper method
            required_fields = catalogue.get_required_fields(match_result.top_template_id)
            
            for req_field in required_fields:
                # 1. Check if it's a known mapped field in the Pydantic schema
                model_field = FIELD_MAPPING.get(req_field, req_field)
                val = getattr(extracted, model_field, None)
                
                # If None, empty string, or empty list
                if not val:
                    missing_fields.append(req_field)
                        
            state["audit_trace"].append(f"Gap Node: Missing required fields determined: {missing_fields}")
        else:
            state["audit_trace"].append(f"Gap Node Warning: Template {match_result.top_template_id} not found in catalogue.")

    # 3. Create Result Model
    gap_result = GapAndConflictResult(
        missing_required_fields=missing_fields,
        detected_conflicts=detected_conflicts,
        is_cross_trade_collision=is_cross_trade
    )
    
    state["gap_result"] = gap_result
    return state
