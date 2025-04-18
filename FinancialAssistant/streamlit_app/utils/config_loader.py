"""
Configuration loader for API keys in the Financial Assistant application.
Loads API keys from .env files if they exist.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import SecretStr
from classes.config import Config

def load_environment_variables():
    """
    Load environment variables from .env files in multiple possible locations.
    Returns a dictionary with the loaded configuration.
    """
    # Define possible .env file locations in order of preference
    possible_env_paths = [
        os.path.join( os.getcwd(),"streamlit_app","env", ".env"),                # Local to streamlit_app
        os.path.join( os.getcwd(),"env",".env"),                # Local to streamlit_app
        os.path.join( os.getcwd(),"..","env",".env"),             # One level up
        os.path.join( os.getcwd(), ".env")            # User's home directory
    ]
    
    # Try to load from each location
    for env_path in possible_env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"Loaded environment variables from {env_path}")
            # Return a config dictionary with the keys we're interested in
            return {
                # LLM provider API keys
                "GROQ_API_KEY": os.environ.get("GROQ_API_KEY"),
                "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
                "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
                # Financial Modeling Prep API key (used across all providers)
                "FINANCIAL_MODELING_PREP_API_KEY": os.environ.get("FINANCIAL_MODELING_PREP_API_KEY"),
            }            
            
        print(f"Could not find .env file at {env_path}")
    return {}
    

def create_config_from_env(provider="Groq"):
    """
    Create a Config object from environment variables.
    Returns None if required keys are not found.
    
    Args:
        provider: The LLM provider to use (default: "Groq")
        
    Returns:
        Config object if keys are found, None otherwise
    """
    env_vars = load_environment_variables()
    
    # Get the FMP API key (required for all providers)
    fmp_api_key = env_vars.get("FINANCIAL_MODELING_PREP_API_KEY")
    if not fmp_api_key:
        return None  # FMP API key is required for all providers
    
    # Get the appropriate LLM API key based on the provider
    llm_api_key = None
    if provider == "Groq":
        llm_api_key = env_vars.get("GROQ_API_KEY")
    elif provider == "OpenAI":
        llm_api_key = env_vars.get("OPENAI_API_KEY")
    elif provider == "Anthropic":
        llm_api_key = env_vars.get("ANTHROPIC_API_KEY")
    
    # Create and return the Config object if both keys are available
    if llm_api_key:
        return Config(
            llm_api_key=SecretStr(llm_api_key),
            fmp_api_key=SecretStr(fmp_api_key),
            provider=provider
        )
    
    return None
