from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class SafetyRiskAssessment(BaseModel):
    has_immediate_hazard: bool = Field(..., description="True if fire, active flooding, thermal runaway, trapped occupants")
    hazard_type: Optional[str] = Field(default=None, description="Physical nature of hazard (e.g., Electrical Arcing, Asbestos)")
    is_life_safety_affected: bool = Field(default=False, description="True if immediate human safety is threatened")

class ExtractedEntities(BaseModel):
    primary_trade: Literal["HVAC", "Plumbing", "Electrical", "Security / Access", "General", "Multi-Trade", "Unknown"]
    secondary_trade: Optional[str] = Field(default=None, description="Co-occurring trade discipline in compound incidents")
    site_location: Optional[str] = Field(default=None, description="Identified building address or campus")
    affected_area_or_room: Optional[str] = Field(default=None, description="Specific floor, room, or wing")
    specific_equipment: Optional[str] = Field(default=None, description="Specific appliance, machine, or fixture")
    symptom_description: str = Field(..., description="Objective physical manifestation")
    stated_urgency: Literal["P1", "P2", "P3", "Unspecified"] = Field(..., description="Explicit customer sentiment")
    assessed_real_urgency: Literal["P1", "P2", "P3"] = Field(..., description="Factual physical urgency tier")
    urgency_rationale: str = Field(..., description="Detailed causal explanation of stated vs real urgency delta")
    safety_assessment: SafetyRiskAssessment
    access_window_or_availability: Optional[str] = Field(default=None, description="Reported site access window")
    on_site_contact_info: Optional[str] = Field(default=None, description="On-site contact name or phone")
    detected_conflicts: List[str] = Field(default_factory=list, description="Documented contradictions or trade collisions")

class ClarificationQuestion(BaseModel):
    target_field: str = Field(..., description="The specific missing intake field or ambiguity being resolved")
    question_text: str = Field(..., description="Targeted, courteous inquiry to customer")
    why_critical: str = Field(..., description="Operational justification for why this parameter is required")



class CandidateMatch(BaseModel):
    template_id: str = Field(description="Exact ID from service_catalogue.json")
    category: str = Field(description="Trade category (e.g., HVAC, Electrical, Plumbing)")
    signal_score: float = Field(
        ge=0.0, le=1.0, 
        description="Semantic signal overlap score calibrated according to the rubric (0.0 to 1.0)"
    )
    matched_signals: List[str] = Field(
        default_factory=list, 
        description="Specific signals from the template matched in the request"
    )
    match_rationale: str = Field(description="Brief explanation for why this score was assigned")

class CatalogueMatchResult(BaseModel):
    candidates: List[CandidateMatch] = Field(
        description="Ranked list of evaluated candidate templates, sorted descending by signal_score"
    )
    top_template_id: Optional[str] = Field(
        default=None, 
        description="ID of the highest-scoring candidate, or null if out-of-catalogue"
    )
    is_out_of_catalogue: bool = Field(
        default=False, 
        description="True if no template in the catalogue achieves a score >= 0.40"
    )
    cross_trade_detected: bool = Field(
        default=False, 
        description="True if top candidates span multiple trade categories with high scores"
    )

class GapAndConflictResult(BaseModel):
    missing_required_fields: List[str] = Field(default_factory=list, description="List of required intake fields missing from extraction")
    detected_conflicts: List[str] = Field(default_factory=list, description="List of detected conflicts, including cross-trade collisions")
    is_cross_trade_collision: bool = Field(default=False, description="True if a fatal cross-trade collision is detected")

class ConfidenceAndRoutingResult(BaseModel):
    confidence_score: float = Field(ge=0.0, le=1.0, description="Final calculated confidence score")
    routing_action: Literal["CONFIDENT_RECOMMENDATION", "NEEDS_CLARIFICATION", "ROUTE_TO_HUMAN"] = Field(description="The determined routing action")

class ClarificationState(BaseModel):
    clarification_questions: List[ClarificationQuestion] = Field(default_factory=list, description="Currently active clarification questions")
    clarification_history: List[Dict[str, str]] = Field(default_factory=list, description="History of Q&A during clarification loops")
    loop_count: int = Field(default=0, description="Number of clarification loops completed")

class ServiceRouterDecision(BaseModel):
    request_id: str
    
    # Node 1-5 Encapsulated Outputs
    extracted_entities: Optional[ExtractedEntities] = None
    match_result: Optional[CatalogueMatchResult] = None
    gap_result: Optional[GapAndConflictResult] = None
    routing_result: Optional[ConfidenceAndRoutingResult] = None
    clarification_state: Optional[ClarificationState] = None
    
    # Node 6 Finalizer Synthesis
    decision_rationale: str = Field(..., description="Concise human-readable rationale")
    what_would_change_this_call: str = Field(..., description="Counterfactual condition that would flip this call")
    audit_trace: List[str] = Field(default_factory=list, description="Sequential audit ledger of reasoning steps")
