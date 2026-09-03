from typing import List, Dict

CLARIFIER_SYSTEM_PROMPT = """You are an expert dispatch triage agent for the Field Services Intelligent Dispatcher (FS-ID).
The inbound service request is currently suspended because it is missing critical discriminatory information or contains unresolved compound conflicts that prevent confident routing.

CRITICAL DIRECTIVES:
1. Targeted Inquiries: Formulate 1 to 3 highly specific, courteous questions directed at the customer.
2. Gap Resolution: These questions MUST strictly address the 'missing_required_fields' or 'detected_conflicts' provided in the context. Do not ask broad, open-ended questions. 
3. Avoid Redundancy: You MUST review the 'Prior Q&A History'. Do not ask for information that the customer has already provided in previous clarification loops.

INSTRUCTIONS:
- Each question must include a brief operational justification (why_critical) explaining to the user why we need this information (e.g., 'To ensure we send the right technician...').
- Output ONLY the requested JSON schema containing the list of ClarificationQuestions.
"""

def build_clarifier_user_prompt(
    raw_text: str, 
    missing_fields: List[str], 
    conflicts: List[str], 
    clarification_history: List[Dict[str, str]]
) -> str:
    """Builds the context payload for the clarifier node."""
    prompt = f"ORIGINAL REQUEST:\n{raw_text}\n\n"
    
    if missing_fields:
        prompt += f"MISSING REQUIRED FIELDS:\n{missing_fields}\n\n"
        
    if conflicts:
        prompt += f"DETECTED CONFLICTS:\n{conflicts}\n\n"
        
    if clarification_history:
        prompt += f"PRIOR Q&A HISTORY (DO NOT REPEAT THESE):\n{clarification_history}\n\n"
        
    prompt += "TASK:\nGenerate up to 3 targeted clarification questions to resolve the gaps/conflicts above."
    return prompt

