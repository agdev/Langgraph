from typing import TypedDict, Any

class GraphState(TypedDict, total=False):
  """
     Represents the state of our graph.

    Attributes:
        symbol: The symbol of the company.
        income_statement: The income statement of the company.
        company_financials: The company financials of the company.
        stock_price: The stock price of the company.
        report_md: The markdown report of the company.
        extraction_chain: The extraction chain of the company.
        chat_chain: The chat chain of the company.
        error: The error message of the company.
        fmp_api_key: The FMP API key of the company.
        request_category: The request category of the company.
        chat_response: The chat response of the company.
        final_answer: The final answer of the company.
  """
  symbol: str
  request: str
  income_statement: str
  company_financials: str
  stock_price: str
  report_md: str
  extraction_chain: Any
  chat_chain: Any
  error: str
  fmp_api_key: str
  request_category: str
  chat_response: str
  final_answer: str

