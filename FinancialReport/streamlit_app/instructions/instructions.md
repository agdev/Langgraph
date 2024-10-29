# Project overview
You are building agentic systme of financial data retrieval. 
There are 3 agents and graph with associated nodes and classes that are already implemented in langgraph.ipynb 
user should be able to select various  LLM Providers and provide API keys for these providers for APIs used in the code the back end. The app is using streamlit.

You will be using Langgraph, Langchain and Streamlit.

# Core functionalities
1 User should be prompted to select one of the following LLM Providers:
    - OpenAI
    - Groq
    - Anthropic

and enter Api Key. Api key should be store in streamlit's session 
User needs tp enter API key for Financial Modeling Prep API.
2. user need to be able to enter its request for data. User's request is parameter for the graph 
# Documentation
## Documentation for streamlit app how to:
1. initialize session state
2. setup api keys
3. display chat history
4. display user message
5. get and display assistant response
## CODE EXAMPLE:
```
import streamlit as st
from openai import OpenAI
from anthropic import Anthropic
import os

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = None
    if "api_keys_set" not in st.session_state:
        st.session_state.api_keys_set = False

def set_api_keys():
    # API Key input section
    st.sidebar.header("API Configuration")
    
    # LLM Provider selection
    provider = st.sidebar.selectbox(
        "Select LLM Provider",
        ["OpenAI", "Groq", "Anthropic"],
        key="provider_select"
    )
    
    # API Key input
    llm_api_key = st.sidebar.text_input(
        f"{provider} API Key",
        type="password",
        key="llm_api_key"
    )
    
    fmp_api_key = st.sidebar.text_input(
        "Financial Modeling Prep API Key",
        type="password",
        key="fmp_api_key"
    )
    
    if st.sidebar.button("Save API Keys"):
        if llm_api_key and fmp_api_key:
            # Store API keys in session state
            st.session_state.llm_api_key = llm_api_key
            st.session_state.fmp_api_key = fmp_api_key
            st.session_state.selected_provider = provider
            st.session_state.api_keys_set = True
            st.sidebar.success("API keys saved successfully!")
        else:
            st.sidebar.error("Please enter both API keys")

def get_llm_response(prompt, provider, api_key):
    if provider == "OpenAI":
       # implement OpenAI provider
        return response
    elif provider == "Anthropic":
        # implement Anthropic provider
        return response
    elif provider == "Groq":
        # implement Groq provider
        return response
    # Add other provider implementations as needed
    return None

def main():
    st.title("Financial Data Assistant")
    
    # Initialize session state
    initialize_session_state()
    
    # Setup API keys section
    set_api_keys()
    
    # Chat interface
    if st.session_state.api_keys_set:
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Enter your financial data request"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get and display assistant response
            with st.chat_message("assistant"):
                stream = get_llm_response(
                    prompt,
                    st.session_state.selected_provider,
                    st.session_state.llm_api_key
                )
                response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.info("Please configure your API keys in the sidebar to start chatting.")

if __name__ == "__main__":
    main()
```

# Current File Structure
FinancialReport
├── notebook
│   ├── langgraph.ipynb
│   └── notebook_with_graph.pdf
├── Pipfile
├── Pipfile.lock
├── README.MD
└── streamlit_app
    ├── chain
    ├── graph
    ├── instructions
    │   └── instructions.md
    └── streamlit_test.py