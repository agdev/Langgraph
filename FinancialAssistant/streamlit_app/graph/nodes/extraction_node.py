"""
Symbol extraction node for the Financial Assistant application.
"""

from langchain_core.runnables.config import RunnableConfig
from langgraph.store.base import BaseStore
from graph.state.graph_state import GraphState
from chains.extraction_chain import Extraction, create_extraction_chain
from methods.memory_manager import MemoryManager
from consts.consts import UNKNOWN, KEY_SYMBOL
from methods.util import get_memory_manager, get_user_id

def create_symbol_extraction_node(llm):
  print('create_symbol_extraction_node')
  chain = create_extraction_chain(llm)
  def symbol_extraction_node(state: GraphState, config: RunnableConfig, store: BaseStore):
    print('symbol_extraction_node')
    print('State', state)
    symbol = UNKNOWN
    try:
      result: Extraction = chain.invoke(state.get('request'))
      symbol = result.symbol
    except Exception as e:
      print('Error:', e)

    # If symbol is unknown, try to get the last used symbol
    if symbol == UNKNOWN:
      mem_store: MemoryManager = get_memory_manager(store)
      # Get the user ID from the config if available
      user_id = get_user_id(config)
      # Use the store parameter to get the last symbol
      last_symbol = mem_store.get_last_symbol(user_id)
      if last_symbol:
        print(f"Using last symbol: {last_symbol}")
        symbol = last_symbol

    return {KEY_SYMBOL: symbol}
  return symbol_extraction_node
