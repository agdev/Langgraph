# API Key Configuration Loader Plan

## Overview

This plan outlines the implementation of a configuration loader for API keys in the Financial Assistant application. The goal is to load API keys from a `.env` file if they exist, eliminating the need to prompt users for keys that are already configured.

## Current State

- The app currently has a `.env` file that contains API keys
- The keys include `GROQ_API_KEY` and `FINANCIAL_MODELING_PREP_API_KEY`
- Currently, these keys are not being loaded from the `.env` file
- Users are always prompted to enter these keys, even if they exist in the `.env` file
- The app uses a `Config` class to store API keys and provider information
- The `set_api_keys()` function handles the UI for entering and saving API keys

## Implementation Plan

### 1. Create a Configuration Loader Module

Create a utility module to handle loading environment variables from the `.env` file:

```python
# FinancialAssistant/streamlit_app/utils/config_loader.py
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
        Path("env/.env"),                # Local to streamlit_app
        Path("../env/.env"),             # One level up
        Path.home() / ".env",            # User's home directory
    ]

    # Try to load from each location
    for env_path in possible_env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            print(f"Loaded environment variables from {env_path}")
            break

    # Return a config dictionary with the keys we're interested in
    return {
        # LLM provider API keys
        "GROQ_API_KEY": os.environ.get("GROQ_API_KEY"),
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
        # Financial Modeling Prep API key (used across all providers)
        "FINANCIAL_MODELING_PREP_API_KEY": os.environ.get("FINANCIAL_MODELING_PREP_API_KEY"),
    }

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
```

### 2. Integrate with Existing `set_api_keys()` Function

Modify the existing `set_api_keys()` function to first try loading keys from the `.env` file:

```python
def set_api_keys():
    # Get the currently selected provider from the selectbox
    provider = st.sidebar.selectbox(
        LABEL_SELECT_PROVIDER,
        [PROVIDER_GROQ, PROVIDER_OPENAI, PROVIDER_ANTHROPIC],
        key="provider_select"
    )

    # Check if provider has changed
    provider_changed = False
    if STATE_SELECTED_PROVIDER in st.session_state and st.session_state.selected_provider != provider:
        provider_changed = True
        # Reset the compiled graph when provider changes
        if 'compiled_graph' in st.session_state:
            del st.session_state.compiled_graph

    # Update the selected provider
    st.session_state.selected_provider = provider

    # If config is already set and provider hasn't changed, don't do anything else
    if st.session_state.config is not None and not provider_changed:
        return

    # Try to load config from environment variables for the selected provider
    from utils.config_loader import create_config_from_env
    env_config = create_config_from_env(provider)

    # If config was loaded from environment, set it and return
    if env_config is not None:
        # Set the config
        st.session_state.config = env_config

        # Reset the compiled graph to force recompilation with the new provider
        if 'compiled_graph' in st.session_state:
            del st.session_state.compiled_graph

        st.sidebar.success(f"API keys for {provider} loaded from environment variables")
        return

    # Otherwise, show the API key input UI as before
    st.sidebar.header(LABEL_API_CONFIG)
    st.sidebar.markdown("""### API keys are stored only in session state of this Streamlit app. \n You can see the code of this app
                        [here](https://github.com/agdev/Langgraph/tree/main/FinancialAssistant).
                        Financial Modeling Prep API key you can get it [here](https://financialmodelingprep.com/developer/docs/).
                        """)

    provider = st.sidebar.selectbox(
        LABEL_SELECT_PROVIDER,
        [PROVIDER_GROQ, PROVIDER_OPENAI, PROVIDER_ANTHROPIC],
        key="provider_select"
    )

    llm_api_key = st.sidebar.text_input(
        f"{provider} {LABEL_API_KEY}",
        type="password",
        key="llm_api_key"
    )

    fmp_api_key = st.sidebar.text_input(
        LABEL_FMP_API_KEY,
        type="password",
        key="fmp_api_key"
    )

    if st.sidebar.button(LABEL_SAVE_KEYS):
        if llm_api_key and fmp_api_key:
            config = Config(SecretStr(llm_api_key), SecretStr(fmp_api_key), provider)
            st.session_state.config = config

            # Reset the compiled graph to force recompilation with the new provider
            if 'compiled_graph' in st.session_state:
                del st.session_state.compiled_graph

            st.sidebar.success(MSG_API_KEYS_SAVED)
        else:
            st.sidebar.error(MSG_ENTER_BOTH_KEYS)
```

### 3. Add python-dotenv to Dependencies

Add the `python-dotenv` package to the project dependencies in `pyproject.toml`:

```toml
[project]
dependencies = [
    "streamlit",
    "langchain",
    "langgraph>=0.3.0",
    "langchain-anthropic",
    "langchain-groq",
    "langchain-openai",
    "langchain-core",
    "python-dotenv",  # Added for .env file support
]
```

### 4. Create a Template .env File

Create a template `.env` file that users can copy:

```
# FinancialAssistant/streamlit_app/env/.env.template
# API Keys for different LLM providers
# You only need to set the API key for the provider you want to use
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Financial Modeling Prep API key (required for all providers)
FINANCIAL_MODELING_PREP_API_KEY=your_fmp_api_key_here
```

### 5. Update Documentation

Add instructions in the README about setting up the `.env` file:

```markdown
## Configuration

You can configure API keys in two ways:

1. **Environment Variables**: Create a `.env` file in the `env/` directory with your API keys:
   ```
   # API Keys for different LLM providers
   # You only need to set the API key for the provider you want to use
   GROQ_API_KEY=your_groq_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here

   # Financial Modeling Prep API key (required for all providers)
   FINANCIAL_MODELING_PREP_API_KEY=your_fmp_api_key_here
   ```

   The application will try to use the API keys in the following order of preference: Groq, OpenAI, Anthropic.

2. **In-App Configuration**: If no `.env` file is found, you'll be prompted to enter your API keys when you launch the app.
```

## Testing Plan

1. Test with no `.env` file to ensure the app still prompts for API keys
2. Test with a `.env` file containing only one key to ensure it loads that key and prompts for the other
3. Test with a `.env` file containing both keys to ensure it loads both keys and doesn't prompt the user
4. Test with invalid API keys to ensure the app handles errors gracefully

## Dependencies

- `python-dotenv` package for loading `.env` files
- Streamlit for the UI components
