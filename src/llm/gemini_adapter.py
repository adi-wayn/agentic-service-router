import os
import sys
import time
import logging
import contextlib
from typing import Type, Optional, Callable, Any
from google import genai
from google.genai import types

# Natively suppress the Google GenAI SDK advisory notice regarding Automatic Function Calling
try:
    from google.genai.models import Models
    Models._logged_afc_warning = True
except Exception:
    pass

logging.getLogger("google.genai").setLevel(logging.ERROR)
logging.getLogger("google").setLevel(logging.ERROR)

from src.llm.base import BaseLLMClient, T
from src.config import config

FALLBACK_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-3.5-flash",
]


@contextlib.contextmanager
def silence_stderr():
    """Silence low-level stderr to prevent harmless GenAI SDK notices from polluting the TUI."""
    saved_fd = None
    stderr_fd = None
    try:
        stderr_fd = sys.stderr.fileno()
        saved_fd = os.dup(stderr_fd)
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, stderr_fd)
        os.close(devnull)
    except Exception:
        pass

    try:
        yield
    finally:
        if saved_fd is not None and stderr_fd is not None:
            try:
                os.dup2(saved_fd, stderr_fd)
                os.close(saved_fd)
            except Exception:
                pass


class GeminiLLMAdapter(BaseLLMClient):
    """Google Gemini LLM Adapter with automatic retry, exponential backoff, and model fallback."""

    def __init__(self, model_name: str = "gemini-3.1-flash-lite"):
        api_key = config.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")

        # Initialize the official google-genai client
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def _execute_with_retry(self, fn: Callable[[str], Any], max_retries: int = 3) -> Any:
        """Execute a GenAI call with exponential backoff on transient errors and model fallback on quota exhaustion."""
        models_to_try = [self.model_name] + [m for m in FALLBACK_MODELS if m != self.model_name]
        last_error = None

        for model in models_to_try:
            for attempt in range(max_retries):
                try:
                    with silence_stderr():
                        return fn(model)
                except Exception as e:
                    last_error = e
                    err_str = str(e)
                    # If daily quota limit is exhausted for this specific model, switch immediately to next model
                    if "GenerateRequestsPerDay" in err_str or "quota limit: 500" in err_str:
                        break
                    # Transient rate limit (RPM) or temporary service spike: back off and retry
                    elif "429" in err_str or "503" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        sleep_secs = 2 ** attempt + 1
                        time.sleep(sleep_secs)
                        continue
                    else:
                        raise e

        if last_error:
            raise last_error
        raise RuntimeError("LLM call failed with all available fallback models.")

    def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
    ) -> T:
        """Generate structured JSON output validated against a Pydantic schema."""
        def _call(model: str) -> T:
            gen_config = types.GenerateContentConfig(
                temperature=0.0,
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=schema,
            )
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=gen_config,
            )
            return response.parsed

        return self._execute_with_retry(_call)

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        """Generate plain text output."""
        def _call(model: str) -> str:
            gen_config = types.GenerateContentConfig(
                temperature=0.0,
                system_instruction=system_instruction,
            )
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=gen_config,
            )
            return response.text

        return self._execute_with_retry(_call)
