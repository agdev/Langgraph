from graph.graph_state import GraphState
from chains.route_chain import RouterResult, create_route_chain
from chains.extraction_chain import Extraction, create_extraction_chain
from chains.chat_chain import ChatResult, create_chat_chain
from classes.income_statement import IncomeStatement, get_income_statement
from classes.company_financials import CompanyFinancials, get_company_financials
from classes.stock_price import StockPrice, get_stock_price
from methods.generate_methods import generate_markdown_report, generate_markdown_financials, generate_markdown_income_statement, generate_markdown_stock_price
from consts.consts import (
    UNKNOWN, KEY_SYMBOL, KEY_REQUEST,
    KEY_FMP_API_KEY, KEY_ERROR, KEY_REPORT_MD,
    KEY_COMPANY_FINANCIALS, KEY_INCOME_STATEMENT, KEY_STOCK_PRICE,
    KEY_REQUEST_CATEGORY, KEY_CHAT_RESPONSE, KEY_FINAL_ANSWER
)
from methods.generate_methods import generate_markdown_report
from chains.extraction_chain import Extraction

def create_get_route_node(llm):
  print('create_get_route_node')
  chain = create_route_chain(llm)

  def get_route_node(state: GraphState):
    print('router_node')
    print('State', state)
    result: RouterResult = chain.invoke({"request": state['request']})
    print('request_category:', result.route)
    return {KEY_REQUEST_CATEGORY:result.route}
  return get_route_node

def create_symbol_extraction_node(llm):
  print('create_symbol_extraction_node')
  chain = create_extraction_chain(llm)
  def symbol_extraction_node(state: GraphState):
    print('symbol_extraction_node')
    print('State', state)
    symbol  = UNKNOWN
    try:
      
      result: Extraction = chain.invoke(state['request'])
      symbol = result.symbol
    except Exception as e:
      print('Error:', e)

    # print('Symbol:', state['symbol'])
    return {KEY_SYMBOL: symbol}
  return symbol_extraction_node

def get_income_statement_node(state: GraphState):
  print('get_income_statement_node')
  print('Symbol:', state[KEY_SYMBOL])
  income_statement: IncomeStatement = get_income_statement(state[KEY_SYMBOL], state[KEY_FMP_API_KEY])
  result = generate_markdown_income_statement(income_statement)
  return {KEY_INCOME_STATEMENT: result}

def get_company_financials_node(state: GraphState):
  print('get_company_financials_node')
  print('Symbol:', state[KEY_SYMBOL])
  info: CompanyFinancials = get_company_financials(state[KEY_SYMBOL], state[KEY_FMP_API_KEY])
  result = generate_markdown_financials(info)
  return {KEY_COMPANY_FINANCIALS: result}

def get_stock_price_node(state: GraphState):
  print('get_stock_price_node')
  print('Symbol:', state[KEY_SYMBOL])
  stock_price: StockPrice = get_stock_price(state[KEY_SYMBOL], state[KEY_FMP_API_KEY])
  result = generate_markdown_stock_price(stock_price)
  return {KEY_STOCK_PRICE: result}

def error_node(state: GraphState):
    """
    Returns an error message if the symbol is unknown.
    """
    return {KEY_ERROR: f"""
    Unknown Symbol: {state[KEY_SYMBOL]}
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
    if state[KEY_SYMBOL].upper() == UNKNOWN:
        print('Symbol:', UNKNOWN)
        return False

    return True

def create_chat_node(llm):
  print('create_chain_node')
  chain = create_chat_chain(llm)
  def chat_node(state: GraphState):
      """
      Generates a response from llm per user request/prompt.
      """
      # chain = state['chat_chain']
      # if chain is None:
      #   raise Exception('Extraction chain is not initialized')

      result: ChatResult = chain.invoke({"request": state[KEY_REQUEST]})
      return {KEY_CHAT_RESPONSE: result.response}
  return chat_node

def where_to(state: GraphState):
    """Determines which path to take based on the request category."""
    if state[KEY_REQUEST_CATEGORY] == 'report':
        return 'report'
    elif state[KEY_REQUEST_CATEGORY] == 'chat':
        return 'chat'
    return 'alone'

def where_to_alone(state: GraphState):
    """Determines which standalone node to use."""
    if state[KEY_SYMBOL].upper() == UNKNOWN:
        return 'error'
    return state[KEY_REQUEST_CATEGORY]

def final_answer_node(state: GraphState):
    """Generates the final answer based on the request category."""
    if state[KEY_REQUEST_CATEGORY] == 'income_statement':
        if KEY_ERROR in state:
            result = state[KEY_ERROR]
        else:
            result = state[KEY_INCOME_STATEMENT]
            result = f"# Income statement for ({state[KEY_SYMBOL]}) \n" + result
    elif state[KEY_REQUEST_CATEGORY] == 'company_financials':
        if KEY_ERROR in state:
            result = state[KEY_ERROR]
        else:
            result = state[KEY_COMPANY_FINANCIALS]
            result = f"# Company financials for ({state[KEY_SYMBOL]}) \n" + result
    elif state[KEY_REQUEST_CATEGORY] == 'stock_price':
        if KEY_ERROR in state:
            result = state[KEY_ERROR]
        else:
            result = state[KEY_STOCK_PRICE]
            result = f"# Stock Price for ({state[KEY_SYMBOL]}) \n" + result
    elif state[KEY_REQUEST_CATEGORY] == 'chat':
        result = state[KEY_CHAT_RESPONSE]
    elif state[KEY_REQUEST_CATEGORY] == 'report':
        if KEY_REPORT_MD in state:
            result = state[KEY_REPORT_MD]
            result = f"# Report for ({state[KEY_SYMBOL]}) \n" + result
        elif KEY_ERROR in state:
            result = state[KEY_ERROR]
        else:
            result = "Can not provide an answer"
    else:
        result = "Can not provide an answer"

    return {KEY_FINAL_ANSWER: result}
