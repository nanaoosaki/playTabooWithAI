"""
Test suite for different game modes (AI vs AI, Human vs AI).
"""

import unittest
from src.taboo_game.cli import TabooGameCLI

class TestAIDescriberMode(unittest.TestCase):
    """Test cases for AI describer mode."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.game = TabooGameCLI(
            mode="human_guesser",
            round_time_limit=120,
            max_rounds=1,
            describer_provider="anthropic"
        )
    
    def test_initialization(self):
        """Test game initialization."""
        self.assertEqual(self.game.mode, "human_guesser")
        self.assertEqual(self.game.game.round_time_limit, 120)
        self.assertEqual(self.game.game.max_rounds, 1)

class TestHumanDescriberMode(unittest.TestCase):
    """Test cases for human describer mode."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.game = TabooGameCLI(
            mode="human_describer",
            round_time_limit=120,
            max_rounds=1,
            guesser_provider="openai"
        )
    
    def test_initialization(self):
        """Test game initialization."""
        self.assertEqual(self.game.mode, "human_describer")
        self.assertEqual(self.game.game.round_time_limit, 120)
        self.assertEqual(self.game.game.max_rounds, 1)

def run_ai_describer_test():
    """Run AI describer mode test."""
    print("\n" + "="*50)
    print("STARTING TABOO GAME - AI DESCRIBER MODE")
    print("="*50)
    
    game = TabooGameCLI(
        mode="human_guesser",
        round_time_limit=120,
        max_rounds=1,
        describer_provider="anthropic"
    )
    
    print("\nGame Rules:")
    print("1. The AI will describe a word without using taboo words")
    print("2. You can type your guess")
    print("3. Type 'hint' to get an additional hint")
    print("4. Type 'skip' to skip to the next word")
    print("5. You have multiple attempts within the time limit\n")
    
    game.play_game()

def run_human_describer_test():
    """Run human describer mode test."""
    print("\n" + "="*50)
    print("STARTING TABOO GAME - HUMAN DESCRIBER MODE")
    print("="*50)
    
    game = TabooGameCLI(
        mode="human_describer",
        round_time_limit=120,
        max_rounds=1,
        guesser_provider="openai"
    )
    
    game.play_game()

if __name__ == '__main__':
    unittest.main() 