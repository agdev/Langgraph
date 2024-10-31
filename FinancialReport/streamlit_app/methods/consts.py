"""
Constants used in the application.
"""

# General constants
UNKNOWN = 'UNKNOWN'

# Provider names
PROVIDER_GROQ = "Groq"
PROVIDER_OPENAI = "OpenAI" 
PROVIDER_ANTHROPIC = "Anthropic"

# Model names
MODEL_GROQ = "mixtral-8x7b-32768"
MODEL_OPENAI = "gpt-4o-mini"
MODEL_ANTHROPIC = "claude-3-sonnet-20240229"

# Node names
NODE_EXTRACTION = 'Extraction'
NODE_STOCK_PRICE = 'StockPrice'
NODE_INCOME_STATEMENT = 'IncomeStatement'
NODE_COMPANY_FINANCIALS = 'CompanyFinancials'
NODE_ERROR = 'ErrorNode'
NODE_REPORT = 'Report'
NODE_PASS = 'Pass'

# Session state keys
STATE_MESSAGES = "messages"
STATE_SELECTED_PROVIDER = "selected_provider"
STATE_CONFIG = "config"
STATE_EXTRACTION_CHAIN = "extraction_chain"

# UI Messages
MSG_API_KEYS_SAVED = "API keys saved successfully!"
MSG_ENTER_BOTH_KEYS = "Please enter both API keys"
MSG_CONFIGURE_API = "Please configure your API keys in the sidebar to start chatting."

# UI Labels
LABEL_API_CONFIG = "API Configuration"
LABEL_SELECT_PROVIDER = "Select LLM Provider"
LABEL_API_KEY = "API Key"
LABEL_FMP_API_KEY = "Financial Modeling Prep API Key"
LABEL_SAVE_KEYS = "Save API Keys"

# Dictionary keys
KEY_SYMBOL = "symbol"
KEY_REQUEST = "request"
KEY_ERROR = "error"
KEY_REPORT_MD = "report_md"
KEY_EXTRACTION_CHAIN = "extraction_chain"
KEY_FMP_API_KEY = "fmp_api_key"
KEY_ROLE = "role"
KEY_CONTENT = "content"

# State keys
KEY_COMPANY_FINANCIALS = "company_financials"
KEY_INCOME_STATEMENT = "income_statement"
KEY_STOCK_PRICE = "stock_price"
KEY_DATE = "date"
KEY_COMPANY_NAME = "companyName"
KEY_MARKET_CAP = "marketCap"
KEY_INDUSTRY = "industry"
KEY_SECTOR = "sector"
KEY_WEBSITE = "website"
KEY_BETA = "beta"
KEY_PRICE = "price"
KEY_VOLUME = "volume"
KEY_PRICE_AVG_50 = "priceAvg50"
KEY_PRICE_AVG_200 = "priceAvg200"
KEY_EPS = "eps"
KEY_PE = "pe"
KEY_EARNINGS_ANNOUNCEMENT = "earningsAnnouncement"
KEY_REVENUE = "revenue"
KEY_GROSS_PROFIT = "grossProfit"
KEY_NET_INCOME = "netIncome"
KEY_EBITDA = "ebitda"
KEY_EPS_DILUTED = "epsdiluted"

# Chat roles
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
