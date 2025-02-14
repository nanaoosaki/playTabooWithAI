"""
Test suite for word database functionality.
"""

import unittest
import time
from src.taboo_game.utils.word_database import WordDatabase

class TestWordDatabase(unittest.TestCase):
    """Test cases for WordDatabase class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.db = WordDatabase()
    
    def test_initialization(self):
        """Test database initialization."""
        # Test singleton pattern
        db2 = WordDatabase()
        self.assertIs(self.db, db2)
    
    def test_word_generation(self):
        """Test word and taboo word generation."""
        word, taboo = self.db.get_word_with_taboo()
        
        # Check word format
        self.assertIsInstance(word, str)
        self.assertTrue(4 <= len(word) <= 12)
        
        # Check taboo words
        self.assertIsInstance(taboo, list)
        self.assertEqual(len(taboo), 5)
        for t in taboo:
            self.assertIsInstance(t, str)
            self.assertNotEqual(t.lower(), word.lower())

def test_performance():
    """Test performance of word database operations."""
    # Test first initialization (should do the full setup)
    print("\nTesting first WordDatabase initialization...")
    start = time.time()
    db1 = WordDatabase()
    init_time = time.time() - start
    print(f"First initialization time: {init_time:.2f} seconds")
    
    # Test second initialization (should be instant due to singleton)
    print("\nTesting second WordDatabase initialization...")
    start = time.time()
    db2 = WordDatabase()
    init_time = time.time() - start
    print(f"Second initialization time: {init_time:.2f} seconds")
    print(f"Same instance? {db1 is db2}")
    
    # Test first word retrieval (should trigger lazy loading)
    print("\nTesting first word retrieval (with lazy loading)...")
    start = time.time()
    word, taboo = db1.get_word_with_taboo()
    retrieval_time = time.time() - start
    print(f"First retrieval time: {retrieval_time:.2f} seconds")
    print(f"Word: {word}")
    print(f"Taboo words: {taboo}")
    
    # Test subsequent retrievals (should be fast)
    print("\nTesting 10 consecutive retrievals...")
    start = time.time()
    for i in range(10):
        word, taboo = db1.get_word_with_taboo()
    avg_time = (time.time() - start) / 10
    print(f"Average retrieval time: {avg_time:.2f} seconds")

def test_taboo_words():
    """Test taboo word generation with sample output."""
    print("\n" + "="*50)
    print("STARTING TABOO WORD TEST")
    print("="*50)
    
    # Create database instance
    print("\nCreating WordDatabase instance...")
    db = WordDatabase()
    
    print("\n" + "="*50)
    print("GENERATING 5 SAMPLE WORDS")
    print("="*50)
    
    # Get 5 sample words with their taboo words
    for i in range(5):
        print(f"\n🎲 WORD SET #{i+1}")
        print("-" * 20)
        word, taboo = db.get_word_with_taboo()
        print(f"TARGET WORD: {word}")
        print("\nTABOO WORDS:")
        for t in taboo:
            print(f"  • {t}")
        print("-" * 20)
    
    print("\n" + "="*50)
    print("TEST COMPLETE")
    print("="*50 + "\n")

if __name__ == '__main__':
    unittest.main() 