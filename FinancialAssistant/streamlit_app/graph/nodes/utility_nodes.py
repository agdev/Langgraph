"""
Utility nodes for the Financial Assistant application.
"""

from graph.graph_state import GraphState
from consts.consts import (
    UNKNOWN, KEY_SYMBOL, KEY_ERROR, KEY_REQUEST_CATEGORY, 
    KEY_INCOME_STATEMENT, KEY_COMPANY_FINANCIALS, KEY_STOCK_PRICE, 
    KEY_CHAT_RESPONSE, KEY_REPORT_MD, KEY_FINAL_ANSWER
)

def error_node(state: GraphState):
    """
    Returns an error message if the symbol is unknown.
    """
    return {KEY_ERROR: f"""
    Unknown Symbol: {state.get(KEY_SYMBOL)}
    Can not produce report for this symbol.
    """}

def is_there_symbol(state: GraphState):
    """
    Checks if the symbol is unknown.
    """
    print('is_there_symbol')
    print('State', state)
    symbol = state.get(KEY_SYMBOL, UNKNOWN)
    if symbol.upper() == UNKNOWN:
        print('Symbol:', UNKNOWN)
        return False

    return True

def where_to(state: GraphState):
    """Determines which path to take based on the request category."""
    category = state.get(KEY_REQUEST_CATEGORY)
    if category == 'report':
        return 'report'
    elif category == 'chat':
        return 'chat'
    return 'alone'

def where_to_alone(state: GraphState):
    """Determines which standalone node to use."""
    symbol = state.get(KEY_SYMBOL, UNKNOWN)
    if symbol.upper() == UNKNOWN:
        return 'error'
    return state.get(KEY_REQUEST_CATEGORY)

def final_answer_node(state: GraphState):
    """Generates the final answer based on the request category."""
    category = state.get(KEY_REQUEST_CATEGORY)
    if category == 'income_statement':
        if KEY_ERROR in state:
            result = state[KEY_ERROR]
        else:
            result_data = state.get(KEY_INCOME_STATEMENT) or ""
            symbol: str = state.get(KEY_SYMBOL) or UNKNOWN
            result = f"# Income statement for ({symbol}) \n" + result_data
    elif category == 'company_financials':
        if KEY_ERROR in state:
            result = state[KEY_ERROR]
        else:
            result_data = state.get(KEY_COMPANY_FINANCIALS) or ""
            symbol: str = state.get(KEY_SYMBOL) or UNKNOWN
            result = f"# Company financials for ({symbol}) \n" + result_data
    elif category == 'stock_price':
        if KEY_ERROR in state:
            result = state[KEY_ERROR]
        else:
            result_data = state.get(KEY_STOCK_PRICE) or ""
            symbol: str = state.get(KEY_SYMBOL) or UNKNOWN
            result = f"# Stock Price for ({symbol}) \n" + result_data
    elif category == 'chat':
        result = state.get(KEY_CHAT_RESPONSE) or "No response available"
    elif category == 'report':
        if KEY_REPORT_MD in state:
            result_data = state.get(KEY_REPORT_MD) or ""
            symbol: str = state.get(KEY_SYMBOL) or UNKNOWN
            result = f"# Report for ({symbol}) \\n" + result_data
        elif KEY_ERROR in state:
            result = state[KEY_ERROR]
        else:
            result = "Can not provide an answer"
    else:
        result = "Can not provide an answer"

    return {KEY_FINAL_ANSWER: result}
