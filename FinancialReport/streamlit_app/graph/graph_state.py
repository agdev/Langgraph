from classes.income_statement import IncomeStatement
from classes.company_financials import CompanyFinancials
from classes.stock_price import StockPrice
from langgraph.graph import END, StateGraph
from typing import TypedDict, Any

class GraphState(TypedDict):
  """
     Represents the state of our graph.

    Attributes:
        symbol: The symbol of the company.
        income_statement: The income statement of the company.
        company_financials: The company financials of the company.
        stock_price: The stock price of the company.
  """
  symbol: str
  request: str
  income_statement: IncomeStatement
  company_financials: CompanyFinancials
  stock_price: StockPrice
  report_md: str
  extraction_chain: Any
  error: str
  fmp_api_key: str
