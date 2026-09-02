from typing import Any, Dict
from src.state import TriageState
from src.models import ExtractedEntities
from src.llm.factory import LLMClientFactory
from src.prompts.extractor_prompt import EXTRACTOR_SYSTEM_PROMPT, build_extractor_user_prompt
import traceback

def extract_and_analyze_node(state: TriageState) -> TriageState:
    """
    Node 1: Extractor & Hazard Node
    Ingests raw request text and extracts normalized entities, stated urgency, 
    real physical urgency, and safety signals.
    """
    raw_text = state.get("raw_text", "")
    
    if "audit_trace" not in state:
        state["audit_trace"] = []
        
    if not raw_text:
        state["error_state"] = "Empty raw_text provided to extractor_node."
        state["audit_trace"].append("Extraction aborted: Empty raw_text.")
        return state
        
    client = LLMClientFactory.get_client()
    user_prompt = build_extractor_user_prompt(raw_text)
    
    try:
        # Call LLM to extract structured entities
        extracted_entities_obj: ExtractedEntities = client.generate_structured(
            prompt=user_prompt,
            schema=ExtractedEntities,
            system_prompt=EXTRACTOR_SYSTEM_PROMPT
        )
        
        # Populate the state with the Pydantic model directly
        state["extracted_entities"] = extracted_entities_obj
        
        state["audit_trace"].append(
            f"Extraction complete. Detected real urgency: {extracted_entities_obj.assessed_real_urgency}. "
            f"Hazard detected: {extracted_entities_obj.safety_assessment.has_immediate_hazard}."
        )
        
    except Exception as e:
        state["error_state"] = f"Extraction failed: {str(e)}"
        state["audit_trace"].append(f"Extraction error: {str(e)}")
        
    return state
