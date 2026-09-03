"""
Main entry point for the FS-ID Triage Agent interactive CLI.

Allows users to submit service requests interactively in the terminal
with real-time LangGraph routing, rich visual formatting, and live
Data Science benchmark evaluation tracking computed in batches of 3 cases.
"""

import sys
from pathlib import Path
import uuid

# Ensure project root is in sys.path when executed directly as `python src/main.py`
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from rich.prompt import Prompt

from src.core.agent import TriageAgent
from src.catalogue import ServiceCatalogue
from src.cli import (
    console,
    display_welcome_banner,
    display_service_catalogue,
    display_routing_result,
    display_metrics,
    display_session_history,
    display_eval_toggle,
    display_batch_notification,
    display_final_summary,
    display_error,
    display_goodbye,
    get_thinking_status,
    prompt_feedback,
    SessionTracker,
)


def main() -> None:
    """Run the interactive CLI loop."""
    display_welcome_banner()

    # Load catalogue and agent with spinner
    try:
        with console.status("📦 Loading Service Catalogue & Initializing LangGraph Agent...", spinner="dots"):
            catalogue = ServiceCatalogue()
            agent = TriageAgent()
    except Exception as e:
        display_error(f"Failed to initialize FS-ID Agent: {e}")
        sys.exit(1)

    display_service_catalogue(catalogue.templates)
    template_ids = [t["id"] for t in catalogue.templates if "id" in t]

    # Initialize tracker with batch_size=3
    tracker = SessionTracker(batch_size=3)

    while True:
        try:
            query = Prompt.ask("[bold green]FS-ID >[/bold green]").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not query:
            continue

        cmd = query.lower()

        # Handle commands
        if cmd in ("quit", "exit", "q"):
            break

        if cmd == "/eval":
            is_active = tracker.toggle_eval()
            display_eval_toggle(is_active)
            continue

        if cmd == "/metrics":
            metrics = tracker.compute_data_science_metrics()
            display_metrics(metrics, title_prefix="Current Session")
            continue

        if cmd == "/history":
            display_session_history(tracker.get_cases())
            continue

        if cmd == "/report":
            if not tracker.get_evaluated_cases():
                console.print("  [dim]No evaluated cases in session to report.[/dim]\n")
                continue
            report_path = tracker.export_report()
            console.print(f"  📁 [dim]Report saved to:[/dim] [cyan]{report_path}[/cyan]\n")
            continue

        if cmd == "/catalogue":
            display_service_catalogue(catalogue.templates)
            continue

        if cmd in ("/help", "/?"):
            console.print(
                "\n  [bold]Available Commands:[/bold]\n"
                "    [cyan]/eval[/cyan]      - Toggle evaluation tracking on/off (batches of 3)\n"
                "    [cyan]/metrics[/cyan]   - Display current Data Science benchmark metrics\n"
                "    [cyan]/history[/cyan]   - View all queries processed this session\n"
                "    [cyan]/report[/cyan]    - Export session evaluation report to JSON\n"
                "    [cyan]/catalogue[/cyan] - Display the service template catalogue\n"
                "    [cyan]quit[/cyan]       - Exit the application\n"
            )
            continue

        # Process user query
        request_id = f"CLI-{uuid.uuid4().hex[:6].upper()}"
        try:
            with get_thinking_status():
                decision = agent.run(request_id=request_id, channel="cli", raw_text=query)

            if decision is None:
                display_error("The agent could not complete triage for this request. Please check API quota or logs.")
                continue

            display_routing_result(decision)
            case = tracker.record_case(raw_text=query, decision=decision)

            # If evaluation mode is on, solicit feedback
            if tracker.is_eval_active():
                is_correct, exp_tmpl, exp_act, exp_urg, exp_missing = prompt_feedback(template_ids)
                if is_correct is not None:
                    batch_triggered = tracker.record_feedback(
                        case_number=case.case_number,
                        is_correct=is_correct,
                        expected_template=exp_tmpl,
                        expected_action=exp_act,
                        expected_urgency=exp_urg,
                        expected_missing_fields=exp_missing,
                    )

                    # Triggered batch evaluation every 3 evaluated cases
                    if batch_triggered:
                        batch_metrics = tracker.compute_data_science_metrics()
                        batch_report = tracker.export_report(batch_label=f"batch_{tracker.batch_count}")
                        display_batch_notification(tracker.batch_count, tracker.batch_size, batch_report)
                        display_metrics(batch_metrics, title_prefix=f"Batch #{tracker.batch_count}")

        except KeyboardInterrupt:
            console.print("\n  [dim]Operation cancelled by user.[/dim]")
            continue
        except Exception as e:
            display_error(f"Error during triage execution: {e}")

    # Session termination / exit
    if tracker.get_evaluated_cases():
        metrics = tracker.compute_data_science_metrics()
        report_path = tracker.export_report(batch_label="final")
        display_final_summary(metrics, report_path)

    display_goodbye()


if __name__ == "__main__":
    main()
