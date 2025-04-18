"""
Router node for the Financial Assistant application.
"""

from langchain_core.runnables.config import RunnableConfig
from langgraph.store.base import BaseStore
from graph.graph_state import GraphState
from chains.route_chain import RouterResult, create_route_chain
from consts.consts import KEY_REQUEST_CATEGORY
from methods.util import get_memory_manager, get_user_id

def create_get_route_node(llm):
  print('create_get_route_node')
  chain = create_route_chain(llm)

  def get_route_node(state: GraphState, config: RunnableConfig, store: BaseStore):
    print('router_node')
    print('State', state)

    mem_store = get_memory_manager(store)
    # Get the user ID from the config if available
    user_id = get_user_id(config)

    # Get conversation summary using the store parameter
    summary = mem_store.get_conversation_summary(user_id) or ""

    # Pass the summary as a separate property
    result: RouterResult = chain.invoke({
        "request": state.get('request'),
        "conversation_summary": summary
    })

    print('request_category:', result.route)
    return {KEY_REQUEST_CATEGORY:result.route}
  return get_route_node
