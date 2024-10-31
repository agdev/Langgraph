from classes.config import Config
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from typing import Any
from methods.consts import (
    PROVIDER_OPENAI, PROVIDER_GROQ, PROVIDER_ANTHROPIC,
    MODEL_OPENAI, MODEL_GROQ, MODEL_ANTHROPIC
)

def get_llm(config: Config)-> Any:
    """
    Get the LLM based on the provider and API key.
    Supported providers: "Groq", "OpenAI", "Anthropic"
    """
    if config.provider == PROVIDER_OPENAI:
        return ChatOpenAI(api_key=config.llm_api_key, model=MODEL_OPENAI)
    elif config.provider == PROVIDER_GROQ:
        return ChatGroq(api_key=config.llm_api_key, model=MODEL_GROQ,
                        temperature=0,
                        max_tokens=None,
                        timeout=None,
                        max_retries=2,)
    elif config.provider == PROVIDER_ANTHROPIC:
        return ChatAnthropic(api_key=config.llm_api_key, model_name=MODEL_ANTHROPIC, temperature=0.0)
    
    raise ValueError(f"Unsupported provider: {config.provider}")
