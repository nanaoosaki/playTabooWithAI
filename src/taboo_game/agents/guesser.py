"""
Guesser agent for the Taboo game.
"""

from typing import List, Optional, Dict
from .base import TabooAgent
from ..utils.llm_api import query_llm

class GuesserAgent(TabooAgent):
    """AI agent that makes intelligent guesses based on descriptions."""
    
    def __init__(self, provider: str = "openai"):
        """
        Initialize the guesser agent.
        
        Args:
            provider: The LLM provider to use (defaults to openai for better reasoning)
        """
        super().__init__(provider)
        self._round_history: List[Dict[str, str]] = []
    
    def reset(self) -> None:
        """Reset the agent's state."""
        super().reset()
        self._round_history.clear()
        self._current_descriptions = []
    
    def make_guess(self, description: str) -> str:
        """
        Make a guess based on the provided description.
        
        Args:
            description: The latest description of the target word
        
        Returns:
            The guessed word
        """
        # Include context from previous rounds if available
        context = ""
        if self._round_history:
            context = "\nPrevious successful rounds for reference:"
            for round_data in self._round_history[-3:]:  # Use last 3 rounds for context
                context += f"\nDescription: {round_data['description']}\nCorrect word: {round_data['word']}"
        
        # Get the number of attempts for this word
        attempt_number = len(self._current_descriptions) if hasattr(self, '_current_descriptions') else 0
        
        prompt = f"""You are playing Taboo as the guesser. A human player is trying to help you guess a word through descriptions.

LATEST DESCRIPTION (Attempt #{attempt_number + 1}):
"{description}"

{f'''PREVIOUS ATTEMPTS FOR THIS WORD:
{self._get_previous_descriptions_text()}

What's new in this attempt:
- Compare this new description with previous ones
- Look for new clues or perspectives added
- Consider how this description clarifies previous ambiguities''' if attempt_number > 0 else ''}

Your task:
1. First, focus on the latest description:
   - What new information or perspective is provided?
   - What specific clues or examples are given?
   - What word type and category is being described?

2. {'''Combine insights from all descriptions:
   - How do the descriptions complement each other?
   - What patterns emerge across multiple attempts?
   - Which characteristics are consistently emphasized?''' if attempt_number > 0 else '''Analyze the description carefully:
   - What are the key characteristics mentioned?
   - What domain or context is suggested?
   - What common words fit this description?'''}

3. Make your best guess:
   - Must be a single word (no spaces/hyphens)
   - Should match ALL provided descriptions
   - Consider both literal and contextual meanings

4. After deciding:
   - Explain why this guess fits all clues
   - Note which aspects were most helpful
   - Suggest what additional information would help if unsure

Format your response as:
GUESS: (your single word guess in lowercase)
REASONING: (2-3 sentences explaining your thought process)
FEEDBACK: (1-2 sentences suggesting what would help clarify){context}"""
        
        response = query_llm(prompt, provider=self.provider).strip().lower()
        
        # Parse the response
        lines = response.split('\n')
        guess = ""
        reasoning = ""
        feedback = ""
        
        for line in lines:
            if line.startswith('guess:'):
                guess = line.replace('guess:', '').strip()
            elif line.startswith('reasoning:'):
                reasoning = line.replace('reasoning:', '').strip()
            elif line.startswith('feedback:'):
                feedback = line.replace('feedback:', '').strip()
        
        # Store the analysis for context
        self._last_analysis = {
            'guess': guess,
            'reasoning': reasoning,
            'feedback': feedback
        }
        
        return guess
    
    def _get_previous_descriptions_text(self) -> str:
        """Get formatted text of previous descriptions for the current word."""
        if not hasattr(self, '_current_descriptions'):
            self._current_descriptions = []
        
        if not self._current_descriptions:
            return "No previous descriptions."
        
        text = ""
        for i, desc in enumerate(self._current_descriptions, 1):
            text += f"Description #{i}: \"{desc}\"\n"
        return text
    
    def add_description(self, description: str):
        """Add a description for the current word."""
        if not hasattr(self, '_current_descriptions'):
            self._current_descriptions = []
        self._current_descriptions.append(description)
    
    @property
    def last_analysis(self) -> dict:
        """Get the reasoning and feedback from the last guess."""
        return getattr(self, '_last_analysis', None)
    
    def record_result(self, description: str, correct_word: str) -> None:
        """
        Record the result of a round for future context.
        
        Args:
            description: The description that was given
            correct_word: The word that was being described
        """
        self._round_history.append({
            'description': description,
            'word': correct_word,
            'analysis': self._last_analysis if hasattr(self, '_last_analysis') else None
        }) 