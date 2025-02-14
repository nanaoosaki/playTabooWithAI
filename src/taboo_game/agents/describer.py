"""
Describer agent for the Taboo game.
"""

from typing import List, Optional
from .base import TabooAgent
from ..utils.llm_api import query_llm

class DescriberAgent(TabooAgent):
    """AI agent that generates descriptions for target words while avoiding taboo words."""
    
    def __init__(self, provider: str = "anthropic"):
        """
        Initialize the describer agent.
        
        Args:
            provider: The LLM provider to use (defaults to anthropic for better constraint following)
        """
        super().__init__(provider)
        self._current_word: Optional[str] = None
        self._current_taboo_words: Optional[List[str]] = None
    
    def reset(self) -> None:
        """Reset the agent's state."""
        super().reset()
        self._current_word = None
        self._current_taboo_words = None
    
    def generate_description(self, target_word: str, taboo_words: List[str]) -> str:
        """
        Generate a description for the target word without using any taboo words.
        
        Args:
            target_word: The word to describe
            taboo_words: List of words that cannot be used in the description
        
        Returns:
            A description of the target word
        """
        self._current_word = target_word
        self._current_taboo_words = taboo_words
        
        prompt = f"""You are playing Taboo, trying to help someone guess the word '{target_word}'. Be creative and engaging!
        
Rules:
1. MOST IMPORTANT: You MUST NOT use:
   - The target word '{target_word}' itself
   - Any part or variation of the target word
   - Any of these taboo words (or their variations): {', '.join(taboo_words)}

2. Start with basic information:
   - What type of word is it? (noun/verb/adjective/etc.)
   - What general category does it belong to? (object/action/feeling/person/etc.)
   - Is it concrete or abstract?

3. Then use a creative approach:
   - Common scenarios or everyday situations
   - Relatable "fill in the blank" sentences
   - Popular expressions or sayings
   - Examples of when people use this word

4. Structure your description:
   - First line: Type and category of word
   - Second/third lines: Creative description or scenario
   - Keep it engaging and conversational

Remember: 
- Your first description should be clear but leave room for more specific hints later
- People often guess words better from context and usage than from dictionary-style definitions
- Double-check your description to ensure you haven't accidentally used the target word or its variations

Respond with ONLY the description, no additional text."""
        
        self._last_response = query_llm(prompt, provider=self.provider)
        return self._last_response
    
    def refine_description(self, feedback: str) -> str:
        """
        Generate a refined description based on feedback.
        
        Args:
            feedback: Feedback about why the previous description wasn't effective
        
        Returns:
            A new description addressing the feedback
        """
        if not self._current_word or not self._current_taboo_words:
            raise ValueError("No current word or taboo words set")
        
        prompt = f"""You are playing Taboo and helping a human player guess a word. Here's the situation:

Previous guesses: {feedback}

Your goal is to help them get closer to guessing: [word hidden for fairness]
DO NOT use these taboo words: {', '.join(self._current_taboo_words)}

Guidelines for your next hint:
1. Analyze their previous guesses:
   - If they're in the right category but wrong word: Focus on distinguishing features
   - If they're in wrong category: Try a completely different approach
   - If no guesses yet: Start with a general, engaging description

2. Try one of these approaches:
   - Create a "fill in the blank" sentence
   - Describe a relatable scenario
   - Use a popular expression or saying
   - Give an example of when people use this word
   - Make a clever analogy

3. Make your hint:
   - Build upon previous information
   - Add new perspectives not covered before
   - Stay conversational and engaging
   - Acknowledge if they're getting closer
   - Guide them gently in the right direction

4. IMPORTANT:
   - NEVER use the target word or any variation of it
   - Keep it natural and friendly
   - Make each hint add value

Respond with ONLY your new hint, no additional text."""
        
        self._last_response = query_llm(prompt, provider=self.provider)
        return self._last_response 