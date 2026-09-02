from typing import TypedDict, List, Dict, Any, Optional
from src.models import ExtractedEntities, CatalogueMatchResult

class TriageState(TypedDict, total=False):
    # Inbound Payload
    request_id: str
    channel: str
    raw_text: str
    
    # Catalogue Context (Dynamic runtime injection)
    catalogue_templates: List[Dict[str, Any]]
    
    # Node 1: Extracted Physical Facts & Hazards
    extracted_entities: Optional[ExtractedEntities]
    
    # Node 2: Template Candidate Matching
    match_result: Optional[CatalogueMatchResult]
    
    # Node 3: Gaps & Conflict Detection
    missing_required_fields: List[str]
    blocking_fields_missing: bool
    detected_conflicts: List[str]
    is_cross_trade_collision: bool
    
    # Node 4: Confidence & Action Banding
    confidence_score: float
    routing_action: str  # CONFIDENT_RECOMMENDATION | NEEDS_CLARIFICATION | ROUTE_TO_HUMAN
    
    # Node 5: Clarification Loop Context
    clarification_questions: List[Dict[str, Any]]
    clarification_history: List[Dict[str, str]]
    loop_count: int
    
    # Node 6: Finalized Audit & Output
    decision_rationale: str
    counterfactual_condition: str
    audit_trace: List[str]
    final_output: Optional[Dict[str, Any]]
    error_state: Optional[str]
