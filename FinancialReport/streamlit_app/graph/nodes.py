from graph.graph_state import GraphState
from classes.income_statement import IncomeStatement, get_income_statement
from classes.company_financials import CompanyFinancials, get_company_financials
from classes.stock_price import StockPrice, get_stock_price
from methods.consts import (
    UNKNOWN, KEY_SYMBOL, KEY_REQUEST, KEY_EXTRACTION_CHAIN,
    KEY_FMP_API_KEY, KEY_ERROR, KEY_REPORT_MD,
    KEY_COMPANY_FINANCIALS, KEY_INCOME_STATEMENT, KEY_STOCK_PRICE
)
from methods.generate_report import generate_markdown_report
from chain.extraction_chain import Extraction
from typing import TypedDict

def extraction_node(state: GraphState):
    """
    Extracts the symbol from the request using the extraction chain.
    """
    print('extraction_node')
    print('State', state)
    symbol = UNKNOWN
    try:
        chain = state[KEY_EXTRACTION_CHAIN]
        if chain is None:
            raise Exception('Extraction chain is not initialized')
            
        result: Extraction = chain.invoke(state[KEY_REQUEST])
        symbol = result.symbol
    except Exception as e:
        print('Error:', e)

    return {KEY_SYMBOL: symbol}

def get_income_statement_node(state: GraphState):
    """
    Fetches the income statement for the given symbol.
    """
    print('get_income_statement_node')
    print('Symbol:', state[KEY_SYMBOL])
    result: IncomeStatement = get_income_statement(state[KEY_SYMBOL], state[KEY_FMP_API_KEY])
    return {KEY_INCOME_STATEMENT: result}

def get_company_financials_node(state: GraphState):
    """
    Fetches the company financials for the given symbol.
    """
    print('get_company_financials_node')
    print('Symbol:', state[KEY_SYMBOL])
    result: CompanyFinancials = get_company_financials(state[KEY_SYMBOL], state[KEY_FMP_API_KEY])
    return {KEY_COMPANY_FINANCIALS: result}

def get_stock_price_node(state: GraphState):
    """
    Fetches the stock price for the given symbol.
    """
    print('get_stock_price_node')
    print('Symbol:', state[KEY_SYMBOL])
    result: StockPrice = get_stock_price(state[KEY_SYMBOL], state[KEY_FMP_API_KEY])
    return {KEY_STOCK_PRICE: result}

def error_node(state: GraphState):
    """
    Returns an error message if the symbol is unknown.
    """
    return {KEY_ERROR: f"""
    Unknown Symbol: {state[KEY_SYMBOL]}
    Can not produce report for this symbol.
    """}

def generate_markdown_report_node(state: GraphState):
    """
    Generates a markdown report from the GraphState instance.
    """
    company_financials = state[KEY_COMPANY_FINANCIALS] if KEY_COMPANY_FINANCIALS in state else None
    income_statement = state[KEY_INCOME_STATEMENT] if KEY_INCOME_STATEMENT in state else None
    stock_price = state[KEY_STOCK_PRICE] if KEY_STOCK_PRICE in state else None
    md_report = generate_markdown_report(
        company_financials=company_financials,
        income_statement=income_statement,
        stock_price=stock_price
    )
    return {KEY_REPORT_MD: md_report}

def is_there_symbol(state: GraphState):
    """ 
    Checks if the symbol is unknown.
    """
    print('is_there_symbol')
    print('State', state)
    if state[KEY_SYMBOL].upper() == UNKNOWN:
        print('Symbol:', UNKNOWN)
        return False

    return True
