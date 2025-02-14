"""
Command-line interface for the Taboo game.
"""

import time
import argparse
from typing import Optional, Literal
from .game import TabooGame, GameState, RoundResult

class TabooGameCLI:
    """Command-line interface for playing the Taboo game."""
    
    def __init__(self, 
                 round_time_limit: int = 60,
                 max_rounds: int = 5,
                 min_word_length: int = 4,
                 max_word_length: int = 8,
                 describer_provider: str = "anthropic",
                 guesser_provider: str = "openai",
                 mode: Literal["ai_only", "human_describer", "human_guesser"] = "ai_only"):
        """Initialize the CLI interface."""
        self.game = TabooGame(
            round_time_limit=round_time_limit,
            max_rounds=max_rounds,
            min_word_length=min_word_length,
            max_word_length=max_word_length,
            describer_provider=describer_provider,
            guesser_provider=guesser_provider
        )
        self.mode = mode
    
    def _get_human_description(self) -> Optional[str]:
        """Get description from human player."""
        print("\n🎮 Your turn to describe the word!")
        print("Rules:")
        print("1. Don't use any of the taboo words")
        print("2. Keep it concise (2-3 sentences)")
        print("3. Type 'skip' to skip this round")
        print("4. Be creative but clear!")
        print("\nTips:")
        print("- Start with the word type (noun/verb/adjective)")
        print("- Mention the general category")
        print("- Use common scenarios or fill-in-the-blank phrases")
        print("- Think about how the word is commonly used\n")
        
        while True:
            description = input("Your description: ").strip()
            
            if description.lower() == 'skip':
                return None
            
            if not description:
                print("❌ Description cannot be empty. Try again!")
                continue
            
            # Check for taboo words
            if not self.game.check_description(description):
                print("🚫 Your description contains taboo words! Try again.")
                print("Taboo words:", ", ".join(self.game.taboo_words or []))
                continue
            
            # Store the description in the game state
            self.game.current_description = description
            return description
    
    def _get_human_guess(self) -> str:
        """Get guess from human player."""
        print("\n🎮 Your turn to guess!")
        print("Rules:")
        print("1. Type your guess (single word)")
        print("2. Type 'hint' to get a new hint")
        print("3. Type 'skip' to skip this word (you have 5 skips per round)")
        print("4. You have multiple attempts until time runs out\n")
        
        hint_count = 0
        skip_count = 0
        max_hints = 2  # Allow 2 additional hints (3 total descriptions)
        max_skips = 5  # Allow up to 5 skips per round
        
        while self.game.check_time_remaining() > 0:
            remaining = self.game.check_time_remaining()
            guess = input(f"Your guess ({remaining:.1f}s remaining, {max_skips - skip_count} skips left): ").strip().lower()
            
            if guess == 'skip':
                skip_count += 1
                if skip_count >= max_skips:
                    print("❌ No more skips available! You must try to guess the word.")
                    continue
                print(f"Word skipped! You have {max_skips - skip_count} skips remaining.")
                return ""
            
            if guess == 'hint':
                if hint_count >= max_hints:
                    print("❌ No more hints available! Make your best guess!")
                    continue
                    
                print("\n🤖 Getting a new hint...")
                # Pass previous guesses as context for the new hint
                previous_guesses_str = ", ".join(self.game.previous_guesses) if self.game.previous_guesses else "no guesses yet"
                new_description = self.game.refine_description(previous_guesses_str)
                self._print_description_for_human(new_description)
                hint_count += 1
                continue
            
            if not guess:
                print("❌ Guess cannot be empty. Try again!")
                continue
            
            if " " in guess:
                print("❌ Guess must be a single word. Try again!")
                continue
            
            # Store the guess for context in future hints
            self.game.previous_guesses.append(guess)
            
            # Check if the guess is correct
            if self.game._are_words_matching(guess, self.game.current_word):
                return guess
            else:
                print("❌ Not quite! Try again, type 'hint' for another clue, or 'skip' to move on.")
                continue
        
        print("\n⏰ Time's up!")
        return ""
    
    def _print_ai_analysis(self, guess: str):
        """Print AI's guess analysis and feedback."""
        analysis = self.game.guesser.last_analysis
        if not analysis:
            return
        
        print("\n" + "="*25 + " AI's ANALYSIS " + "="*25)
        print("🤔 AI's thought process:")
        print(f"Guess: {guess}")
        if analysis.get('reasoning'):
            print(f"Reasoning: {analysis['reasoning']}")
        if analysis.get('feedback'):
            print(f"\n💡 Suggestion for clearer description:")
            print(analysis['feedback'])
        print("="*66 + "\n")
    
    def _handle_human_description_round(self) -> tuple[str, RoundResult]:
        """Handle a round where the human is the describer."""
        max_skips = 5    # Maximum number of skips allowed
        skip_count = 0   # Track number of skips used
        
        while skip_count < max_skips and self.game.check_time_remaining() > 0:
            # Show remaining skips at the start of each word
            print(f"\n💫 You have {max_skips - skip_count} skips remaining")
            
            # Get a new word if needed (use is_skip=True to stay in same round)
            if skip_count > 0:  # Only use is_skip after first skip
                word, taboo_words = self.game.start_round(is_skip=True)
                self._print_word_info(word, taboo_words)
            
            # Ensure we're in DESCRIBING state
            self.game.state = GameState.DESCRIBING
            
            # Get description from human
            description = self._get_human_description()
            
            if description is None:  # User chose to skip
                skip_count += 1
                if skip_count >= max_skips:
                    print("❌ No more skips available! You must try to describe this word.")
                    continue
                print(f"Word skipped! You have {max_skips - skip_count} skips remaining.")
                continue
            
            # Check for taboo words
            if not self.game.check_description(description):
                print("🚫 Your description contains taboo words! Try again.")
                continue
            
            # Store the description and ensure state is correct
            self.game.current_description = description
            self.game.state = GameState.DESCRIBING  # Ensure we're in the right state
            
            # Get AI's guess
            print("\n🤖 AI is thinking about your description...")
            guess, result = self.game.make_guess()
            
            # Show AI's analysis
            self._print_ai_analysis(guess)
            
            if result == RoundResult.CORRECT_GUESS:
                return guess, result
            
            # If incorrect, ask if they want to try again, skip, or end round
            print("\nOptions:")
            print("1. Try describing again with different words")
            print(f"2. Skip to a new word ({max_skips - skip_count} skips remaining)")
            print("3. End this round")
            
            while True:  # Keep asking until valid input
                choice = input("What would you like to do? (1/2/3): ").strip()
                
                if choice == "1":  # Try again with same word
                    break  # Continue the outer loop
                elif choice == "2":  # Skip
                    if skip_count >= max_skips:
                        print("❌ No more skips available! Choose another option.")
                        continue
                    skip_count += 1
                    print(f"Word skipped! You have {max_skips - skip_count} skips remaining.")
                    break  # Get a new word in the outer loop
                elif choice == "3":  # End round
                    return guess, RoundResult.INCORRECT_GUESS
                else:
                    print("❌ Invalid choice. Please enter 1, 2, or 3.")
                    continue
                
            if choice == "2":  # If skipped, continue outer loop to get new word
                continue
        
        return "", RoundResult.TIME_UP
    
    def _handle_guess(self) -> tuple[str, RoundResult]:
        """Handle guess generation based on game mode."""
        if self.mode == "human_guesser":
            guess = self._get_human_guess()
            
            if not guess:
                return "", RoundResult.SKIPPED
            
            if self.game._are_words_matching(guess, self.game.current_word):
                self.game.score += 1
                self.game.state = GameState.ROUND_ENDED
                result = RoundResult.CORRECT_GUESS
            else:
                result = RoundResult.INCORRECT_GUESS
            
            if result in [RoundResult.CORRECT_GUESS, RoundResult.TIME_UP]:
                self.game._record_round(guess, result)
            
            return guess, result
        elif self.mode == "human_describer":
            return self._handle_human_description_round()
        else:
            # AI guesser logic
            try:
                print("🤖 Guesser Agent is thinking...")
                return self.game.make_guess()
            except Exception as e:
                print(f"❌ Error making guess: {e}")
                return "", RoundResult.SKIPPED
    
    def _print_header(self):
        """Print game header."""
        print("\n" + "="*50)
        print("🎮 TABOO - AI vs Human Edition 🤖")
        if self.mode == "human_describer":
            print("Mode: You are the Describer vs AI Guesser")
        elif self.mode == "human_guesser":
            print("Mode: You are the Guesser vs AI Describer")
        else:
            print("Mode: AI vs AI")
        print("="*50 + "\n")
    
    def _print_round_header(self):
        """Print round header."""
        print("\n" + "-"*50)
        print(f"📝 Round {self.game.current_round}/{self.game.max_rounds}")
        print(f"🎯 Score: {self.game.score}")
        print("-"*50 + "\n")
    
    def _print_word_info(self, word: str, taboo_words: list[str]):
        """Print word and taboo words."""
        print(f"🎲 Target Word: {word}")
        print("🚫 Taboo Words:")
        for word in taboo_words:
            print(f"  - {word}")
        print()
    
    def _print_time_remaining(self):
        """Print time remaining in round."""
        remaining = self.game.check_time_remaining()
        print(f"\n⏱️  Time remaining: {remaining:.1f} seconds")
    
    def _print_description_for_human(self, description: str):
        """Print description in a clear format for human players."""
        print("\n" + "="*25 + " AI's DESCRIPTION " + "="*25)
        print("📝 The AI describes the word as:")
        print(f"\"{description}\"")
        print("="*66 + "\n")
    
    def _print_result(self, guess: str, result: RoundResult):
        """Print round result."""
        print("\n" + "-"*25 + " RESULT " + "-"*25)
        
        # Adjust display based on game mode
        if self.mode == "human_guesser":
            print(f"🤔 Your guess: {guess}")
        else:
            print(f"🤔 AI Guess: {guess}")
        
        if result == RoundResult.CORRECT_GUESS:
            print("✅ Correct guess! Point scored!")
        elif result == RoundResult.INCORRECT_GUESS:
            print(f"❌ Incorrect! The word was: {self.game.current_word}")
        elif result == RoundResult.TIME_UP:
            print("⏰ Time's up!")
            print(f"The word was: {self.game.current_word}")
        elif result == RoundResult.TABOO_WORD_USED:
            print("🚫 Taboo word used in description!")
        elif result == RoundResult.SKIPPED:
            print("⏭️  Round skipped")
            print(f"The word was: {self.game.current_word}")
        
        print("-"*58 + "\n")
    
    def _print_game_summary(self):
        """Print game summary."""
        print("\n" + "="*25 + " GAME OVER " + "="*25)
        print(f"🎯 Final Score: {self.game.score}/{self.game.max_rounds}")
        print("\n📊 Round History:")
        
        for round_data in self.game.round_history:
            print(f"\nRound {round_data['round']}:")
            print(f"Word: {round_data['target_word']}")
            print(f"Description: {round_data['description']}")
            print(f"Guess: {round_data['guess']}")
            print(f"Result: {round_data['result']}")
            print(f"Time: {round_data['time_taken']:.1f}s")
        
        print("\n" + "="*58 + "\n")
    
    def _handle_description(self) -> Optional[str]:
        """Handle description generation based on game mode."""
        if self.mode == "human_describer":
            return self._get_human_description()
        
        # AI describer logic
        max_retries = 2
        try:
            for attempt in range(max_retries):
                print("🤖 Describer Agent is thinking...")
                description = self.game.generate_description()
                print(f"📝 Description: {description}\n")
                
                if not self.game.check_description(description):
                    if attempt < max_retries - 1:
                        print("🚫 Description contains taboo words! Trying again...")
                        feedback = (
                            "Your description contained taboo words. "
                            "Please try again with completely different words and approach. "
                            "Focus on unique characteristics or use cases."
                        )
                        description = self.game.refine_description(feedback)
                        print(f"📝 New Description: {description}\n")
                        
                        if self.game.check_description(description):
                            return description
                    else:
                        print("🚫 Failed to generate valid description. Round ended.")
                        self.game.state = GameState.ROUND_ENDED
                        return None
                else:
                    return description
            
            return None
            
        except Exception as e:
            print(f"❌ Error generating description: {e}")
            self.game.state = GameState.ROUND_ENDED
            return None
    
    def play_round(self) -> bool:
        """Play a single round."""
        try:
            print("\n🕒 Starting new round...")
            round_start = time.time()
            
            self._print_round_header()
            
            # Start round and get word
            print("🕒 Generating word and taboo words...")
            word_start = time.time()
            word, taboo_words = self.game.start_round()
            word_time = time.time() - word_start
            print(f"✓ Word generated in {word_time:.2f} seconds")
            
            # Only show target word in human describer mode
            if self.mode == "human_describer":
                self._print_word_info(word, taboo_words)
            
            # Handle the round based on mode
            if self.mode == "human_describer":
                guess, result = self._handle_human_description_round()
            else:
                description = self._handle_description()
                if not description:
                    return True
                
                if self.mode == "human_guesser":
                    self._print_description_for_human(description)
                
                guess, result = self._handle_guess()
            
            self._print_result(guess, result)
            
            round_time = time.time() - round_start
            print(f"✓ Round completed in {round_time:.2f} seconds")
            
            time.sleep(2)
            return True
            
        except ValueError as e:
            if str(e) == "Maximum rounds reached":
                return False
            print(f"❌ Error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def play_game(self):
        """Play a full game."""
        print("\n🕒 Starting game initialization...")
        start_time = time.time()
        
        self._print_header()
        print("🎮 Starting new game...")
        self.game.start_game()
        
        init_time = time.time() - start_time
        print(f"✓ Game initialized in {init_time:.2f} seconds")
        
        while self.game.state != GameState.GAME_OVER:
            if not self.play_round():
                break
        
        self._print_game_summary()

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Play Taboo with AI agents")
    parser.add_argument("--time-limit", type=int, default=60,
                       help="Time limit per round in seconds")
    parser.add_argument("--max-rounds", type=int, default=5,
                       help="Number of rounds to play")
    parser.add_argument("--min-word-length", type=int, default=4,
                       help="Minimum length of target words")
    parser.add_argument("--max-word-length", type=int, default=8,
                       help="Maximum length of target words")
    parser.add_argument("--describer", choices=["anthropic", "openai", "local"],
                       default="anthropic", help="LLM provider for describer agent")
    parser.add_argument("--guesser", choices=["anthropic", "openai", "local"],
                       default="openai", help="LLM provider for guesser agent")
    parser.add_argument("--mode", choices=["ai_only", "human_describer", "human_guesser"],
                       default="ai_only", help="Game mode")
    
    args = parser.parse_args()
    
    cli = TabooGameCLI(
        round_time_limit=args.time_limit,
        max_rounds=args.max_rounds,
        min_word_length=args.min_word_length,
        max_word_length=args.max_word_length,
        describer_provider=args.describer,
        guesser_provider=args.guesser,
        mode=args.mode
    )
    
    cli.play_game()

if __name__ == "__main__":
    main() 