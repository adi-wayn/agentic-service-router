from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class BaseLLMClient(ABC):
    @abstractmethod
    def generate_structured(
        self, 
        prompt: str, 
        response_schema: Type[T], 
        system_instruction: Optional[str] = None
    ) -> T:
        """Generates a structured Pydantic model response."""
        pass

    @abstractmethod
    def generate_text(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None
    ) -> str:
        """Generates a raw string text response."""
        pass
