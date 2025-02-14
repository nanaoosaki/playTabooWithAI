"""
Base classes for Taboo game AI agents.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

class TabooAgent(ABC):
    """Abstract base class for Taboo game agents."""
    
    def __init__(self, provider: str = "anthropic"):
        """
        Initialize the agent.
        
        Args:
            provider: The LLM provider to use ("anthropic", "openai", or "local")
        """
        self.provider = provider
        self._last_response: Optional[str] = None
    
    @property
    def last_response(self) -> Optional[str]:
        """Get the last response from the agent."""
        return self._last_response
    
    @abstractmethod
    def reset(self) -> None:
        """Reset the agent's state."""
        self._last_response = None 