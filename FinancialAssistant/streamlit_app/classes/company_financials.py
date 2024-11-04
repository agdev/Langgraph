from pydantic import BaseModel, Field
import requests
from typing import Union

class CompanyFinancials(BaseModel):
    """
    A class that represents the company financials.
    """
    symbol:str =  Field(description="The symbol of the company")
    companyName:str =  Field(description="The name of the company")
    marketCap:float = Field(alias="mktCap", description="The market capitalization of the company")
    industry:str =  Field(description="The industry of the company")
    sector:str =  Field(description="The sector of the company")
    website:str =  Field(description="The website of the company")
    beta:float = Field(description="The beta of the company")
    price:float = Field(description="The price of the company")

def get_company_financials(symbol, api_key: str) -> Union[CompanyFinancials, None]:
    """
    Fetch basic financial information for the given company symbol such as the industry, the sector, the name of the company, and the market capitalization.
    """
    try:
      url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={api_key}"
      response = requests.get(url)
      data = response.json()
      financials = CompanyFinancials(**data[0])
      return financials
    except (IndexError, KeyError):
        print ("Error:",f"Could not fetch financials for symbol: {symbol}")
        return None

## DATA PROVIDED BY THIS ENDPOINT:
# [{'symbol': 'AAPL',
#   'price': 222.5,
#   'beta': 1.24,
#   'volAvg': 57548506,
#   'mktCap': 3382912250000,
#   'lastDiv': 1,
#   'range': '164.08-237.23',
#   'changes': -0.27,
#   'companyName': 'Apple Inc.',
#   'currency': 'USD',
#   'cik': '0000320193',
#   'isin': 'US0378331005',
#   'cusip': '037833100',
#   'exchange': 'NASDAQ Global Select',
#   'exchangeShortName': 'NASDAQ',
#   'industry': 'Consumer Electronics',
#   'website': 'https://www.apple.com',
#   'description': 'Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide. The company offers iPhone, a line of smartphones; Mac, a line of personal computers; iPad, a line of multi-purpose tablets; and wearables, home, and accessories comprising AirPods, Apple TV, Apple Watch, Beats products, and HomePod. It also provides AppleCare support and cloud services; and operates various platforms, including the App Store that allow customers to discover and download applications and digital content, such as books, music, video, games, and podcasts. In addition, the company offers various services, such as Apple Arcade, a game subscription service; Apple Fitness+, a personalized fitness service; Apple Music, which offers users a curated listening experience with on-demand radio stations; Apple News+, a subscription news and magazine service; Apple TV+, which offers exclusive original content; Apple Card, a co-branded credit card; and Apple Pay, a cashless payment service, as well as licenses its intellectual property. The company serves consumers, and small and mid-sized businesses; and the education, enterprise, and government markets. It distributes third-party applications for its products through the App Store. The company also sells its products through its retail and online stores, and direct sales force; and third-party cellular network carriers, wholesalers, retailers, and resellers. Apple Inc. was incorporated in 1977 and is headquartered in Cupertino, California.',
#   'ceo': 'Mr. Timothy D. Cook',
#   'sector': 'Technology',
#   'country': 'US',
#   'fullTimeEmployees': '161000',
#   'phone': '408 996 1010',
#   'address': 'One Apple Park Way',
#   'city': 'Cupertino',
#   'state': 'CA',
#   'zip': '95014',
#   'dcfDiff': 55.70546,
#   'dcf': 166.79453554058594,
#   'image': 'https://financialmodelingprep.com/image-stock/AAPL.png',
#   'ipoDate': '1980-12-12',
#   'defaultImage': False,
#   'isEtf': False,
#   'isActivelyTrading': True,
#   'isAdr': False,
#   'isFund': False}]
