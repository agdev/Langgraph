"""
Summarization Node for Financial Assistant.

This module provides a node for summarizing conversations and updating memory
in the Financial Assistant workflow.
"""

from langgraph.store.base import BaseStore
from graph.graph_state import GraphState
from chains.summarization_chain import create_summarization_chain
from methods.memory_manager import MemoryManager
from langchain_core.runnables.config import RunnableConfig
from methods.util import get_memory_manager, get_user_id


def create_summarization_node(llm):
    """
    Creates a node for summarizing conversations and updating memory.
    This node should be placed right before the final answer node.

    Args:
        llm: The language model to use for summarization
        memory_manager: The memory manager instance (not used directly in the node)

    Returns:
        A function that takes state, config, and store and returns updated state
    """
    # Create the summarization chain
    summarization_chain = create_summarization_chain(llm)

    def summarization_node(state: GraphState, config: RunnableConfig, store: BaseStore):
        """
        Summarizes the conversation and updates the summary in the memory manager.

        Args:
            state: The current state of the graph
            config: The configuration for the runnable
            store: The store to use for memory operations (cast to MemoryManager)

        Returns:
            The unchanged state
        """
        # Get the user ID from the config if available
        user_id = get_user_id(config)
        mem_store = get_memory_manager(store)
        # Get existing summary using the store parameter
        existing_summary = mem_store.get_conversation_summary(user_id) or "No previous summary available."

        # Format the conversation for summarization
        request = state.get('request', 'No request')
        final_answer = state.get('final_answer', 'No answer')
        request_category = state.get('request_category', 'unknown')
        symbol = state.get('symbol', 'UNKNOWN')

        # Build a conversation string with metadata
        conversation = f"User: {request}\n"
        conversation += f"Request Type: {request_category.replace('_', ' ').title()}\n"

        # Add symbol information if available and relevant
        if symbol != 'UNKNOWN' and request_category != 'chat':
            conversation += f"Company Symbol: {symbol}\n"

        # Add the final answer which already contains all outputs
        conversation += f"Assistant: {final_answer}\n"

        # Prepare inputs for the summarization chain
        chain_inputs = {
            "existing_summary": existing_summary,
            "conversation": conversation
        }

        # Generate the summary
        result = summarization_chain.invoke(chain_inputs)
        summary = result.summary

        # Update the summary in memory using the store parameter
        mem_store.update_conversation_summary(user_id, summary)

        # If there's a symbol in the state, update the last symbol using the store parameter
        symbol = state.get("symbol")
        if symbol and symbol != "UNKNOWN":
            mem_store.update_last_symbol(user_id, symbol)

        # Return the state unchanged
        return state

    return summarization_node
