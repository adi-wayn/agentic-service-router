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

class ServiceRouterDecision(BaseModel):
    request_id: str
    selected_template_id: Optional[str] = Field(default=None, description="Matched template ID from catalogue, or null")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Calibrated confidence score 0.0 to 1.0")
    routing_action: Literal["CONFIDENT_RECOMMENDATION", "NEEDS_CLARIFICATION", "ROUTE_TO_HUMAN"]
    real_urgency: Literal["P1", "P2", "P3"]
    extracted_intake: Dict[str, Any] = Field(default_factory=dict)
    missing_required_fields: List[str] = Field(default_factory=list)
    clarification_questions: List[ClarificationQuestion] = Field(default_factory=list)
    decision_rationale: str = Field(..., description="Concise human-readable rationale")
    what_would_change_this_call: str = Field(..., description="Counterfactual condition that would flip this call")
    loop_count: int = 0
    audit_trace: List[str] = Field(default_factory=list, description="Sequential audit ledger of reasoning steps")
