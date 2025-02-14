#!/usr/bin/env python3
"""
Script to run all tests for the Taboo game.
"""

import unittest
import sys
import os

def run_tests():
    """Run all test suites."""
    # Add src directory to Python path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1) 