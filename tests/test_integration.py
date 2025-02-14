"""
Integration tests for the Taboo game.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.taboo_game.game import TabooGame, GameState, RoundResult

class TestGameWithAgents(unittest.TestCase):
    """Integration tests for TabooGame with AI agents."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.game = TabooGame(
            round_time_limit=60,
            max_rounds=3,
            min_word_length=4,
            max_word_length=8
        )
        self.test_word = "computer"
        self.test_taboo_words = ["machine", "keyboard", "screen", "device", "electronic"]
    
    @patch('src.taboo_game.utils.word_database.WordDatabase.get_word_with_taboo')
    @patch('src.taboo_game.agents.describer.query_llm')
    @patch('src.taboo_game.agents.guesser.query_llm')
    def test_successful_round(self, mock_guesser_llm, mock_describer_llm, mock_get_word):
        """Test a successful round where the guesser correctly guesses the word."""
        # Mock the word database to return our test word
        mock_get_word.return_value = (self.test_word, self.test_taboo_words)
        
        # Mock the describer's response
        mock_description = "A tool that helps solve complex problems using mathematics."
        mock_describer_llm.return_value = mock_description
        
        # Mock the guesser's response to match the target word
        mock_guesser_llm.return_value = self.test_word
        
        # Start the game and first round
        self.game.start_game()
        word, taboo = self.game.start_round()
        
        # Verify initial state
        self.assertEqual(word, self.test_word)
        self.assertEqual(taboo, self.test_taboo_words)
        self.assertEqual(self.game.state, GameState.DESCRIBING)
        
        # Generate description
        description = self.game.generate_description()
        self.assertEqual(description, mock_description)
        
        # Verify description is valid (doesn't use taboo words)
        is_valid = self.game.check_description(description)
        self.assertTrue(is_valid)
        
        # Make guess
        guess, result = self.game.make_guess()
        
        # Verify results
        self.assertEqual(guess, self.test_word)
        self.assertEqual(result, RoundResult.CORRECT_GUESS)
        self.assertEqual(self.game.score, 1)
        self.assertEqual(self.game.state, GameState.ROUND_ENDED)
        
        # Verify round was recorded
        self.assertEqual(len(self.game.round_history), 1)
        round_data = self.game.round_history[0]
        self.assertEqual(round_data['target_word'], self.test_word)
        self.assertEqual(round_data['description'], mock_description)
        self.assertEqual(round_data['guess'], self.test_word)
        self.assertEqual(round_data['result'], RoundResult.CORRECT_GUESS)
    
    @patch('src.taboo_game.utils.word_database.WordDatabase.get_word_with_taboo')
    @patch('src.taboo_game.agents.describer.query_llm')
    @patch('src.taboo_game.agents.guesser.query_llm')
    def test_incorrect_guess(self, mock_guesser_llm, mock_describer_llm, mock_get_word):
        """Test a round where the guesser makes an incorrect guess."""
        # Mock the word database
        mock_get_word.return_value = (self.test_word, self.test_taboo_words)
        
        # Mock the describer's response
        mock_description = "A tool that helps solve complex problems."
        mock_describer_llm.return_value = mock_description
        
        # Mock the guesser's response
        mock_guesser_llm.return_value = "calculator"
        
        # Play the round
        self.game.start_game()
        self.game.start_round()
        description = self.game.generate_description()
        guess, result = self.game.make_guess()
        
        # Verify results
        self.assertEqual(guess, "calculator")
        self.assertEqual(result, RoundResult.INCORRECT_GUESS)
        self.assertEqual(self.game.score, 0)
        
        # Verify no round recording for incorrect guess
        self.assertEqual(len(self.game.round_history), 0)
    
    @patch('src.taboo_game.utils.word_database.WordDatabase.get_word_with_taboo')
    @patch('src.taboo_game.agents.describer.query_llm')
    def test_invalid_description(self, mock_describer_llm, mock_get_word):
        """Test handling of a description that uses taboo words."""
        # Mock the word database
        mock_get_word.return_value = (self.test_word, self.test_taboo_words)
        
        # Mock the describer to use a taboo word
        mock_description = "A machine that processes information."
        mock_describer_llm.return_value = mock_description
        
        # Play the round
        self.game.start_game()
        self.game.start_round()
        description = self.game.generate_description()
        
        # Verify the description is invalid
        is_valid = self.game.check_description(description)
        self.assertFalse(is_valid)
        self.assertEqual(self.game.state, GameState.ROUND_ENDED)
    
    @patch('src.taboo_game.utils.word_database.WordDatabase.get_word_with_taboo')
    @patch('src.taboo_game.agents.describer.query_llm')
    @patch('src.taboo_game.agents.guesser.query_llm')
    def test_multiple_rounds(self, mock_guesser_llm, mock_describer_llm, mock_get_word):
        """Test playing multiple rounds with different outcomes."""
        # Mock the word database
        mock_get_word.return_value = (self.test_word, self.test_taboo_words)
        
        # Mock the agents' responses for different rounds
        mock_describer_llm.side_effect = [
            "A tool for calculations",  # Round 1
            "A problem-solving device",  # Round 2 (uses taboo word)
            "Helps with math"  # Round 3
        ]
        mock_guesser_llm.side_effect = [
            self.test_word,  # Round 1 - correct
            "wrong",  # Round 2 - incorrect
            "calculator"  # Round 3 - incorrect
        ]
        
        # Play multiple rounds
        self.game.start_game()
        
        # Round 1 - Correct guess
        self.game.start_round()
        self.game.generate_description()
        guess, result = self.game.make_guess()
        self.assertEqual(result, RoundResult.CORRECT_GUESS)
        self.assertEqual(self.game.score, 1)
        
        # Round 2 - Invalid description
        self.game.start_round()
        self.game.generate_description()
        is_valid = self.game.check_description("A problem-solving device")
        self.assertFalse(is_valid)
        
        # Round 3 - Incorrect guess
        self.game.start_round()
        self.game.generate_description()
        guess, result = self.game.make_guess()
        self.assertEqual(result, RoundResult.INCORRECT_GUESS)
        
        # Verify final game state
        self.assertEqual(self.game.score, 1)
        self.assertEqual(len(self.game.round_history), 1)  # Only successful rounds are recorded

if __name__ == '__main__':
    unittest.main() 