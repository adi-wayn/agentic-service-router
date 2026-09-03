import json
from src.state import TriageState
from src.models import FinalizerSynthesis, ServiceRouterDecision
from src.llm.factory import LLMClientFactory
from src.prompts.finalizer_prompt import FINALIZER_SYSTEM_PROMPT, build_finalizer_user_prompt

def finalize_decision_node(state: TriageState) -> TriageState:
    """
    Node 6: Finalize Decision Node
    Synthesizes the rationale and assembles the final ServiceRouterDecision.
    """
    if "audit_trace" not in state:
        state["audit_trace"] = []
        
    client = LLMClientFactory.get_client()
    
    # 1. Build the synthesis context from the previous nodes
    prompt = build_finalizer_user_prompt(
        state.get("extracted_entities"),
        state.get("match_result"),
        state.get("gap_result"),
        state.get("routing_result"),
        state.get("clarification_state")
    )
    
    try:
        # 2. Call the LLM to generate the FinalizerSynthesis
        synthesis: FinalizerSynthesis = client.generate_structured(
            prompt=prompt,
            schema=FinalizerSynthesis,
            system_instruction=FINALIZER_SYSTEM_PROMPT
        )
        
        # 3. Assemble the final ServiceRouterDecision
        decision = ServiceRouterDecision(
            request_id=state.get("request_id", "UNKNOWN"),
            extracted_entities=state.get("extracted_entities"),
            match_result=state.get("match_result"),
            gap_result=state.get("gap_result"),
            initial_missing_fields=state.get("initial_missing_fields"),
            routing_result=state.get("routing_result"),
            initial_routing_action=state.get("initial_routing_action"),
            clarification_state=state.get("clarification_state"),
            finalizer_synthesis=synthesis,
            audit_trace=state["audit_trace"].copy()
        )
        
        state["final_decision"] = decision
        state["audit_trace"].append("Finalizer complete. Rationale synthesized.")
        
    except Exception as e:
        state["error_state"] = f"Finalizer synthesis failed: {str(e)}"
        state["audit_trace"].append(f"Finalizer error: {str(e)}")
        
    return state
