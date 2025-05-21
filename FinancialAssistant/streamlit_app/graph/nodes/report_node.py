"""
Report generation node for the Financial Assistant application.
"""

from graph.state.graph_state import GraphState
from methods.generate_methods import generate_markdown_report
from consts.consts import KEY_COMPANY_FINANCIALS, KEY_INCOME_STATEMENT, KEY_STOCK_PRICE, KEY_REPORT_MD

def generate_markdown_report_node(state: GraphState):
    """
    Generates a markdown report from the GraphState instance.
    """
    print('generate_markdown_report_node')
    company_financials = state[KEY_COMPANY_FINANCIALS] if KEY_COMPANY_FINANCIALS in state else None
    income_statement = state[KEY_INCOME_STATEMENT] if KEY_INCOME_STATEMENT in state else None
    stock_price = state[KEY_STOCK_PRICE] if KEY_STOCK_PRICE in state else None
    md_report = generate_markdown_report(
        company_financials=company_financials,
        income_statement=income_statement,
        stock_price=stock_price
    )
    return {KEY_REPORT_MD: md_report}
