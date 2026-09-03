from src.state import TriageState
from src.models import ClarificationState, ClarificationLLMOutput
from src.llm.factory import LLMClientFactory
from src.prompts.clarifier_prompt import CLARIFIER_SYSTEM_PROMPT, build_clarifier_user_prompt
from src.prompts.simulated_answers import get_simulated_answer

def clarifier_node(state: TriageState) -> TriageState:
    """
    Node 5a: Clarifier Node
    If the routing action is NEEDS_CLARIFICATION, asks the LLM to generate targeted questions.
    """
    if "audit_trace" not in state:
        state["audit_trace"] = []
        
    routing_result = state.get("routing_result")
    if not routing_result or routing_result.routing_action != "NEEDS_CLARIFICATION":
        return state

    if "clarification_state" not in state or state["clarification_state"] is None:
        state["clarification_state"] = ClarificationState()
        
    clarification_state = state["clarification_state"]
    
    # Gather context
    raw_text = state.get("raw_text", "")
    gap_result = state.get("gap_result")
    missing_fields = gap_result.missing_required_fields if gap_result else []
    conflicts = gap_result.detected_conflicts if gap_result else []
    
    prompt = build_clarifier_user_prompt(
        raw_text, 
        missing_fields, 
        conflicts, 
        clarification_state.clarification_history
    )
    
    client = LLMClientFactory.get_client()
    try:
        llm_response = client.generate_structured(
            prompt=prompt,
            schema=ClarificationLLMOutput,
            system_instruction=CLARIFIER_SYSTEM_PROMPT
        )
        
        clarification_state.clarification_questions = llm_response.questions
        
        q_texts = [q.question_text for q in llm_response.questions]
        state["audit_trace"].append(f"Clarification generated {len(q_texts)} question(s).")
        
    except Exception as e:
        state["error_state"] = f"Clarifier generation failed: {str(e)}"
        state["audit_trace"].append(f"Clarifier error: {str(e)}")
        
    return state


def feedback_node(state: TriageState) -> TriageState:
    """
    Node 5b: Feedback Ingestion Node
    Simulates user answers, appends to history, and updates raw_text so Node 1 can re-extract.
    """
    if "audit_trace" not in state:
        state["audit_trace"] = []
        
    clarification_state = state.get("clarification_state")
    if not clarification_state or not clarification_state.clarification_questions:
        return state
        
    # Simulate user answers
    new_qa_text = "\n\n--- Customer Follow-Up ---\n"
    answered = 0
    
    for q in clarification_state.clarification_questions:
        # Use our simulated answers database
        simulated_answer = get_simulated_answer(q.question_text, q.target_field)
        
        clarification_state.clarification_history.append({
            "question": q.question_text,
            "answer": simulated_answer
        })
        new_qa_text += f"Q: {q.question_text}\nA: {simulated_answer}\n"
        answered += 1
        
    # Inject back into raw_text so Node 1 sees it on the next loop
    state["raw_text"] = state.get("raw_text", "") + new_qa_text
    
    # Reset active questions and bump loop count
    clarification_state.clarification_questions = []
    clarification_state.loop_count += 1
    
    state["audit_trace"].append(f"Feedback ingested for {answered} question(s). Loop count now {clarification_state.loop_count}.")
    
    return state
