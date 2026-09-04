from src.core.state import TriageState
from src.models import CatalogueMatchResult
from src.llm.factory import LLMClientFactory
from src.prompts.matcher_prompt import MATCHER_SYSTEM_PROMPT, build_matcher_user_prompt
from src.catalogue import ServiceCatalogue


def catalogue_match_node(state: TriageState) -> TriageState:
    """
    Node 2: Template Matcher Node
    Performs deterministic pre-filtering followed by non-deterministic
    semantic similarity scoring via the LLM.
    """
    if "audit_trace" not in state:
        state["audit_trace"] = []

    extracted_entities = state.get("extracted_entities")
    if not extracted_entities:
        state["error_state"] = "No extracted entities available for matching."
        return state

    primary_trade = extracted_entities.primary_trade
    secondary_trade = extracted_entities.secondary_trade

    all_templates = ServiceCatalogue().templates

    # Deterministic Pre-Filtering
    filtered_templates = []
    if primary_trade in ["Unknown", "Multi-Trade"]:
        filtered_templates = all_templates
    else:
        target_trades = {primary_trade}
        if secondary_trade:
            target_trades.add(secondary_trade)

        filtered_templates = [
            t for t in all_templates if t.get("category") in target_trades
        ]

    # Fallback to all if filter is too aggressive
    if not filtered_templates:
        filtered_templates = all_templates

    state["audit_trace"].append(
        f"Matcher pre-filtering: evaluated trades {primary_trade}/{secondary_trade}, "
        f"filtered {len(all_templates)} templates down to {len(filtered_templates)}."
    )

    client = LLMClientFactory.get_client()
    user_prompt = build_matcher_user_prompt(
        extracted_entities.model_dump(), filtered_templates
    )

    try:
        match_result: CatalogueMatchResult = client.generate_structured(
            prompt=user_prompt,
            schema=CatalogueMatchResult,
            system_instruction=MATCHER_SYSTEM_PROMPT,
        )

        # Sort candidates deterministically by score
        candidates = match_result.candidates
        candidates.sort(key=lambda x: x.signal_score, reverse=True)

        # Double check thresholds deterministically
        if candidates and candidates[0].signal_score < 0.40:
            match_result.is_out_of_catalogue = True
            match_result.top_template_id = None

        if not candidates:
            match_result.is_out_of_catalogue = True
            match_result.top_template_id = None

        # Update state directly with the Pydantic model
        state["match_result"] = match_result

        state["audit_trace"].append(
            f"Matcher complete. Top candidate: {match_result.top_template_id}. "
            f"Out of catalogue: {match_result.is_out_of_catalogue}. "
            f"Cross-trade collision: {match_result.cross_trade_detected}."
        )

    except Exception as e:
        state["error_state"] = f"Matcher failed: {str(e)}"
        state["audit_trace"].append(f"Matcher error: {str(e)}")

    return state
