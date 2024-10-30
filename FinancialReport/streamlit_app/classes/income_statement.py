from pydantic import BaseModel, Field
from datetime import date
import requests
from typing import Union
class IncomeStatement(BaseModel):
    date_field: date = Field(alias='date', description="The date of the income statement")
    revenue:float = Field(description="The revenue of the company")
    gross_profit:float = Field(alias='grossProfit', description="The gross profit of the company")
    net_income:float = Field(alias='netIncome', description="The net income of the company")
    ebitda:float = Field(description="The EBITDA of the company")
    eps:float = Field(description="The EPS of the company")
    eps_diluted:float = Field(alias='epsdiluted', description="The EPS diluted of the company")


def get_income_statement(symbol:str, api_key: str) -> Union[IncomeStatement, None]:
    """
    Fetch last income statement for the given company symbol such as revenue, gross profit, net income, EBITDA, EPS.
    """
    try:
      url = f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}?period=annual&apikey={api_key}"
      response = requests.get(url)
      data = response.json()
      financials = IncomeStatement(**data[0])
      return financials
    except (IndexError, KeyError):
        print ("Error:",f"Could not fetch financials for symbol: {symbol}")
        return None

## DATA PROVIDED BY THIS ENDPOINT:
# {'date': '2023-09-30',
#   'symbol': 'AAPL',
#   'reportedCurrency': 'USD',
#   'cik': '0000320193',
#   'fillingDate': '2023-11-03',
#   'acceptedDate': '2023-11-02 18:08:27',
#   'calendarYear': '2023',
#   'period': 'FY',
#   'revenue': 383285000000,
#   'costOfRevenue': 214137000000,
#   'grossProfit': 169148000000,
#   'grossProfitRatio': 0.4413112958,
#   'researchAndDevelopmentExpenses': 29915000000,
#   'generalAndAdministrativeExpenses': 0,
#   'sellingAndMarketingExpenses': 0,
#   'sellingGeneralAndAdministrativeExpenses': 24932000000,
#   'otherExpenses': 382000000,
#   'operatingExpenses': 55229000000,
#   'costAndExpenses': 269366000000,
#   'interestIncome': 3750000000,
#   'interestExpense': 3933000000,
#   'depreciationAndAmortization': 11519000000,
#   'ebitda': 125820000000,
#   'ebitdaratio': 0.3282674772,
#   'operatingIncome': 114301000000,
#   'operatingIncomeRatio': 0.2982141227,
#   'totalOtherIncomeExpensesNet': -565000000,
#   'incomeBeforeTax': 113736000000,
#   'incomeBeforeTaxRatio': 0.2967400237,
#   'incomeTaxExpense': 16741000000,
#   'netIncome': 96995000000,
#   'netIncomeRatio': 0.2530623426,
#   'eps': 6.16,
#   'epsdiluted': 6.13,
#   'weightedAverageShsOut': 15744231000,
#   'weightedAverageShsOutDil': 15812547000,
#   'link': 'https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/0000320193-23-000106-index.htm',
#   'finalLink': 'https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/aapl-20230930.htm'}