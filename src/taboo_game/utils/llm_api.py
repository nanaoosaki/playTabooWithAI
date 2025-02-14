"""
LLM API utility for the Taboo game.
"""

import os
from typing import Optional
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env files."""
    env_files = ['.env.local', '.env', '.env.example']
    env_loaded = False
    
    for env_file in env_files:
        if os.path.exists(env_file):
            load_dotenv(dotenv_path=env_file)
            env_loaded = True
            break
    
    if not env_loaded:
        raise EnvironmentError("No .env files found")

# Load environment variables on module import
load_environment()

def query_llm(prompt: str, provider: str = "anthropic", max_retries: int = 3) -> str:
    """
    Query an LLM provider with the given prompt.
    
    Args:
        prompt: The prompt to send to the LLM
        provider: The LLM provider to use ("anthropic", "openai", or "local")
        max_retries: Maximum number of retries on failure
    
    Returns:
        The LLM's response
    
    Raises:
        ValueError: If the provider is not supported
        RuntimeError: If the API call fails after max retries
    """
    for attempt in range(max_retries):
        try:
            if provider == "anthropic":
                return _query_anthropic(prompt)
            elif provider == "openai":
                return _query_openai(prompt)
            elif provider == "local":
                return _query_local(prompt)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        except Exception as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"Failed to query LLM after {max_retries} attempts") from e
            continue

def _query_anthropic(prompt: str) -> str:
    """Query the Anthropic Claude API."""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    
    return response.content[0].text

def _query_openai(prompt: str) -> str:
    """Query the OpenAI API."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": prompt
        }],
        max_tokens=1024
    )
    
    return response.choices[0].message.content

def _query_local(prompt: str) -> str:
    """
    Query the local LLM (not implemented).
    This is a placeholder for future implementation of local LLM support.
    """
    raise NotImplementedError("Local LLM support not implemented yet") 