"""
Word database utility for the Taboo game using NLTK's WordNet.
"""

import random
from typing import List, Tuple, Set, Optional
from nltk.corpus import wordnet as wn
import time

class WordDatabase:
    """Word database utility for the Taboo game using NLTK's WordNet."""
    
    _instance: Optional['WordDatabase'] = None
    _synsets_cache = None  # Class-level cache for synsets
    _wordnet_ready = False  # Track if WordNet is ready
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, min_word_length: int = 4, max_word_length: int = 12):
        """
        Initialize the word database.
        
        Args:
            min_word_length: Minimum length of target words
            max_word_length: Maximum length of target words
        """
        # Only initialize once
        if hasattr(self, 'initialized'):
            return
            
        self.initialized = True
        self.min_word_length = min_word_length
        self.max_word_length = max_word_length
        self.word_pool = []
        
        # Lazy initialization - don't load anything yet
        if not WordDatabase._wordnet_ready:
            self._ensure_wordnet_downloaded()
            WordDatabase._wordnet_ready = True
    
    def _ensure_wordnet_downloaded(self):
        """Ensure WordNet data is downloaded."""
        import nltk
        print("🕒 Checking WordNet data...")
        start_time = time.time()
        try:
            wn.all_synsets()
        except LookupError:
            print("📥 Downloading WordNet data...")
            nltk.download('wordnet')
        download_time = time.time() - start_time
        print(f"✓ WordNet ready in {download_time:.2f} seconds")
    
    def _get_all_synsets(self):
        """Get all noun synsets, using cache if available."""
        if WordDatabase._synsets_cache is None:
            print("🕒 Loading synsets (first time only)...")
            start_time = time.time()
            WordDatabase._synsets_cache = list(wn.all_synsets(pos='n'))
            load_time = time.time() - start_time
            print(f"✓ Loaded {len(WordDatabase._synsets_cache)} synsets in {load_time:.2f} seconds")
        return WordDatabase._synsets_cache
    
    def _initialize_word_pool(self, pool_size: int = 100):
        """Pre-generate a pool of words with their taboo words."""
        print("🕒 Pre-generating word pool...")
        start_time = time.time()
        self.word_pool = []
        
        all_synsets = self._get_all_synsets()
        
        # Common word endings to filter out
        derived_endings = ('ness', 'ment', 'tion', 'sion', 'ing', 'er', 'est', 'ly', 'ity')
        
        while len(self.word_pool) < pool_size:
            # Get a random synset
            synset = random.choice(all_synsets)
            word = synset.lemmas()[0].name()
            
            # Check if word meets our criteria
            if '_' in word or not (self.min_word_length <= len(word) <= self.max_word_length):
                continue
                
            # Skip words that are not common enough (have very few synsets)
            if len(wn.synsets(word)) < 2:
                continue
                
            # Skip derived forms and abstract concepts
            if any(word.endswith(ending) for ending in derived_endings):
                continue
            
            # Get related words
            related_words = self._get_related_words(word)
            
            # Ensure we have enough meaningful related words
            meaningful_related = {
                w for w in related_words 
                if len(w) >= 3 
                and not any(w.endswith(ending) for ending in derived_endings)
            }
            
            if len(meaningful_related) >= 5:
                # Select 5 random related words for taboo list
                taboo_words = random.sample(list(meaningful_related), 5)
                self.word_pool.append((word, taboo_words))
        
        gen_time = time.time() - start_time
        print(f"✓ Generated {len(self.word_pool)} words in {gen_time:.2f} seconds")
    
    def _get_related_words(self, word: str) -> Set[str]:
        """
        Get related words for a given word using WordNet.
        
        Args:
            word: The target word to find related words for
        
        Returns:
            A set of related words
        """
        related = set()
        
        # Get all synsets for the word
        synsets = wn.synsets(word)
        if not synsets:
            return related
        
        # Add synonyms
        for synset in synsets:
            # Add lemma names (synonyms)
            related.update(lemma.name() for lemma in synset.lemmas())
            
            # Add hypernyms (more general terms)
            for hypernym in synset.hypernyms():
                related.update(lemma.name() for lemma in hypernym.lemmas())
            
            # Add hyponyms (more specific terms)
            for hyponym in synset.hyponyms():
                related.update(lemma.name() for lemma in hyponym.lemmas())
        
        # Remove the original word and any multi-word phrases
        related = {w for w in related if '_' not in w and w.lower() != word.lower()}
        return related
    
    def get_word_with_taboo(self) -> Tuple[str, List[str]]:
        """
        Get a random word and its taboo words from the pre-generated pool.
        
        Returns:
            A tuple of (target_word, list_of_taboo_words)
        """
        # Lazy initialization of word pool
        if not self.word_pool:
            self._initialize_word_pool()
        
        # Remove and return a random word pair from the pool
        index = random.randrange(len(self.word_pool))
        word_pair = self.word_pool.pop(index)
        
        # If pool is getting low, generate more words in background
        if len(self.word_pool) < 20:
            self._initialize_word_pool(50)
        
        return word_pair

def test_word_database():
    """Simple test function for the WordDatabase class."""
    db = WordDatabase()
    word, taboo_words = db.get_word_with_taboo()
    print(f"Target word: {word}")
    print("Taboo words:")
    for taboo in taboo_words:
        print(f"- {taboo}")

if __name__ == "__main__":
    test_word_database() 