"""
Rich TUI rendering module for the FS-ID Triage Agent.

Provides all display functions for the interactive CLI, including
welcome banners, service catalogue tables, routing result panels,
live Data Science evaluation metrics dashboards matching `eval.metrics`,
batch notifications, and feedback collection prompts.
"""

from typing import Any, List, Optional, Tuple

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
import rich.box


from src.config import config

console = Console()


# ---------------------------------------------------------------------------
# Welcome & Goodbye
# ---------------------------------------------------------------------------

def display_welcome_banner() -> None:
    """Display the FS-ID welcome banner with project metadata."""
    active_provider = config.LLM_PROVIDER.upper() if config.LLM_PROVIDER else "GEMINI"
    banner = Text()
    banner.append("\n  ⚡ ", style="bright_yellow")
    banner.append("FS-ID Triage Agent\n", style="bold bright_white")
    banner.append("  Field Services Intelligent Dispatcher\n\n", style="bright_cyan")
    banner.append("  Architecture: ", style="dim")
    banner.append("LangGraph 6-Node State Machine\n", style="bold magenta")
    banner.append("  LLM Engine:   ", style="dim")
    banner.append(f"{active_provider} ", style="bold green")
    banner.append("(Multi-Provider Support: Gemini / Anthropic / OpenAI)\n", style="dim")
    banner.append("  Pipeline:     Real-Time Triage • Dynamic Evaluation Tracking\n", style="dim")

    console.print(Panel(
        banner,
        border_style="bright_blue",
        padding=(0, 2),
    ))
    console.print("  [dim]Type a service request to begin, or use a command:[/dim]")
    console.print("  [dim]/eval · /metrics · /history · /report · /catalogue · quit[/dim]\n")


def display_goodbye() -> None:
    """Display a clean exit message."""
    console.print("\n  👋 [dim]Goodbye! Session ended.[/dim]\n")


# ---------------------------------------------------------------------------
# Service Catalogue
# ---------------------------------------------------------------------------

URGENCY_STYLES = {"P1": "bold red", "P2": "yellow", "P3": "green"}


def display_service_catalogue(templates: list[dict]) -> None:
    """Render the service catalogue as a rich table.

    Args:
        templates: List of template dicts from ServiceCatalogue().templates.
    """
    table = Table(
        title="📋 Available Service Templates",
        show_header=True,
        header_style="bold bright_cyan",
        border_style="dim",
        title_style="bold",
        box=rich.box.ROUNDED,
    )
    table.add_column("Template ID", style="bold")
    table.add_column("Name")
    table.add_column("Category", style="cyan")
    table.add_column("Tier", justify="center")

    for t in templates:
        tier = t.get("urgency_tier", "?")
        tier_style = URGENCY_STYLES.get(tier, "")
        table.add_row(
            t.get("id", ""),
            t.get("name", ""),
            t.get("category", ""),
            Text(tier, style=tier_style),
        )

    console.print(table)
    console.print()


# ---------------------------------------------------------------------------
# Routing Result
# ---------------------------------------------------------------------------

ACTION_STYLES = {
    "CONFIDENT_RECOMMENDATION": ("✅ CONFIDENT_RECOMMENDATION", "bold green"),
    "NEEDS_CLARIFICATION": ("🟡 NEEDS_CLARIFICATION", "bold yellow"),
    "ROUTE_TO_HUMAN": ("🔴 ROUTE_TO_HUMAN", "bold red"),
}


def _confidence_bar(score: float, width: int = 20) -> Text:
    """Build a visual confidence bar."""
    filled = int(round(score * width))
    bar = Text()
    bar.append("█" * filled, style="bright_green")
    bar.append("░" * (width - filled), style="dim")
    bar.append(f"  {score:.2f}", style="bold")
    return bar


def display_routing_result(decision: Any) -> None:
    """Render the full ServiceRouterDecision with rich formatting.

    Args:
        decision: A ServiceRouterDecision from the triage agent.
    """
    if decision is None:
        display_error("No decision was returned from the agent.")
        return

    lines = Text()

    # --- Template & Action ---
    template_id = "None / Out of Catalogue"
    if decision.match_result and decision.match_result.top_template_id:
        template_id = decision.match_result.top_template_id

    # Resolve final routing action (check routing_result first, fallback to initial_routing_action)
    action_raw = None
    if decision.routing_result and getattr(decision.routing_result, "routing_action", None):
        action_raw = decision.routing_result.routing_action
    elif getattr(decision, "initial_routing_action", None):
        action_raw = decision.initial_routing_action
    action_raw = action_raw or "UNKNOWN"
    action_label, action_style = ACTION_STYLES.get(
        action_raw, (action_raw, "bold")
    )

    cs = getattr(decision, "clarification_state", None)
    loop_count = getattr(cs, "loop_count", 0) if cs else 0

    confidence = 0.0
    if decision.routing_result:
        confidence = decision.routing_result.confidence_score or 0.0

    urgency = "—"
    if decision.extracted_entities:
        urgency = decision.extracted_entities.assessed_real_urgency or "—"
    urg_style = URGENCY_STYLES.get(urgency, "")

    lines.append("  Template:   ", style="dim")
    lines.append(f"{template_id}\n", style="bold bright_white")
    lines.append("  Action:     ", style="dim")
    if loop_count > 0:
        lines.append(f"{action_label} ", style=action_style)
        resolution_style = "bold green" if action_raw == "CONFIDENT_RECOMMENDATION" else "dim italic"
        lines.append(f"(Resolved via Clarification Loop • {loop_count} turn{'s' if loop_count > 1 else ''})\n", style=resolution_style)
    else:
        lines.append(f"{action_label}\n", style=action_style)
    lines.append("  Confidence: ", style="dim")
    lines.append_text(_confidence_bar(confidence))
    lines.append("\n")
    lines.append("  Urgency:    ", style="dim")
    lines.append(f"{urgency}\n", style=urg_style)

    # --- Extracted Entities ---
    ee = decision.extracted_entities
    if ee:
        lines.append("\n  ─── Extracted Entities ───\n", style="bold dim")
        lines.append("  Trade: ", style="dim")
        lines.append(f"{ee.primary_trade}", style="cyan")
        if ee.secondary_trade:
            lines.append(f" + {ee.secondary_trade}", style="cyan")
        lines.append("\n")

        safety = ee.safety_assessment
        if safety and safety.has_immediate_hazard:
            lines.append("  Safety: ", style="dim")
            lines.append("⚠️  Hazard Detected", style="bold red")
            if safety.is_life_safety_affected:
                lines.append(" (life-safety)", style="bold red")
            lines.append("\n")

        lines.append("  Stated Urgency: ", style="dim")
        lines.append(f"{ee.stated_urgency}", style="yellow")
        lines.append(" → Real: ", style="dim")
        lines.append(f"{ee.assessed_real_urgency}\n", style=URGENCY_STYLES.get(ee.assessed_real_urgency, ""))

        lines.append("  Symptom: ", style="dim")
        lines.append(f"{escape(ee.symptom_description)}\n")

    # --- Clarification History (if loop was executed) ---
    if cs and cs.clarification_history:
        lines.append("\n  ─── Clarification History ───\n", style="bold dim")
        for idx, qa in enumerate(cs.clarification_history, 1):
            q_text = qa.get("question", "")
            a_text = qa.get("answer", "")
            lines.append(f"  Turn {idx}:\n", style="bold yellow")
            lines.append("    ❓ Question: ", style="dim")
            lines.append(f"{escape(q_text)}\n", style="yellow")
            lines.append("    💬 Ingested Answer: ", style="dim")
            lines.append(f"{escape(a_text)}\n", style="cyan")

    # --- Rationale ---
    fs = decision.finalizer_synthesis
    if fs:
        lines.append("\n  ─── Rationale ───\n", style="bold dim")
        lines.append(f"  {escape(fs.decision_rationale)}\n")

        lines.append("\n  ─── Counterfactual ───\n", style="bold dim")
        lines.append(f"  {escape(fs.what_would_change_this_call)}\n")

    # --- Audit Trace ---
    trace = getattr(decision, "audit_trace", None) or []
    if trace:
        lines.append("\n  ─── Audit Trace ───\n", style="bold dim")
        for i, step in enumerate(trace, 1):
            lines.append(f"  {i}. {escape(step)}\n", style="dim")

    console.print(Panel(
        lines,
        title="🎯 Triage Decision",
        border_style="bright_blue",
        padding=(0, 1),
    ))


# ---------------------------------------------------------------------------
# Clarification Questions
# ---------------------------------------------------------------------------

def display_clarification_questions(questions: list) -> None:
    """Render clarification questions in a styled panel.

    Args:
        questions: List of ClarificationQuestion objects.
    """
    if not questions:
        return

    lines = Text()
    for i, q in enumerate(questions, 1):
        target = getattr(q, "target_field", "?")
        text = getattr(q, "question_text", "?")
        why = getattr(q, "why_critical", "")
        lines.append(f"  {i}. ", style="bold yellow")
        lines.append(f"[{escape(target)}] ", style="dim")
        lines.append(f"{escape(text)}\n")
        if why:
            lines.append(f"     Why: {escape(why)}\n", style="dim italic")

    console.print(Panel(
        lines,
        title="❓ Clarification Required",
        border_style="yellow",
        padding=(0, 1),
    ))


# ---------------------------------------------------------------------------
# Data Science Evaluation Metrics Dashboard (Parity with run_evaluation.py)
# ---------------------------------------------------------------------------

def display_metrics(metrics: dict, title_prefix: str = "Live Session") -> None:
    """Render the Data Science benchmark evaluation report.

    Mirrors the exact metrics and layout computed in `eval.run_evaluation.py`:
    1. Action Routing Performance (Macro/Weighted F1, Per-class Precision & Recall)
    2. Safety Critical Metrics (P1 Recall, P1 FNR, Cost Penalty)
    3. Template & Gap Extraction (Template Accuracy, Mean Jaccard IoU)
    4. Confidence Calibration (Brier Score, ECE)
    5. Clarification Quality (Specificity, Redundancy)

    Args:
        metrics: Dict returned by SessionTracker.compute_data_science_metrics().
        title_prefix: Label indicating whether this is a Batch or Session report.
    """
    if not metrics or not metrics.get("evaluated_cases"):
        console.print(Panel("  [dim]No evaluated cases with feedback recorded yet.[/dim]", title=f"📊 {title_prefix} Metrics", border_style="bright_cyan"))
        return

    total = metrics.get("total_cases", 0)
    evaluated = metrics.get("evaluated_cases", 0)
    correct = metrics.get("correct_cases", 0)
    accuracy = metrics.get("accuracy", 0.0)

    # 1. Action Routing Performance
    conf = metrics.get("confusion_matrix", {})
    macro_f1 = conf.get("macro_f1", 0.0)
    weighted_f1 = conf.get("weighted_f1", 0.0)

    f1_status = "✅ PASS" if macro_f1 >= 0.850 else "⚠️ BELOW TARGET"

    action_table = Table(
        title="1. Action Routing Performance",
        show_header=True,
        header_style="bold bright_cyan",
        border_style="dim",
        box=rich.box.ROUNDED,
    )
    action_table.add_column("Action Category", style="bold")
    action_table.add_column("Precision", justify="center")
    action_table.add_column("Recall", justify="center")
    action_table.add_column("F1-Score", justify="center")

    for cat in ["CONFIDENT_RECOMMENDATION", "NEEDS_CLARIFICATION", "ROUTE_TO_HUMAN"]:
        cat_data = conf.get(cat, {"precision": 0.0, "recall": 0.0, "f1": 0.0})
        _, cat_style = ACTION_STYLES.get(cat, (cat, ""))
        action_table.add_row(
            Text(cat, style=cat_style),
            f"{cat_data.get('precision', 0.0):.3f}",
            f"{cat_data.get('recall', 0.0):.3f}",
            f"{cat_data.get('f1', 0.0):.3f}",
        )

    # 2. Safety Metrics
    safety = metrics.get("safety_metrics", {})
    p1_rec = safety.get("p1_recall", 1.0)
    p1_fnr = safety.get("p1_fnr", 0.0)
    cost = safety.get("cost_safety", 0)
    safety_status = "✅ PASS" if p1_rec >= 1.0 else "❌ FAILED"

    # 3. Template & Gap
    temp_acc = metrics.get("template_accuracy", 0.0)
    jaccard = metrics.get("mean_jaccard_iou", 0.0)
    temp_status = "✅ PASS" if temp_acc >= 0.90 else "⚠️ BELOW TARGET"

    # 4. Calibration
    calib = metrics.get("calibration", {})
    brier = calib.get("brier_score", 0.0)
    ece = calib.get("ece", 0.0)

    # 5. Clarification
    clarif = metrics.get("clarification", {})
    spec = clarif.get("question_specificity", 0.0)
    redun = clarif.get("redundancy_index", 0.0)
    cr = clarif.get("loop_convergence_rate", 0.0)

    # Summary Panel
    summary_text = Text()
    summary_text.append(f"  Evaluated Cases: {evaluated} of {total} total\n", style="bold")
    summary_text.append(f"  Raw Accuracy:    {correct}/{evaluated} ({accuracy:.1%})\n\n", style="bold bright_white")

    summary_text.append("  [Primary KPIs & Targets]\n", style="bold underline")
    summary_text.append(f"  • Macro-Averaged F1:    {macro_f1:.3f}  (Target: >= 0.850) -> {f1_status}\n", style="cyan")
    summary_text.append(f"  • Weighted F1:          {weighted_f1:.3f}\n", style="dim")
    summary_text.append(f"  • P1 Safety Recall:     {p1_rec*100:.1f}%  (Target: 100.0%) -> {safety_status}\n", style="red")
    summary_text.append(f"  • P1 False Neg Rate:    {p1_fnr*100:.1f}%\n", style="dim")
    summary_text.append(f"  • Safety Cost Penalty:  {cost}\n", style="dim")
    summary_text.append(f"  • Template Accuracy:    {temp_acc*100:.1f}%  (Target: >= 90.0%) -> {temp_status}\n", style="yellow")
    summary_text.append(f"  • Mean Jaccard IoU:     {jaccard:.3f}  (Gap extraction overlap)\n", style="yellow")
    summary_text.append(f"  • Brier Calibration:    {brier:.3f}  (Target: <= 0.100)\n", style="dim")
    summary_text.append(f"  • Expected Calib Error: {ece:.3f}  (Target: <= 0.100)\n", style="dim")
    summary_text.append(f"  • Clarif. Specificity:  {spec:.3f}  | Redundancy: {redun:.3f} | CR: {cr:.1%}\n", style="dim")

    console.print(Panel(
        summary_text,
        title=f"📊 {title_prefix} Benchmark Evaluation Report",
        border_style="bright_cyan",
        padding=(0, 1),
    ))

    console.print(action_table)
    console.print()


def display_batch_notification(batch_number: int, batch_size: int, report_path: str) -> None:
    """Display a banner when a batch evaluation completes.

    Args:
        batch_number: Index of the completed batch.
        batch_size: Configured batch size.
        report_path: Path where batch JSON was exported.
    """
    msg = (
        f"🔔 [bold green]Batch #{batch_number} Completed ({batch_size} cases evaluated)[/bold green]\n"
        f"[dim]Data Science matrices updated and exported to: {escape(report_path)}[/dim]"
    )
    console.print(Panel(msg, border_style="green", padding=(0, 1)))


# ---------------------------------------------------------------------------
# Session History
# ---------------------------------------------------------------------------

def display_session_history(cases: list) -> None:
    """Render all session cases as a summary table.

    Args:
        cases: List of SessionCase objects from session_tracker.
    """
    if not cases:
        console.print("  [dim]No cases recorded yet.[/dim]\n")
        return

    t = Table(title="📜 Session History", show_header=True, header_style="bold", border_style="dim", box=rich.box.ROUNDED)
    t.add_column("#", justify="right", style="bold")
    t.add_column("Query", max_width=50)
    t.add_column("Template")
    t.add_column("Action")
    t.add_column("Conf.", justify="center")
    t.add_column("Correct?", justify="center")

    for c in cases:
        query_short = c.raw_text[:50] + ("…" if len(c.raw_text) > 50 else "")
        _, action_style = ACTION_STYLES.get(c.predicted_action, (c.predicted_action, ""))

        if c.is_correct is True:
            correct_str = Text("✅", style="green")
        elif c.is_correct is False:
            correct_str = Text("❌", style="red")
        else:
            correct_str = Text("⏭️", style="dim")

        t.add_row(
            str(c.case_number),
            escape(query_short),
            c.predicted_template or "—",
            Text(c.predicted_action, style=action_style),
            f"{c.confidence:.2f}",
            correct_str,
        )

    console.print(t)
    console.print()


# ---------------------------------------------------------------------------
# Eval Toggle & Feedback
# ---------------------------------------------------------------------------

def display_eval_toggle(is_active: bool) -> None:
    """Display a message indicating eval mode was toggled.

    Args:
        is_active: The new evaluation mode state.
    """
    if is_active:
        console.print(Panel(
            "  Evaluation mode: [bold green]ON[/bold green]\n"
            "  [dim]Batches of 3 cases will automatically trigger Data Science benchmark matrices.[/dim]",
            border_style="green", padding=(0, 1),
        ))
    else:
        console.print(Panel(
            "  Evaluation mode: [dim]OFF[/dim]",
            border_style="dim", padding=(0, 1),
        ))


def prompt_feedback(
    template_ids: list[str]
) -> Tuple[Optional[bool], Optional[str], Optional[str], Optional[str], Optional[List[str]]]:
    """Interactive feedback collection after a routing result.

    Gathers ground truth dynamically for the Data Science matrices:
    - Template match correctness
    - Action correctness
    - Urgency tier correctness
    - Missing fields correctness

    Args:
        template_ids: List of valid template IDs for correction selection.

    Returns:
        Tuple of (is_correct, expected_template, expected_action, expected_urgency, expected_missing_fields).
    """
    answer = Prompt.ask(
        "  Was this routing correct?",
        choices=["y", "n", "skip"],
        default="y",
        case_sensitive=False,
    ).lower()

    if answer == "skip":
        return None, None, None, None, None

    if answer in ("y", "yes"):
        return True, None, None, None, None

    # User reported error: collect ground truth corrections
    console.print("\n  [bold]Ground Truth Corrections:[/bold]")
    console.print("  Available Templates:")
    for i, tid in enumerate(template_ids, 1):
        console.print(f"    {i}. {tid}")

    tmpl_choice = Prompt.ask("  Select correct template (enter number or leave blank to keep predicted)", default="")
    expected_template = None
    if tmpl_choice.isdigit():
        idx = int(tmpl_choice) - 1
        if 0 <= idx < len(template_ids):
            expected_template = template_ids[idx]

    expected_action_short = Prompt.ask(
        "  Expected routing action?",
        choices=["CONFIDENT", "CLARIFY", "HUMAN", "CONFIDENT_RECOMMENDATION", "NEEDS_CLARIFICATION", "ROUTE_TO_HUMAN"],
        default="CONFIDENT",
        case_sensitive=False,
    ).upper()
    action_map = {
        "CONFIDENT": "CONFIDENT_RECOMMENDATION",
        "CLARIFY": "NEEDS_CLARIFICATION",
        "HUMAN": "ROUTE_TO_HUMAN",
    }
    expected_action = action_map.get(expected_action_short, expected_action_short)

    expected_urgency = Prompt.ask(
        "  Expected real urgency tier?",
        choices=["P1", "P2", "P3"],
        default="P1",
        case_sensitive=False,
    ).upper()

    missing_input = Prompt.ask("  Expected missing fields? (comma-separated, or Enter for none)", default="").strip()
    expected_missing = [f.strip() for f in missing_input.split(",") if f.strip()] if missing_input else []

    console.print("  ✏️  [dim]Feedback and ground truth logged for batch evaluation.[/dim]\n")
    return False, expected_template, expected_action, expected_urgency, expected_missing


# ---------------------------------------------------------------------------
# Final Summary & Utilities
# ---------------------------------------------------------------------------

def display_final_summary(metrics: dict, report_path: str) -> None:
    """Display the final session summary on exit.

    Args:
        metrics: The Data Science metrics dict.
        report_path: Path where the final report was saved.
    """
    display_metrics(metrics, title_prefix="Final Session")
    console.print(f"  📁 [dim]Complete session report saved to:[/dim] [cyan]{escape(report_path)}[/cyan]\n")


def display_error(message: str) -> None:
    """Display an error message in a red panel.

    Args:
        message: The error message to display.
    """
    console.print(Panel(
        f"  {escape(message)}",
        title="❌ Error",
        border_style="red",
        padding=(0, 1),
    ))


def get_thinking_status():
    """Return a rich Status context manager for the processing spinner.

    Returns:
        A rich.status.Status context manager.
    """
    return console.status("⚙️  Processing through 6-node pipeline...", spinner="dots")
