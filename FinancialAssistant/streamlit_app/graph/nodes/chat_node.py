"""
Chat node for the Financial Assistant application.
"""

from langchain_core.runnables.config import RunnableConfig
from langgraph.store.base import BaseStore
from graph.state.graph_state import GraphState
from graph.state.internal_state import InternalState
from chains.chat_chain import ChatResult, create_chat_chain
from consts.consts import KEY_REQUEST, KEY_CHAT_RESPONSE
from methods.util import get_memory_manager, get_user_id

def create_chat_node(llm):
  print('create_chain_node')
  chain = create_chat_chain(llm)
  def chat_node(state: GraphState, config: RunnableConfig, store: BaseStore)->InternalState:
      """
      Generates a response from llm per user request/prompt.
      """
      mem_store = get_memory_manager(store)
      # Get the user ID from the config if available
      user_id = get_user_id(config)

      # Get conversation summary using the store parameter
      summary = mem_store.get_conversation_summary(user_id) or ""

      # Pass the summary as a separate property
      result: ChatResult = chain.invoke({
          "request": state.get(KEY_REQUEST),
          "conversation_summary": summary
      })

      return {KEY_CHAT_RESPONSE: result.response}
  return chat_node
