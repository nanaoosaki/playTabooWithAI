"""
Test suite for AI vs AI mode in the Taboo game.
"""

import unittest
from src.taboo_game.cli import TabooGameCLI
from src.taboo_game.game import GameState, RoundResult

class TestAIvsAIMode(unittest.TestCase):
    """Test cases for AI vs AI gameplay."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.game = TabooGameCLI(
            mode="ai_only",
            round_time_limit=60,
            max_rounds=1,
            describer_provider="anthropic",  # Claude is better at following constraints
            guesser_provider="openai"        # GPT-4 is better at semantic understanding
        )
    
    def test_initialization(self):
        """Test game initialization."""
        self.assertEqual(self.game.mode, "ai_only")
        self.assertEqual(self.game.game.round_time_limit, 60)
        self.assertEqual(self.game.game.max_rounds, 1)
        self.assertEqual(self.game.game.state, GameState.INITIALIZED)
    
    def test_state_transitions(self):
        """Test game state transitions during AI vs AI play."""
        # Start game
        self.game.game.start_game()
        self.assertEqual(self.game.game.state, GameState.ROUND_STARTING)
        
        # Start round
        word, taboo = self.game.game.start_round()
        self.assertEqual(self.game.game.state, GameState.DESCRIBING)
        self.assertIsNotNone(word)
        self.assertIsNotNone(taboo)
        
        # Generate description
        description = self.game.game.generate_description()
        self.assertIsNotNone(description)
        self.assertTrue(self.game.game.check_description(description))
        
        # Make guess
        guess, result = self.game.game.make_guess()
        self.assertIsNotNone(guess)
        self.assertIn(result, [RoundResult.CORRECT_GUESS, RoundResult.INCORRECT_GUESS])

def run_ai_vs_ai_test():
    """Run an interactive AI vs AI game test."""
    print("\n" + "="*50)
    print("STARTING TABOO GAME - AI VS AI MODE")
    print("="*50)
    
    game = TabooGameCLI(
        mode="ai_only",
        round_time_limit=60,
        max_rounds=3,  # Testing 3 rounds to see patterns
        describer_provider="anthropic",
        guesser_provider="openai"
    )
    
    print("\nGame Configuration:")
    print("- Describer: Claude (Anthropic)")
    print("- Guesser: GPT-4 (OpenAI)")
    print("- Rounds: 3")
    print("- Time limit: 60 seconds per round\n")
    
    game.play_game()

if __name__ == '__main__':
    # For quick testing, run the interactive test
    run_ai_vs_ai_test() 