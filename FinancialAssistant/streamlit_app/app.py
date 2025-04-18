import streamlit as st
import uuid
from classes.config import Config
from methods.util import get_llm
from graph.work_flow import create_workflow
from typing import Any
from pydantic import SecretStr
from methods.memory_manager import MemoryManager
from consts.consts import (
    STATE_MESSAGES, STATE_SELECTED_PROVIDER, STATE_CONFIG,
    PROVIDER_GROQ, PROVIDER_OPENAI, PROVIDER_ANTHROPIC,
    MSG_API_KEYS_SAVED, MSG_ENTER_BOTH_KEYS, MSG_CONFIGURE_API,
    LABEL_API_CONFIG, LABEL_SELECT_PROVIDER, LABEL_API_KEY, LABEL_FMP_API_KEY, LABEL_SAVE_KEYS,
    KEY_REQUEST, KEY_FMP_API_KEY, KEY_ERROR, KEY_REPORT_MD,
    KEY_ROLE, KEY_CONTENT, ROLE_USER, ROLE_ASSISTANT
)

def initialize_session_state():
    if STATE_MESSAGES not in st.session_state:
        st.session_state.messages = []
    if STATE_SELECTED_PROVIDER not in st.session_state:
        st.session_state.selected_provider = None
    if STATE_CONFIG not in st.session_state:
        st.session_state.config = None
    if 'user_id' not in st.session_state:
        # Generate a unique user ID for this session
        st.session_state.user_id = str(uuid.uuid4())
    if 'memory_manager' not in st.session_state:

        st.session_state.memory_manager = MemoryManager()

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
        # Reset the config when provider changes
        st.session_state.config = None

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

    # Otherwise, show the API key input UI
    st.sidebar.header(LABEL_API_CONFIG)
    st.sidebar.markdown("""### API keys are stored only in session state of this Streamlit app. \n You can see the code of this app
                        [here](https://github.com/agdev/Langgraph/tree/main/FinancialAssistant).
                        Financial Modeling Prep API key you can get it [here](https://financialmodelingprep.com/developer/docs/).
                        """)

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

def get_graph_response(compiled_graph: Any, prompt: str, fmp_api_key: SecretStr, thread_id: int, user_id: str):
    result = compiled_graph.invoke({
        KEY_REQUEST: prompt,
        "user_id": user_id  # Pass the user_id in the state
    }, config={"configurable": {
        "thread_id": str(thread_id),
        "user_id": user_id,  # Also pass the user_id in the config
        KEY_FMP_API_KEY: fmp_api_key,
    }})

    return result['final_answer']

# import debugpy
def main():

    try:
        # debugpy.configure(python=3.11)  # Adjust the Python version as needed
        # debugpy.listen(("localhost", 5679))  # Use a different port if 5678 is in use
        # debugpy.wait_for_client()  # This will pause execution until the debugger attaches


        st.title("Financial Data Assistant")

        # Initialize session state
        initialize_session_state()

        # Setup API keys section
        set_api_keys()

        # Chat interface
        if st.session_state.config:
            if 'compiled_graph' not in st.session_state:
                llm = get_llm(st.session_state.config)
                compiled_graph = create_workflow(llm)
                st.session_state.compiled_graph = compiled_graph
                st.session_state.thread_id = 1
            else:
                st.session_state.thread_id = st.session_state.thread_id + 1

            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message[KEY_ROLE]):
                    st.markdown(message[KEY_CONTENT])

            # Chat input
            if prompt := st.chat_input("Enter your financial data request"):
                # Add user message to chat history
                st.session_state.messages.append({
                    KEY_ROLE: ROLE_USER,
                    KEY_CONTENT: prompt
                })

                # Display user message
                with st.chat_message(ROLE_USER):
                    st.markdown(prompt)

                # Get and display assistant response
                with st.chat_message(ROLE_ASSISTANT):
                    response = get_graph_response(
                        st.session_state.compiled_graph,
                        prompt,
                        st.session_state.config.fmp_api_key,
                        st.session_state.thread_id,
                        st.session_state.user_id
                    )
                    st.markdown(response)
                    st.session_state.messages.append({
                        KEY_ROLE: ROLE_ASSISTANT,
                        KEY_CONTENT: response
                    })
        else:
            st.info(MSG_CONFIGURE_API)
    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
