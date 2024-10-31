import streamlit as st
from chain.extraction_chain import get_extraction_chain
from classes.config import Config
from methods.util import get_llm
from graph.work_flow import compiled_graph
from typing import Any
import os

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = None
    if "config" not in st.session_state:
        st.session_state.config = None

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
            config = Config(llm_api_key, fmp_api_key, provider)
            st.session_state.config= config
            st.sidebar.success("API keys saved successfully!")
        else:
            st.sidebar.error("Please enter both API keys")

def get_graph_response(prompt: str, extraction_chain: Any, fmp_api_key: str):

    result = compiled_graph.invoke({'request': prompt, 'extraction_chain': extraction_chain, 'fmp_api_key': fmp_api_key})
    return result['report_md']

def main():
    st.title("Financial Data Assistant")
    
    # Initialize session state
    initialize_session_state()
    
    # Setup API keys section
    set_api_keys()
    
    # Chat interface
    if st.session_state.config:
        if 'extraction_chain' not in st.session_state:
            llm = get_llm(st.session_state.config)
            extraction_chain = get_extraction_chain(llm)
            st.session_state.extraction_chain = extraction_chain
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
                stream = get_graph_response(
                    prompt,
                    st.session_state.extraction_chain,
                    st.session_state.config.fmp_api_key
                )
                response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.info("Please configure your API keys in the sidebar to start chatting.")

if __name__ == "__main__":
    main()
