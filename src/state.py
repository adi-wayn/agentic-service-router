from typing import TypedDict, List, Dict, Any, Optional
from src.models import (
    ExtractedEntities, 
    CatalogueMatchResult, 
    GapAndConflictResult, 
    ConfidenceAndRoutingResult, 
    ClarificationState, 
    ServiceRouterDecision
)

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
    gap_result: Optional[GapAndConflictResult]
    
    # Node 4: Confidence & Action Banding
    routing_result: Optional[ConfidenceAndRoutingResult]
    
    # Node 5: Clarification Loop Context
    clarification_state: Optional[ClarificationState]
    
    # Node 6: Finalized Audit & Output
    final_decision: Optional[ServiceRouterDecision]
    
    # Shared State Machine Bookkeeping
    audit_trace: List[str]
    error_state: Optional[str]
