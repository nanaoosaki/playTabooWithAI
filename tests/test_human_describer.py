"""
Test suite for Human Describer vs AI mode in the Taboo game.
"""

import unittest
from src.taboo_game.cli import TabooGameCLI
from src.taboo_game.game import GameState, RoundResult

class TestHumanDescriberMode(unittest.TestCase):
    """Test cases for Human Describer vs AI gameplay."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.game = TabooGameCLI(
            mode="human_describer",
            round_time_limit=120,  # 2 minutes per round for human thinking
            max_rounds=1,
            guesser_provider="openai"  # GPT-4 for better semantic understanding
        )
    
    def test_initialization(self):
        """Test game initialization."""
        self.assertEqual(self.game.mode, "human_describer")
        self.assertEqual(self.game.game.round_time_limit, 120)
        self.assertEqual(self.game.game.max_rounds, 1)
        self.assertEqual(self.game.game.state, GameState.INITIALIZED)
    
    def test_skip_system(self):
        """Test the skip system functionality."""
        self.game.game.start_game()
        word, taboo = self.game.game.start_round()
        
        # Verify initial state
        self.assertEqual(self.game.game.state, GameState.DESCRIBING)
        self.assertIsNotNone(word)
        self.assertIsNotNone(taboo)
        
        # Test skip
        self.game.game.skip_round()
        self.assertEqual(self.game.game.state, GameState.ROUND_ENDED)

def run_human_describer_test():
    """Run an interactive Human Describer vs AI game test."""
    print("\n" + "="*50)
    print("STARTING TABOO GAME - HUMAN DESCRIBER MODE")
    print("="*50)
    
    game = TabooGameCLI(
        mode="human_describer",
        round_time_limit=120,
        max_rounds=2,  # 2 rounds for testing
        guesser_provider="openai"
    )
    
    print("\nGame Configuration:")
    print("- Describer: Human (You)")
    print("- Guesser: GPT-4 (OpenAI)")
    print("- Rounds: 2")
    print("- Time limit: 120 seconds per round")
    print("- Skips: 5 per round")
    
    print("\nGame Rules:")
    print("1. You will be shown a target word and taboo words")
    print("2. Describe the target word WITHOUT using:")
    print("   - The target word itself")
    print("   - Any part or variation of the target word")
    print("   - Any of the taboo words")
    print("3. Type 'skip' to skip a difficult word (5 skips available)")
    print("4. After AI's guess, you can:")
    print("   - Try describing again with different words")
    print("   - Skip to a new word (if skips available)")
    print("   - End the round")
    print("\nTips:")
    print("- Start with the word type (noun/verb/adjective)")
    print("- Use fill-in-the-blank sentences")
    print("- Give examples of usage")
    print("- Think about common contexts\n")
    
    game.play_game()

if __name__ == '__main__':
    # For quick testing, run the interactive test
    run_human_describer_test() 