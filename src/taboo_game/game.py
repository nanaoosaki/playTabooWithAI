"""
Core game logic for the Taboo game.
"""

import time
from enum import Enum, auto
from typing import Optional, Tuple, List, Dict
from .utils.word_database import WordDatabase
from .agents import DescriberAgent, GuesserAgent

class GameState(Enum):
    """Possible states of the game."""
    INITIALIZED = auto()
    ROUND_STARTING = auto()
    DESCRIBING = auto()
    GUESSING = auto()
    ROUND_ENDED = auto()
    GAME_OVER = auto()

class RoundResult(Enum):
    """Possible results of a round."""
    CORRECT_GUESS = auto()
    INCORRECT_GUESS = auto()
    TABOO_WORD_USED = auto()
    TIME_UP = auto()
    SKIPPED = auto()

class TabooGame:
    """Main game class handling the game loop and state management."""
    
    def __init__(self, 
                 round_time_limit: int = 60,
                 max_rounds: int = 5,
                 min_word_length: int = 4,
                 max_word_length: int = 12,
                 describer_provider: str = "anthropic",
                 guesser_provider: str = "openai"):
        """
        Initialize the game.
        
        Args:
            round_time_limit: Time limit per round in seconds
            max_rounds: Maximum number of rounds to play
            min_word_length: Minimum length of target words
            max_word_length: Maximum length of target words
            describer_provider: LLM provider for the describer agent
            guesser_provider: LLM provider for the guesser agent
        """
        self.round_time_limit = round_time_limit
        self.max_rounds = max_rounds
        self.word_db = WordDatabase(min_word_length, max_word_length)
        
        # Initialize agents
        self.describer = DescriberAgent(provider=describer_provider)
        self.guesser = GuesserAgent(provider=guesser_provider)
        
        # Game state
        self.state = GameState.INITIALIZED
        self.current_round = 0
        self.score = 0
        self.round_start_time: Optional[float] = None
        
        # Current round data
        self.current_word: Optional[str] = None
        self.taboo_words: Optional[List[str]] = None
        self.current_description: Optional[str] = None
        self.previous_guesses: List[str] = []  # Track guesses for progressive hints
        self.current_descriptions: List[str] = []  # Track all descriptions for current word
        
        # Game history
        self.round_history: List[Dict] = []
    
    def start_game(self) -> None:
        """Start a new game."""
        self.current_round = 0
        self.score = 0
        self.state = GameState.ROUND_STARTING
        self.round_history.clear()
        self.previous_guesses.clear()  # Clear previous guesses
        self.describer.reset()
        self.guesser.reset()
    
    def start_round(self, is_skip: bool = False) -> Tuple[str, List[str]]:
        """
        Start a new round.
        
        Args:
            is_skip: If True, get a new word without incrementing round number
        
        Returns:
            Tuple of (target word, list of taboo words)
        
        Raises:
            ValueError if maximum rounds reached
        """
        if not is_skip and self.current_round >= self.max_rounds:
            raise ValueError("Maximum rounds reached")
        
        # Only increment round if not skipping
        if not is_skip:
            self.current_round += 1
        
        # Reset round state
        self.state = GameState.DESCRIBING
        self.round_start_time = time.time()
        self.current_description = None
        self.previous_guesses = []
        self.current_descriptions = []  # Clear descriptions for new word
        
        # Get new word
        self.current_word, self.taboo_words = self.word_db.get_word_with_taboo()
        
        return self.current_word, self.taboo_words
    
    def generate_description(self) -> str:
        """
        Generate a description for the current word using the describer agent.
        
        Returns:
            The generated description
        
        Raises:
            ValueError: If called in wrong game state
        """
        if self.state != GameState.DESCRIBING:
            raise ValueError("Not in describing phase")
        
        if not self.current_word or not self.taboo_words:
            raise ValueError("No current word or taboo words")
        
        self.current_description = self.describer.generate_description(
            self.current_word,
            self.taboo_words
        )
        return self.current_description
    
    def refine_description(self, feedback: str) -> str:
        """
        Refine the current description based on feedback.
        
        Args:
            feedback: Feedback about why the previous description wasn't effective
        
        Returns:
            The refined description
        """
        if not self.current_word or not self.taboo_words:
            raise ValueError("No current word or taboo words")
        
        # Ensure we're still in describing state
        self.state = GameState.DESCRIBING
        
        self.current_description = self.describer.refine_description(feedback)
        return self.current_description
    
    def _are_words_matching(self, guess: str, target: str) -> bool:
        """
        Check if two words match, considering plural forms.
        
        Args:
            guess: The guessed word
            target: The target word
        
        Returns:
            True if the words match (including plural forms)
        """
        guess = guess.lower()
        target = target.lower()
        
        # Direct match
        if guess == target:
            return True
            
        # Check plural forms
        if guess.endswith('s') and guess[:-1] == target:  # guess is plural, target is singular
            return True
        if target.endswith('s') and target[:-1] == guess:  # target is plural, guess is singular
            return True
            
        # Handle special cases (e.g., 'y' to 'ies')
        if target.endswith('y') and guess == target[:-1] + 'ies':
            return True
        if guess.endswith('y') and target == guess[:-1] + 'ies':
            return True
            
        return False

    def make_guess(self) -> Tuple[str, RoundResult]:
        """
        Make a guess using the guesser agent.
        
        Returns:
            Tuple of (guessed_word, result)
        
        Raises:
            ValueError: If called in wrong game state or no description available
        """
        if self.state != GameState.DESCRIBING:
            raise ValueError("Not in describing phase")
        
        if not self.current_description:
            raise ValueError("No description available")
        
        # Check if time is up
        if self.check_time_remaining() <= 0:
            self.state = GameState.ROUND_ENDED
            return "", RoundResult.TIME_UP
        
        # Add current description to the list
        self.current_descriptions.append(self.current_description)
        self.guesser.add_description(self.current_description)
        
        # Get guess from agent
        guess = self.guesser.make_guess(self.current_description)
        
        # Process the guess
        if self._are_words_matching(guess, self.current_word):
            self.score += 1
            self.state = GameState.ROUND_ENDED
            result = RoundResult.CORRECT_GUESS
        else:
            result = RoundResult.INCORRECT_GUESS
        
        # Record the result
        if result in [RoundResult.CORRECT_GUESS, RoundResult.TIME_UP]:
            self.guesser.record_result("\n".join(self.current_descriptions), self.current_word)
            self._record_round(guess, result)
        
        return guess, result
    
    def check_description(self, description: str) -> bool:
        """
        Check if a description contains any taboo words.
        
        Args:
            description: The description to check
        
        Returns:
            True if the description is valid (no taboo words used)
        """
        if self.taboo_words is None:
            raise ValueError("No taboo words set")
        
        # Convert everything to lowercase for comparison
        description_lower = description.lower()
        
        # Check if any taboo word appears in the description
        for taboo in self.taboo_words:
            if taboo.lower() in description_lower:
                # Don't change state here, let the caller decide what to do
                return False
        
        return True
    
    def check_time_remaining(self) -> float:
        """
        Check how much time is remaining in the current round.
        
        Returns:
            Seconds remaining in the round
        """
        if self.round_start_time is None:
            raise ValueError("Round hasn't started")
        
        elapsed = time.time() - self.round_start_time
        remaining = self.round_time_limit - elapsed
        
        if remaining <= 0:
            self.state = GameState.ROUND_ENDED
            return 0
        
        return remaining
    
    def skip_round(self) -> None:
        """Skip the current round."""
        if self.current_word and self.current_description:
            self._record_round("", RoundResult.SKIPPED)
        self.state = GameState.ROUND_ENDED
    
    def _record_round(self, guess: str, result: RoundResult) -> None:
        """Record the result of a round."""
        if not self.current_word or not self.taboo_words:
            return
        
        round_data = {
            'round': self.current_round,
            'target_word': self.current_word,
            'taboo_words': self.taboo_words.copy(),
            'description': self.current_description,
            'guess': guess,
            'result': result,
            'time_taken': time.time() - (self.round_start_time or time.time())
        }
        self.round_history.append(round_data)

def test_game():
    """Simple test function for the TabooGame class."""
    game = TabooGame(round_time_limit=60)
    game.start_game()
    
    print("Starting new game...")
    word, taboo = game.start_round()
    print(f"Round {game.current_round}")
    print(f"Target word: {word}")
    print("Taboo words:")
    for t in taboo:
        print(f"- {t}")
    
    # Generate description
    description = game.generate_description()
    print(f"\nDescription: {description}")
    
    # Check if description is valid
    is_valid = game.check_description(description)
    print(f"Description valid: {is_valid}")
    
    if is_valid:
        # Make guess
        guess, result = game.make_guess()
        print(f"\nGuess: {guess}")
        print(f"Result: {result}")
    
    print(f"\nTime remaining: {game.check_time_remaining():.1f} seconds")
    print(f"Score: {game.score}")

if __name__ == "__main__":
    test_game() 