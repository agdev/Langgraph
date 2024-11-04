import sys
from typing import Any

def print_flush(*args: Any, **kwargs: Any) -> None:
    """Print and flush immediately."""
    print(*args, **kwargs)
    sys.stdout.flush()

try:
    print_flush("Testing imports...")
    
    # Core dependencies
    import streamlit
    print_flush("✓ streamlit")
    
    from langchain_core.prompts import ChatPromptTemplate
    print_flush("✓ langchain_core")
    
    from langgraph.graph import StateGraph
    print_flush("✓ langgraph")
    
    # LLM providers
    from langchain_anthropic import ChatAnthropic
    print_flush("✓ langchain_anthropic")
    
    from langchain_groq import ChatGroq
    print_flush("✓ langchain_groq")
    
    from langchain_openai import ChatOpenAI
    print_flush("✓ langchain_openai")

    from consts.consts import UNKNOWN
    print_flush("✓ methods.consts")

    print_flush("\nAll imports successful!")

except ImportError as e:
    print_flush(f"\n❌ Import Error: {str(e)}")
    print_flush("\nTry installing the missing package with:")
    print_flush(f"pip install {str(e).split()[-1]}") 