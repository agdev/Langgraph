from langchain_core.runnables.config import RunnableConfig
from langgraph.store.base import BaseStore
from graph.graph_state import GraphState
from chains.route_chain import RouterResult, create_route_chain
from chains.extraction_chain import Extraction, create_extraction_chain
from chains.chat_chain import ChatResult, create_chat_chain
from classes.income_statement import IncomeStatement, get_income_statement
from classes.company_financials import CompanyFinancials, get_company_financials
from classes.stock_price import StockPrice, get_stock_price
from methods.memory_manager import MemoryManager
from methods.generate_methods import generate_markdown_report, generate_markdown_financials, generate_markdown_income_statement, generate_markdown_stock_price
from consts.consts import (
    UNKNOWN, KEY_SYMBOL, KEY_REQUEST,
    KEY_FMP_API_KEY, KEY_ERROR, KEY_REPORT_MD,
    KEY_COMPANY_FINANCIALS, KEY_INCOME_STATEMENT, KEY_STOCK_PRICE,
    KEY_REQUEST_CATEGORY, KEY_CHAT_RESPONSE, KEY_FINAL_ANSWER
)
from methods.generate_methods import generate_markdown_report
from chains.extraction_chain import Extraction
from methods.util import get_fmp_api_key, get_memory_manager, get_user_id

# def dummy_node(state: GraphState, config: RunnableConfig, store: MemoryManager):
#     return state

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

def get_income_statement_node(state: GraphState, config: RunnableConfig):
  symbol = state.get(KEY_SYMBOL, UNKNOWN)
  print('get_income_statement_node')
  print('Symbol:', symbol)
  income_statement: IncomeStatement | None = get_income_statement(symbol, get_fmp_api_key(config))
  if income_statement is None:
    return {KEY_INCOME_STATEMENT: None}
  result = generate_markdown_income_statement(income_statement)
  return {KEY_INCOME_STATEMENT: result}

def get_company_financials_node(state: GraphState, config: RunnableConfig):
  symbol = state.get(KEY_SYMBOL, UNKNOWN)
  print('get_company_financials_node')
  print('Symbol:', symbol)
  info: CompanyFinancials | None= get_company_financials(symbol, get_fmp_api_key(config))
  if info is None:
    return {KEY_COMPANY_FINANCIALS: None}
  result = generate_markdown_financials(info)
  return {KEY_COMPANY_FINANCIALS: result}

def get_stock_price_node(state: GraphState, config: RunnableConfig):
  symbol = state.get(KEY_SYMBOL, UNKNOWN)
  print('get_stock_price_node')
  print('Symbol:', symbol)
  stock_price: StockPrice | None= get_stock_price(symbol, get_fmp_api_key(config))
  if stock_price is None:
    return {KEY_STOCK_PRICE: None}
  result = generate_markdown_stock_price(stock_price)
  return {KEY_STOCK_PRICE: result}

def error_node(state: GraphState):
    """
    Returns an error message if the symbol is unknown.
    """
    return {KEY_ERROR: f"""
    Unknown Symbol: {state.get(KEY_SYMBOL)}
    Can not produce report for this symbol.
    """}

def generate_markdown_report_node(state: GraphState):
    """
    Generates a markdown report from the GraphState instance.
    """
    print('generate_markdown_report_node')
    company_financials = state[KEY_COMPANY_FINANCIALS] if KEY_COMPANY_FINANCIALS in state else None
    income_statement = state[KEY_INCOME_STATEMENT] if KEY_INCOME_STATEMENT in state else None
    stock_price = state[KEY_STOCK_PRICE] if KEY_STOCK_PRICE in state else None
    md_report = generate_markdown_report(
        company_financials=company_financials,
        income_statement=income_statement,
        stock_price=stock_price
    )
    return {KEY_REPORT_MD: md_report}

def is_there_symbol(state: GraphState):
    """
    Checks if the symbol is unknown.
    """
    print('is_there_symbol')
    print('State', state)
    symbol = state.get(KEY_SYMBOL, UNKNOWN)
    if symbol.upper() == UNKNOWN:
        print('Symbol:', UNKNOWN)
        return False

    return True

def create_chat_node(llm):
  print('create_chain_node')
  chain = create_chat_chain(llm)
  def chat_node(state: GraphState, config: RunnableConfig, store: BaseStore):
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

def where_to(state: GraphState):
    """Determines which path to take based on the request category."""
    category = state.get(KEY_REQUEST_CATEGORY)
    if category == 'report':
        return 'report'
    elif category == 'chat':
        return 'chat'
    return 'alone'

def where_to_alone(state: GraphState):
    """Determines which standalone node to use."""
    symbol = state.get(KEY_SYMBOL, UNKNOWN)
    if symbol.upper() == UNKNOWN:
        return 'error'
    return state.get(KEY_REQUEST_CATEGORY)

def final_answer_node(state: GraphState):
    """Generates the final answer based on the request category."""
    category = state.get(KEY_REQUEST_CATEGORY)
    if category == 'income_statement':
        if KEY_ERROR in state:
            result = state[KEY_ERROR]
        else:
            result_data = state.get(KEY_INCOME_STATEMENT) or ""
            symbol: str = state.get(KEY_SYMBOL) or UNKNOWN
            result = f"# Income statement for ({symbol}) \n" + result_data
    elif category == 'company_financials':
        if KEY_ERROR in state:
            result = state[KEY_ERROR]
        else:
            result_data = state.get(KEY_COMPANY_FINANCIALS) or ""
            symbol: str = state.get(KEY_SYMBOL) or UNKNOWN
            result = f"# Company financials for ({symbol}) \n" + result_data
    elif category == 'stock_price':
        if KEY_ERROR in state:
            result = state[KEY_ERROR]
        else:
            result_data = state.get(KEY_STOCK_PRICE) or ""
            symbol: str = state.get(KEY_SYMBOL) or UNKNOWN
            result = f"# Stock Price for ({symbol}) \n" + result_data
    elif category == 'chat':
        result = state.get(KEY_CHAT_RESPONSE) or "No response available"
    elif category == 'report':
        if KEY_REPORT_MD in state:
            result_data = state.get(KEY_REPORT_MD) or ""
            symbol: str = state.get(KEY_SYMBOL) or UNKNOWN
            result = f"# Report for ({symbol}) \n" + result_data
        elif KEY_ERROR in state:
            result = state[KEY_ERROR]
        else:
            result = "Can not provide an answer"
    else:
        result = "Can not provide an answer"

    return {KEY_FINAL_ANSWER: result}
