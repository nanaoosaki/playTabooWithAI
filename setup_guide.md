# Deep Research Agent Setup Guide for Windows PowerShell

## Overview
This guide provides step-by-step instructions for setting up the deep research agent in a Windows PowerShell environment, including common issues and their solutions.

## Prerequisites
- Windows 10 or later
- PowerShell (Run as Administrator recommended)
- Git
- Python 3.x
- OpenAI API key

## Detailed Setup Steps

### 1. Repository Setup

First, ensure you're in the directory where you want to set up the project:

```powershell
# Check current directory
pwd

# If needed, navigate to your desired directory
cd D:\your\path

# IMPORTANT: Clean up directory if needed (BE CAREFUL with these commands!)
# Remove any existing files/directories that might conflict
rm -r -Force * 
rm -r -Force .git  # Remove any existing git repository

# Clone repository directly into current directory
# The dot (.) at the end is crucial - it clones into current directory without creating a subdirectory
git clone https://github.com/grapeot/deep_research_agent.git .

# Verify files are in place - you should see:
# - deep_research_agent.py
# - tools.py
# - requirements.txt
# - etc.
dir
```

### 2. Python Virtual Environment Setup

Always run PowerShell as Administrator for setup to avoid permission issues:

```powershell
# Enable script execution (one-time setup)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Create virtual environment
python -m venv venv

# Activate virtual environment (try these methods in order until one works)
.\venv\Scripts\activate  # Method 1 (Standard)
# If that fails, try:
& "$(Get-Location)\venv\Scripts\Activate.ps1"  # Method 2 (Full path)
# If that fails, try:
cmd /c "venv\Scripts\activate.bat && powershell"  # Method 3 (CMD fallback)

# Verify activation
# Your prompt should show (venv) at the beginning
# And python should point to the venv directory:
Get-Command python | Format-List
```

### 3. Package Installation

Install packages in this specific order to avoid dependency issues:

```powershell
# First, upgrade pip
python -m pip install --upgrade pip

# Try installing all requirements at once first
pip install -r requirements.txt

# If the above fails, try with trusted hosts
pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org

# If still having issues, install critical packages individually in this order:
pip install openai  # Core dependency
pip install yfinance pandas matplotlib  # Data analysis packages
pip install aiohttp html5lib  # Web interaction packages
pip install duckduckgo_search beautifulsoup4 requests  # Search and scraping packages
```

### 4. Environment Configuration

Set up your OpenAI API key:

```powershell
# Create .env file (preferred method)
@"
OPENAI_API_KEY=your_key_here
"@ > .env

# Or set environment variable (temporary)
$env:OPENAI_API_KEY = "your-key-here"

# Or set permanently (requires restart)
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your-key-here", "User")
```

### 5. Verify Installation

Run these checks in order:

```powershell
# 1. Check directory structure
dir  # Should show all repository files

# 2. Verify virtual environment
Get-Command python  # Should point to .\venv\Scripts\python.exe
pip list  # Should show all installed packages

# 3. Test OpenAI integration
python -c "import openai; print('OpenAI module working')"

# 4. Test the research agent
python deep_research_agent.py "What is the current weather in New York?"
```

## Common Issues and Solutions

### Directory Issues
- **Problem**: Files in wrong location or nested subdirectory
  - **Solution**: Use the dot (.) when cloning
  ```powershell
  git clone https://github.com/grapeot/deep_research_agent.git .
  ```

### Virtual Environment Issues
- **Problem**: Activation script won't run
  - **Solution**: Try alternative activation methods
  - **Solution**: Check execution policy
  - **Solution**: Run PowerShell as Administrator

### Package Installation Issues
- **Problem**: SSL/TLS errors
  - **Solution**: Use trusted hosts flag
- **Problem**: Dependency conflicts
  - **Solution**: Install packages individually in the specified order

### OpenAI API Issues
- **Problem**: API key not found
  - **Solution**: Check .env file exists and is in correct directory
  - **Solution**: Verify environment variable is set
  ```powershell
  echo $env:OPENAI_API_KEY  # Should show your key
  ```

## Project Structure
```
your_directory/           # Your chosen directory
├── .env                 # API keys and configuration
├── .deep_research_rules # Agent rules and prompts
├── deep_research_agent.py
├── tools.py
├── requirements.txt
├── venv/               # Virtual environment
└── examples/           # Example outputs
```

## Final Verification Checklist
1. [ ] All files are in the correct directory (not in a subdirectory)
2. [ ] Virtual environment is activated (prompt shows `(venv)`)
3. [ ] All required packages are installed (`pip list`)
4. [ ] OpenAI API key is properly set
5. [ ] Agent runs without errors

## Best Practices

1. **Environment Management**
   - Always verify virtual environment activation
   - Check package installation paths
   - Keep requirements.txt updated

2. **Debugging**
   - Use stderr for debug output
   - Add verbose logging in development
   - Test API access separately

3. **PowerShell**
   - Use consistent path separators
   - Handle Unicode properly
   - Manage execution policies

4. **Project Structure**
   - Keep configuration in `.env`
   - Maintain clear documentation
   - Follow multi-agent format in `.cursorrules`

## Tools Reference

### LLM API
```powershell
python ./tools/llm_api.py --prompt "Your prompt" --provider "openai" --model "gpt-4-0125-preview"
```

### Web Scraper
```powershell
python ./tools/web_scraper.py --max-concurrent 3 URL1 URL2 URL3
```

### Search Engine
```powershell
python ./tools/search_engine.py "your search keywords"
```

## Multi-Agent Setup (New)

### Repository Setup for Multi-Agent Branch
```powershell
# Initialize git repository
git init

# Configure safe directory (if you get dubious ownership error)
git config --global --add safe.directory D:/your/path/here

# Add remote and fetch multi-agent branch
git remote add origin https://github.com/nanaoosaki/devin.cursorrules.git
git fetch origin multi-agent
git checkout multi-agent
git pull origin multi-agent
```

### Package Installation Order
For the multi-agent system, install packages in this specific order to avoid dependency conflicts:

```powershell
# 1. Create and activate virtual environment
python -m venv venv
$env:PATH = "$(Get-Location)\venv\Scripts;$env:PATH"

# 2. Verify virtual environment activation
Get-Command python | Select-Object Source  # Should show path in venv

# 3. Install base packages first
python -m ensurepip --upgrade
python -m pip install --upgrade pip

# 4. Install Google packages (required for LLM integration)
python -m pip install --upgrade google
python -m pip install --upgrade google-generativeai

# 5. Install OpenAI package
python -m pip install openai

# 6. Install Anthropic package
python -m pip install anthropic

# 7. Install remaining requirements
python -m pip install -r requirements.txt --no-cache-dir

# 8. Install Playwright browser (for web scraping)
python -m playwright install chromium
```

### Environment Configuration
Create a `.env` file with necessary API keys:

```powershell
@"
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
GOOGLE_API_KEY=your_google_key_here
AZURE_OPENAI_API_KEY=your_azure_key_here
AZURE_OPENAI_MODEL_DEPLOYMENT=gpt-4o-ms
"@ > .env
```

### Package Import Troubleshooting
If you encounter module import errors:

1. Create an empty `__init__.py` in the tools directory:
```powershell
@"
# Initialize tools package
"@ > tools/__init__.py
```

2. Add current directory to PYTHONPATH when running scripts:
```powershell
$env:PYTHONPATH = "."; python -m tools.llm_api --prompt "Your prompt"
```

### Common PowerShell Syntax Issues

1. **Command Chaining**:
   - Unix-style (`&&`) doesn't work in PowerShell
   - Use semicolon (`;`) instead:
   ```powershell
   # Wrong:
   git fetch origin multi-agent && git checkout multi-agent

   # Correct:
   git fetch origin multi-agent; git checkout multi-agent
   ```

2. **Path Variables**:
   - Use PowerShell path syntax:
   ```powershell
   # Wrong:
   export PYTHONPATH=.

   # Correct:
   $env:PYTHONPATH = "."
   ```

3. **Directory Paths**:
   - Use forward slashes or escaped backslashes:
   ```powershell
   # All of these work:
   git config --global --add safe.directory D:/your/path
   git config --global --add safe.directory "D:\your\path"
   git config --global --add safe.directory D:\\your\\path
   ```

## Lessons Learned

1. **Git Setup**:
   - Always configure safe.directory when getting dubious ownership errors
   - Use the correct branch (multi-agent) for enhanced functionality
   - Initialize git before adding remote if directory not empty

2. **Package Dependencies**:
   - Install Google packages before other dependencies
   - Use --no-cache-dir when encountering installation issues
   - Install packages in correct order to avoid conflicts

3. **Python Environment**:
   - Create __init__.py in tools directory for proper package recognition
   - Set PYTHONPATH when running modules directly
   - Use full module path (e.g., python -m tools.llm_api) instead of direct script execution

4. **PowerShell Specifics**:
   - Use PowerShell-specific syntax for environment variables
   - Avoid Unix-style command chaining
   - Use proper path separators

5. **API Integration**:
   - Test each API provider separately
   - Verify API keys are properly loaded from .env
   - Use default models unless specifically needed otherwise 