"""
CLI package for the FS-ID Triage Agent.
Contains the interactive Rich terminal interface and live session evaluation tracker.
"""

from src.cli.cli import (
    console,
    display_welcome_banner,
    display_service_catalogue,
    display_routing_result,
    display_clarification_questions,
    display_metrics,
    display_batch_notification,
    display_session_history,
    display_eval_toggle,
    prompt_feedback,
    display_final_summary,
    display_error,
    display_goodbye,
    get_thinking_status,
)
from src.cli.session_tracker import SessionTracker, SessionCase

__all__ = [
    "console",
    "display_welcome_banner",
    "display_service_catalogue",
    "display_routing_result",
    "display_clarification_questions",
    "display_metrics",
    "display_batch_notification",
    "display_session_history",
    "display_eval_toggle",
    "prompt_feedback",
    "display_final_summary",
    "display_error",
    "display_goodbye",
    "get_thinking_status",
    "SessionTracker",
    "SessionCase",
]
