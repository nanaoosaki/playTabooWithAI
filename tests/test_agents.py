"""
Tests for the Taboo game AI agents.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.taboo_game.agents import DescriberAgent, GuesserAgent

class TestDescriberAgent(unittest.TestCase):
    """Test cases for the DescriberAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = DescriberAgent()
        self.test_word = "computer"
        self.test_taboo_words = ["machine", "keyboard", "screen", "device", "electronic"]
    
    def test_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.provider, "anthropic")
        self.assertIsNone(self.agent.last_response)
        self.assertIsNone(self.agent._current_word)
        self.assertIsNone(self.agent._current_taboo_words)
    
    def test_reset(self):
        """Test agent reset functionality."""
        # Set some state
        self.agent._current_word = "test"
        self.agent._current_taboo_words = ["word"]
        self.agent._last_response = "response"
        
        # Reset
        self.agent.reset()
        
        # Verify everything is reset
        self.assertIsNone(self.agent._current_word)
        self.assertIsNone(self.agent._current_taboo_words)
        self.assertIsNone(self.agent._last_response)
    
    @patch('src.taboo_game.agents.describer.query_llm')
    def test_generate_description(self, mock_query_llm):
        """Test description generation."""
        # Mock the LLM response
        mock_description = "A device that processes information and performs calculations."
        mock_query_llm.return_value = mock_description
        
        # Generate description
        description = self.agent.generate_description(self.test_word, self.test_taboo_words)
        
        # Verify the description
        self.assertEqual(description, mock_description)
        self.assertEqual(self.agent.last_response, mock_description)
        self.assertEqual(self.agent._current_word, self.test_word)
        self.assertEqual(self.agent._current_taboo_words, self.test_taboo_words)
        
        # Verify LLM was called with correct prompt
        mock_query_llm.assert_called_once()
        prompt = mock_query_llm.call_args[0][0]
        self.assertIn(self.test_word, prompt)
        for taboo in self.test_taboo_words:
            self.assertIn(taboo, prompt)
    
    @patch('src.taboo_game.agents.describer.query_llm')
    def test_refine_description(self, mock_query_llm):
        """Test description refinement."""
        # Set up initial state
        self.agent._current_word = self.test_word
        self.agent._current_taboo_words = self.test_taboo_words
        
        # Mock the LLM response
        mock_refined = "A tool that helps solve complex problems using mathematics."
        mock_query_llm.return_value = mock_refined
        
        # Refine description
        feedback = "Too vague, focus more on its problem-solving capabilities"
        refined = self.agent.refine_description(feedback)
        
        # Verify the refined description
        self.assertEqual(refined, mock_refined)
        self.assertEqual(self.agent.last_response, mock_refined)
        
        # Verify LLM was called with correct prompt
        mock_query_llm.assert_called_once()
        prompt = mock_query_llm.call_args[0][0]
        self.assertIn(feedback, prompt)
        self.assertIn(self.test_word, prompt)
        for taboo in self.test_taboo_words:
            self.assertIn(taboo, prompt)
    
    def test_refine_description_no_current_word(self):
        """Test refinement without current word raises error."""
        with self.assertRaises(ValueError):
            self.agent.refine_description("feedback")

class TestGuesserAgent(unittest.TestCase):
    """Test cases for the GuesserAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = GuesserAgent()
        self.test_description = "This tool helps solve complex problems using mathematics."
    
    def test_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.provider, "openai")
        self.assertIsNone(self.agent.last_response)
        self.assertEqual(self.agent._round_history, [])
    
    def test_reset(self):
        """Test agent reset functionality."""
        # Add some history
        self.agent._round_history.append({
            'description': 'test description',
            'word': 'test'
        })
        self.agent._last_response = 'test'
        
        # Reset
        self.agent.reset()
        
        # Verify everything is reset
        self.assertEqual(self.agent._round_history, [])
        self.assertIsNone(self.agent._last_response)
    
    @patch('src.taboo_game.agents.guesser.query_llm')
    def test_make_guess_no_history(self, mock_query_llm):
        """Test guess making without history."""
        # Mock the LLM response
        mock_guess = "computer"
        mock_query_llm.return_value = mock_guess
        
        # Make guess
        guess = self.agent.make_guess(self.test_description)
        
        # Verify the guess
        self.assertEqual(guess, mock_guess)
        self.assertEqual(self.agent.last_response, mock_guess)
        
        # Verify LLM was called with correct prompt
        mock_query_llm.assert_called_once()
        prompt = mock_query_llm.call_args[0][0]
        self.assertIn(self.test_description, prompt)
        self.assertNotIn("Previous rounds for context", prompt)
    
    @patch('src.taboo_game.agents.guesser.query_llm')
    def test_make_guess_with_history(self, mock_query_llm):
        """Test guess making with history."""
        # Add some history
        self.agent._round_history = [
            {'description': 'test desc 1', 'word': 'word1'},
            {'description': 'test desc 2', 'word': 'word2'}
        ]
        
        # Mock the LLM response
        mock_guess = "computer"
        mock_query_llm.return_value = mock_guess
        
        # Make guess
        guess = self.agent.make_guess(self.test_description)
        
        # Verify the guess
        self.assertEqual(guess, mock_guess)
        
        # Verify LLM was called with correct prompt
        mock_query_llm.assert_called_once()
        prompt = mock_query_llm.call_args[0][0]
        self.assertIn(self.test_description, prompt)
        self.assertIn("Previous rounds for context", prompt)
        self.assertIn("word1", prompt)
        self.assertIn("word2", prompt)
    
    def test_record_result(self):
        """Test recording round results."""
        description = "test description"
        word = "test"
        
        # Record result
        self.agent.record_result(description, word)
        
        # Verify history was updated
        self.assertEqual(len(self.agent._round_history), 1)
        self.assertEqual(self.agent._round_history[0]['description'], description)
        self.assertEqual(self.agent._round_history[0]['word'], word)

if __name__ == '__main__':
    unittest.main() 