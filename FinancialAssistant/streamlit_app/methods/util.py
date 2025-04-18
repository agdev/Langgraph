from langchain_core.runnables.config import RunnableConfig
from pydantic import SecretStr
from classes.config import Config
from langchain_core.runnables.config import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from typing import Any, Union
from consts.consts import (
    KEY_FMP_API_KEY, PROVIDER_OPENAI, PROVIDER_GROQ, PROVIDER_ANTHROPIC,
    MODEL_OPENAI, MODEL_GROQ, MODEL_ANTHROPIC
)

# Define KEY_CONFIG constant
KEY_CONFIG = "configurable"
from langgraph.store.base import BaseStore
from methods.memory_manager import MemoryManager

def get_llm(config: Config)-> Any:
    """
    Get the LLM based on the provider and API key.
    Supported providers: "Groq", "OpenAI", "Anthropic"
    """
    # The api_key is already a SecretStr, so we can pass it directly
    if config.provider == PROVIDER_OPENAI:
        return ChatOpenAI(api_key=config.llm_api_key, model=MODEL_OPENAI)
    elif config.provider == PROVIDER_GROQ:
        return ChatGroq(api_key=config.llm_api_key, model=MODEL_GROQ,
                        temperature=0,
                        max_tokens=None,
                        timeout=None,
                        max_retries=2,)
    elif config.provider == PROVIDER_ANTHROPIC:
        return ChatAnthropic(
            api_key=config.llm_api_key,
            model_name=MODEL_ANTHROPIC,
            temperature=0.0,
            timeout=None,
            max_retries=2,
            stop=None
        )


    raise ValueError(f"Unsupported provider: {config.provider}")

def get_memory_manager(store: BaseStore) -> MemoryManager:
  if isinstance(store, MemoryManager):
        mem_store: MemoryManager = store
  else:
      raise TypeError("Expected store to be an instance of MemoryManager")
  return mem_store


def get_fmp_api_key(config: RunnableConfig) -> SecretStr:
    """Get the FMP API key from the config."""
    return get_secret_key(config, KEY_FMP_API_KEY)

def get_user_id(config: RunnableConfig) -> str:
    """Get the user ID from the config."""
    return get_key(config, "user_id")

def get_key(config: RunnableConfig, key: str) ->  str:
    """Retrieve a key from the config."""
    if config is None or KEY_CONFIG not in config:
        raise ValueError(f"Config is missing or does not contain the key '{KEY_CONFIG}'")
    return config[KEY_CONFIG][key]


def get_secret_key(config: RunnableConfig, key: str) -> SecretStr :
    """Retrieve a key from the config."""
    if config is None or KEY_CONFIG not in config:
        raise ValueError(f"Config is missing or does not contain the key '{KEY_CONFIG}'")
    return config[KEY_CONFIG][key]



