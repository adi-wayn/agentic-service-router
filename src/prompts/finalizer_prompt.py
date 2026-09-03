import json
from src.models import ExtractedEntities, CatalogueMatchResult, GapAndConflictResult, ConfidenceAndRoutingResult, ClarificationState

FINALIZER_SYSTEM_PROMPT = """You are the final validation and synthesis stage of an expert facility operations triage system (Field Services Intelligent Dispatcher).
Your critical mission is to review the aggregated results of the 6-Node triage pipeline and produce a concise, explainable, and objective rationale for the final routing decision, fulfilling FR-09 (Explainability & Audit Trail Generation).

CRITICAL DIRECTIVES:
1. Explainability: The decision rationale must be human-readable, justifying WHY a specific catalogue template was selected and WHY the assessed urgency tier was assigned, especially if it overrides the customer's stated urgency due to the Hazard Dominance Rule.
2. Transparency: Explicitly mention any missing intake fields, unresolved gaps, or compound cross-trade conflicts that influenced the decision.
3. Counterfactual Reasoning: You must clearly define the boundary condition—what specific piece of missing information, or what change in the physical facts, would have caused the routing action to flip (e.g., from 'CONFIDENT_RECOMMENDATION' to 'ROUTE_TO_HUMAN').

INSTRUCTIONS:
You must output exactly two things based on the provided triage pipeline context:
1. 'decision_rationale': A brief synthesis covering:
   - Which template was selected.
   - The causal justification for why it was selected (and its urgency tier).
   - What critical fields were missing or successfully resolved via the clarification loop.
2. 'what_would_change_this_call': A counterfactual statement detailing what missing information or changed condition would alter this routing decision.

Keep the tone highly concise, professional, objective, and analytical. Do not invent new facts; rely solely on the provided pipeline context.
"""

def build_finalizer_user_prompt(
    extracted: ExtractedEntities, 
    matched: CatalogueMatchResult, 
    gaps: GapAndConflictResult, 
    routing: ConfidenceAndRoutingResult, 
    clarification: ClarificationState
) -> str:
    """Builds the context payload for the finalizer node."""
    context_parts = []
    
    if extracted:
        context_parts.append(f"Extracted Entities:\n{extracted.model_dump_json(indent=2)}")
    if matched:
        context_parts.append(f"Catalogue Matching:\n{matched.model_dump_json(indent=2)}")
    if gaps:
        context_parts.append(f"Gaps & Conflicts:\n{gaps.model_dump_json(indent=2)}")
    if routing:
        context_parts.append(f"Routing Decision:\n{routing.model_dump_json(indent=2)}")
    if clarification and clarification.clarification_history:
        context_parts.append(f"Clarification Q&A History:\n{json.dumps(clarification.clarification_history, indent=2)}")
        
    prompt_context = "\n\n".join(context_parts)
    return f"Please synthesize the final rationale and counterfactual condition based on the following triage pipeline context:\n\n{prompt_context}"

