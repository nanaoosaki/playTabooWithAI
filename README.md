# Taboo Game with AI

An AI-driven implementation of the classic Taboo word-guessing game, featuring both AI and human players.

## Features

- Multiple Game Modes:
  - AI vs AI: Watch two AI agents play against each other
  - Human Describer vs AI Guesser: Test your description skills
  - Human Guesser vs AI Describer: Challenge your word-guessing abilities

- Smart AI Agents:
  - Anthropic Claude for generating clear, constraint-following descriptions
  - OpenAI GPT-4 for semantic understanding and intelligent guessing
  - Progressive hint system with contextual awareness

- Advanced Game Mechanics:
  - Dynamic word selection using NLTK WordNet
  - Real-time taboo word validation
  - Multi-turn interaction with progressive hints
  - Flexible skip system for difficult words
  - Comprehensive round history and scoring

## Setup

1. Clone the repository:
```bash
git clone https://github.com/nanaoosaki/playTabooWithAI.git
cd playTabooWithAI
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
- Copy `.env.example` to `.env`
- Add your API keys for OpenAI and Anthropic

## Usage

Run the game with default settings:
```bash
python play_taboo.py
```

Customize game settings:
```bash
python play_taboo.py --mode human_describer --time-limit 120 --max-rounds 5
```

Available options:
- `--mode`: Game mode (`ai_only`, `human_describer`, `human_guesser`)
- `--time-limit`: Time limit per round in seconds (default: 60)
- `--max-rounds`: Number of rounds to play (default: 5)
- `--min-word-length`: Minimum length of target words (default: 4)
- `--max-word-length`: Maximum length of target words (default: 8)
- `--describer`: LLM provider for describer (`anthropic`, `openai`, `local`)
- `--guesser`: LLM provider for guesser (`anthropic`, `openai`, `local`)

## Testing

Run the test suite:
```bash
python run_tests.py
```

## Project Structure

```
src/
├── taboo_game/         # Core game package
│   ├── game.py         # Game logic
│   ├── cli.py          # Command-line interface
│   ├── agents/         # AI agents
│   └── utils/          # Utilities
├── tools/              # External tools
└── tests/              # Test suite
```

## License

MIT License - see LICENSE file for details.
