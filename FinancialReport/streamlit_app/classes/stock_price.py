from pydantic import BaseModel, Field
import requests
from datetime import datetime
class StockPrice(BaseModel):
    symbol:str = Field(description="The symbol of the company")
    price:float = Field(description="The price of the company")
    volume:float = Field(description="The volume of the company")
    priceAvg50:float = Field(description="The 50 day average price of the company")
    priceAvg200:float = Field(description="The 200 day average price of the company")
    eps:float = Field(description="The EPS of the company")
    pe:float = Field(description="The PE of the company")
    earningsAnnouncement:datetime = Field(description="The earnings announcement of the company")
# Define the functions that will fetch financial data
def get_stock_price(symbol):
    """
    Fetch the current stock price for the given symbol, the current volume, the average price 50d and 200d, EPS, PE and the next earnings Announcement.
    """
    try:
      url = f"https://financialmodelingprep.com/api/v3/quote-order/{symbol}?apikey={FINANCIAL_MODELING_PREP_API_KEY}"
      response = requests.get(url)
      data = response.json()
      stock_price = StockPrice(**data[0])
      return stock_price
    except (IndexError, KeyError):
        return {"error": f"Could not fetch price for symbol: {symbol}"}

## DATA PROVIDED BY THIS ENDPOINT:
# [{'symbol': 'AAPL',
#   'name': 'Apple Inc.',
#   'price': 222.5,
#   'changesPercentage': -0.1212,
#   'change': -0.27,
#   'dayLow': 221.91,
#   'dayHigh': 224.03,
#   'yearHigh': 237.23,
#   'yearLow': 164.08,
#   'marketCap': 3382912250000,
#   'priceAvg50': 223.0692,
#   'priceAvg200': 195.382,
#   'exchange': 'NASDAQ',
#   'volume': 35396922,
#   'avgVolume': 57548506,
#   'open': 223.58,
#   'previousClose': 222.77,
#   'eps': 6.57,
#   'pe': 33.87,
#   'earningsAnnouncement': '2024-10-31T00:00:00.000+0000',
#   'sharesOutstanding': 15204100000,
#   'timestamp': 1726257601}]
