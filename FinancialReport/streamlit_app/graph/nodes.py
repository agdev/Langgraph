from graph.graph_state import GraphState
from classes.income_statement import IncomeStatement
from classes.company_financials import CompanyFinancials
from classes.stock_price import StockPrice
from methods.consts import UNKNOWN
from methods.generate_report import generate_markdown_report

def extraction_node(state: GraphState):
  print('extraction_node')
  print('State', state)
  try:
    result: Extraction = extraction_chain.invoke(state['request'])
    state['symbol'] = result.symbol
  except Exception as e:
    print('Error:', e)
    state['symbol'] = UNKNOWN

  print('Symbol:', state['symbol'])
  return state

def get_income_statement_node(state: GraphState):
  print('get_income_statement_node')
  print('Symbol:', state['symbol'])
  result: IncomeStatement = get_income_statement(state['symbol'])
  return {'income_statement': result}

def get_company_financials_node(state: GraphState):
  print('get_company_financials_node')
  print('Symbol:', state['symbol'])
  result: CompanyFinancials = get_company_financials(state['symbol'])
  return {'company_financials': result}

def get_stock_price_node(state: GraphState):
  print('get_stock_price_node')
  print('Symbol:', state['symbol'])
  result: StockPrice = get_stock_price(state['symbol'])
  return {'stock_price': result}

def error_node(state: GraphState) -> str:
    return f"""
    Unknown Symbol: {state['symbol']}
    Can not produce report for this symbol.
    """

def generate_markdown_report_node(state: GraphState) -> str:
    """
    Generates a markdown report from the GraphState instance.
    """
    company_financials = state['company_financials'] if 'company_financials' in state else None
    income_statement = state['income_statement'] if ('income_statement' in state) else None
    stock_price = state['stock_price'] if ('stock_price' in state) else None
    md_report = generate_markdown_report(company_financials=company_financials, income_statement=income_statement, stock_price=stock_price)
    file_name = f"{state['symbol']}_financial_report.md"
    save_md_report_to_file(md_report, filename= file_name)
    return state    

def is_there_symbol(state: GraphState):
  print('is_there_symbol')
  print('State', state)
  if state['symbol']  == UNKNOWN:
    print('Symbol:', UNKNOWN)
    return False

  return True

