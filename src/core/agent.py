import os
from src.core.graph import create_triage_graph
from src.models import ServiceRouterDecision
from src.llm.factory import LLMClientFactory

class TriageAgent:
    """
    Primary interface for the Field Services Intelligent Dispatcher (FS-ID).
    Wraps the compiled LangGraph and handles initial state setup.
    """
    def __init__(self):
        # Ensure LLM Client is initialized
        _ = LLMClientFactory.get_client()
        self.app = create_triage_graph()
        self._export_graph_visualization()
        
    def _export_graph_visualization(self):
        """Exports the Mermaid visualization of the LangGraph to disk."""
        try:
            mermaid_str = self.app.get_graph().draw_mermaid()
            # Ensure docs directory exists
            os.makedirs("docs", exist_ok=True)
            with open("docs/graph_visualization.md", "w") as f:
                f.write("# FS-ID Agentic Loop Visualization\n\n")
                f.write("```mermaid\n")
                f.write(mermaid_str)
                f.write("\n```\n")
        except Exception as e:
            print(f"Warning: Failed to export graph visualization: {e}")
            
    def run(self, request_id: str, channel: str, raw_text: str) -> ServiceRouterDecision:
        """
        Executes the triage graph for a given inbound service request.
        """
        initial_state = {
            "request_id": request_id,
            "channel": channel,
            "raw_text": raw_text,
            "audit_trace": []
        }
        
        final_state = self.app.invoke(initial_state)
        
        return final_state.get("final_decision")
