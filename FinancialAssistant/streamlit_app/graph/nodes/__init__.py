"""
Node functions for the Financial Assistant application.
"""

# Router node
from graph.nodes.router_node import create_get_route_node

# Symbol extraction node
from graph.nodes.extraction_node import create_symbol_extraction_node

# Financial data nodes
from graph.nodes.financial_data_nodes import (
    get_income_statement_node,
    get_company_financials_node,
    get_stock_price_node
)

# Chat node
from graph.nodes.chat_node import create_chat_node

# Report node
from graph.nodes.report_node import generate_markdown_report_node

# Utility nodes
from graph.nodes.utility_nodes import (
    error_node,
    is_there_symbol,
    where_to,
    where_to_alone,
    final_answer_node
)

# Summarization node
from graph.nodes.summarization_node import create_summarization_node