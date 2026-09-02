import os
from src.llm.base import BaseLLMClient
from src.llm.gemini_adapter import GeminiLLMAdapter
from src.config import config

class LLMClientFactory:
    @staticmethod
    def get_client() -> BaseLLMClient:
        provider = config.LLM_PROVIDER
        
        if provider == "gemini":
            # Using gemini-2.5-flash as default if GEMINI_MODEL not in env
            model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
            return GeminiLLMAdapter(model_name=model_name)
        elif provider == "anthropic":
            raise NotImplementedError("Anthropic adapter is not yet implemented.")
        elif provider == "openai":
            raise NotImplementedError("OpenAI adapter is not yet implemented.")
        else:
            raise ValueError(f"Unsupported LLM_PROVIDER: '{provider}'. Supported: gemini, anthropic, openai.")
