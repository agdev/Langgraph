"""
Financial data nodes for the Financial Assistant application.
"""

from langchain_core.runnables.config import RunnableConfig
from graph.state.graph_state import GraphState
from graph.state.internal_state import InternalState
from classes.income_statement import IncomeStatement, get_income_statement
from classes.company_financials import CompanyFinancials, get_company_financials
from classes.stock_price import StockPrice, get_stock_price
from methods.generate_methods import generate_markdown_financials, generate_markdown_income_statement, generate_markdown_stock_price
from consts.consts import UNKNOWN, KEY_SYMBOL, KEY_INCOME_STATEMENT, KEY_COMPANY_FINANCIALS, KEY_STOCK_PRICE
from methods.util import get_fmp_api_key

def get_income_statement_node(state: InternalState, config: RunnableConfig)->InternalState:
  symbol = state.get(KEY_SYMBOL, UNKNOWN)
  print('get_income_statement_node')
  print('Symbol:', symbol)
  income_statement: IncomeStatement | None = get_income_statement(symbol, get_fmp_api_key(config))
  if income_statement is None:
    return {KEY_INCOME_STATEMENT: None}
  result = generate_markdown_income_statement(income_statement)
  return {KEY_INCOME_STATEMENT: result}

def get_company_financials_node(state: InternalState, config: RunnableConfig)->InternalState:
  symbol = state.get(KEY_SYMBOL, UNKNOWN)
  print('get_company_financials_node')
  print('Symbol:', symbol)
  info: CompanyFinancials | None= get_company_financials(symbol, get_fmp_api_key(config))
  if info is None:
    return {KEY_COMPANY_FINANCIALS: None}
  result = generate_markdown_financials(info)
  return {KEY_COMPANY_FINANCIALS: result}

def get_stock_price_node(state: InternalState, config: RunnableConfig)->InternalState:
  symbol = state.get(KEY_SYMBOL, UNKNOWN)
  print('get_stock_price_node')
  print('Symbol:', symbol)
  stock_price: StockPrice | None= get_stock_price(symbol, get_fmp_api_key(config))
  if stock_price is None:
    return {KEY_STOCK_PRICE: None}
  result = generate_markdown_stock_price(stock_price)
  return {KEY_STOCK_PRICE: result}
