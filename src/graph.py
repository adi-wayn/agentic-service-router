from langgraph.graph import StateGraph, END
from src.state import TriageState
from src.nodes.extractor_node import extract_and_analyze_node
from src.nodes.matcher_node import catalogue_match_node
from src.nodes.gap_node import gap_and_conflict_node
from src.nodes.router_node import confidence_and_routing_node
from src.nodes.clarifier_node import clarifier_node, feedback_node
from src.nodes.finalizer_node import finalize_decision_node

def route_conditional_edge(state: TriageState) -> str:
    routing_result = state.get("routing_result")
    
    if not routing_result:
        return "finalize_node"
        
    action = routing_result.routing_action
    
    clarification_state = state.get("clarification_state")
    loop_count = clarification_state.loop_count if clarification_state else 0
    
    if action == "CONFIDENT_RECOMMENDATION":
        return "finalize_node"
    elif action == "NEEDS_CLARIFICATION":
        if loop_count >= 2:
            state["audit_trace"].append("Clarification limit reached (2 turns). Escalating to Human.")
            # Force escalate to human when loops run out (Production Reality)
            routing_result.routing_action = "ROUTE_TO_HUMAN"
            return "finalize_node"
        return "clarifier_node"
    else:  # ROUTE_TO_HUMAN
        return "finalize_node"


def create_triage_graph():
    workflow = StateGraph(TriageState)
    
    # Register Nodes
    workflow.add_node("extractor_node", extract_and_analyze_node)
    workflow.add_node("matcher_node", catalogue_match_node)
    workflow.add_node("gap_node", gap_and_conflict_node)
    workflow.add_node("router_node", confidence_and_routing_node)
    workflow.add_node("clarifier_node", clarifier_node)
    workflow.add_node("feedback_node", feedback_node)
    workflow.add_node("finalize_node", finalize_decision_node)
    
    # Set Edges
    workflow.set_entry_point("extractor_node")
    workflow.add_edge("extractor_node", "matcher_node")
    workflow.add_edge("matcher_node", "gap_node")
    workflow.add_edge("gap_node", "router_node")
    
    # Conditional Branching
    workflow.add_conditional_edges("router_node", route_conditional_edge, {
        "finalize_node": "finalize_node",
        "clarifier_node": "clarifier_node"
    })
    
    # Clarification Loop Edges
    workflow.add_edge("clarifier_node", "feedback_node")
    workflow.add_edge("feedback_node", "extractor_node")
    
    # Terminal Edge
    workflow.add_edge("finalize_node", END)
    
    return workflow.compile()
