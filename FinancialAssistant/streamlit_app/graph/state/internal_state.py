from typing import TypedDict, Any, Optional

class InternalState(TypedDict, total=False):
  """
     Represents the internal state of our graph.

    Attributes:
        symbol: The symbol of the company.
        income_statement: The income statement of the company.
        company_financials: The company financials of the company.
        stock_price: The stock price of the company.
        report_md: The markdown report of the company.
        error: The error message of the company.
        request_category: The request category of the company.
        chat_response: The chat response of the company.
  """
  symbol: str  
  request_category:str
  income_statement: Optional[str]
  company_financials: Optional[str]
  stock_price: Optional[str]
  report_md: Optional[str]
  error: Optional[str]
  chat_response: Optional[str]
