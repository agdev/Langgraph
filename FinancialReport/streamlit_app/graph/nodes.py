from graph.graph_state import GraphState
from classes.income_statement import IncomeStatement, get_income_statement
from classes.company_financials import CompanyFinancials, get_company_financials
from classes.stock_price import StockPrice, get_stock_price
from methods.consts import UNKNOWN
from methods.generate_report import generate_markdown_report
from chain.extraction_chain import Extraction
from typing import TypedDict

def extraction_node(state: GraphState):
  """
  Extracts the symbol from the request using the extraction chain.
  """
  print('extraction_node')
  print('State', state)
  symbol  = UNKNOWN
  try:
    chain = state['extraction_chain']
    if chain is None:
      raise Exception('Extraction chain is not initialized')
      
    result: Extraction = chain.invoke(state['request'])
    # result: Extraction = extraction_chain_p.invoke(state['request'])
    symbol = result.symbol
  except Exception as e:
    print('Error:', e)
    

  # print('Symbol:', state['symbol'])
  return {'symbol': symbol}

def get_income_statement_node(state: GraphState):
  """
  Fetches the income statement for the given symbol.
  """
  print('get_income_statement_node')
  print('Symbol:', state['symbol'])
  result: IncomeStatement = get_income_statement(state['symbol'], state['fmp_api_key'])
  return {'income_statement': result}

def get_company_financials_node(state: GraphState):
  """
  Fetches the company financials for the given symbol.
  """
  print('get_company_financials_node')
  print('Symbol:', state['symbol'])
  result: CompanyFinancials = get_company_financials(state['symbol'], state['fmp_api_key'])
  return {'company_financials': result}

def get_stock_price_node(state: GraphState):
  """
  Fetches the stock price for the given symbol.
  """
  print('get_stock_price_node')
  print('Symbol:', state['symbol'])
  result: StockPrice = get_stock_price(state['symbol'], state['fmp_api_key'])
  return {'stock_price': result}

def error_node(state: GraphState):
  """
  Returns an error message if the symbol is unknown.
  """
  return {'error':f"""
  Unknown Symbol: {state['symbol']}
  Can not produce report for this symbol.
  """}

def generate_markdown_report_node(state: GraphState):
    """
    Generates a markdown report from the GraphState instance.
    """
    company_financials = state['company_financials'] if 'company_financials' in state else None
    income_statement = state['income_statement'] if ('income_statement' in state) else None
    stock_price = state['stock_price'] if ('stock_price' in state) else None
    md_report = generate_markdown_report(company_financials=company_financials, income_statement=income_statement, stock_price=stock_price)
    # file_name = f"{state['symbol']}_financial_report.md"
    # save_md_report_to_file(md_report, filename= file_name)
    # state['report_md'] = md_report
    return {'report_md': md_report}

def is_there_symbol(state: GraphState):
  """ 
  Checks if the symbol is unknown.
  """
  print('is_there_symbol')
  print('State', state)
  if state['symbol']  == UNKNOWN:
    print('Symbol:', UNKNOWN)
    return False

  return True
