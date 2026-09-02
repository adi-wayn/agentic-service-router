import os
from typing import Type, Optional
from google import genai
from google.genai import types

from src.llm.base import BaseLLMClient, T
from src.config import config

class GeminiLLMAdapter(BaseLLMClient):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        api_key = config.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")
        
        # Initialize the official google-genai client
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_structured(
        self, 
        prompt: str, 
        response_schema: Type[T], 
        system_instruction: Optional[str] = None
    ) -> T:
        gen_config = types.GenerateContentConfig(
            temperature=0.0,
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=response_schema
        )
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=gen_config
        )
        return response.parsed

    def generate_text(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None
    ) -> str:
        gen_config = types.GenerateContentConfig(
            temperature=0.0,
            system_instruction=system_instruction
        )
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=gen_config
        )
        return response.text
