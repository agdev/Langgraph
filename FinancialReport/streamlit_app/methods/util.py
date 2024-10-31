from classes.config import Config
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from typing import Any

def get_llm(config: Config)-> Any:
    if config.provider == "openai":
        return ChatOpenAI(api_key=config.llm_api_key, model="gpt-4o-mini")
    elif config.provider == "groq":
        return ChatGroq(api_key=config.llm_api_key, model="mixtral-8x7b-32768",
                        temperature=0,
                        max_tokens=None,
                        timeout=None,
                        max_retries=2,)
    elif config.provider == "anthropic":
        return ChatAnthropic(api_key=config.llm_api_key, model_name='claude-3-sonnet-20240229', temperature=0.0)
    
    raise ValueError(f"Unsupported provider: {config.provider}")
