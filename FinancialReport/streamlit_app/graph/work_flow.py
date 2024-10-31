from graph.graph_state import GraphState
from graph.nodes import extraction_node, get_income_statement_node, get_company_financials_node, get_stock_price_node, error_node, generate_markdown_report_node, is_there_symbol
from langgraph.graph import END, StateGraph
from methods.consts import (
    NODE_EXTRACTION, NODE_STOCK_PRICE, NODE_INCOME_STATEMENT,
    NODE_COMPANY_FINANCIALS, NODE_ERROR, NODE_REPORT, NODE_PASS
)

workflow = StateGraph(GraphState)
workflow.add_node(NODE_EXTRACTION, extraction_node)
workflow.add_node(NODE_PASS, lambda state: state)
workflow.add_node(NODE_INCOME_STATEMENT, get_income_statement_node)
workflow.add_node(NODE_COMPANY_FINANCIALS, get_company_financials_node)
workflow.add_node(NODE_STOCK_PRICE, get_stock_price_node)
workflow.add_node(NODE_REPORT, generate_markdown_report_node)
workflow.add_node(NODE_ERROR, error_node)

workflow.set_entry_point(NODE_EXTRACTION)

workflow.add_conditional_edges(NODE_EXTRACTION, is_there_symbol, {True:NODE_PASS, False: NODE_ERROR})

workflow.add_edge(NODE_PASS, NODE_INCOME_STATEMENT)
workflow.add_edge(NODE_PASS, NODE_COMPANY_FINANCIALS)
workflow.add_edge(NODE_PASS, NODE_STOCK_PRICE)

workflow.add_edge(NODE_INCOME_STATEMENT, NODE_REPORT)
workflow.add_edge(NODE_COMPANY_FINANCIALS, NODE_REPORT)
workflow.add_edge(NODE_STOCK_PRICE, NODE_REPORT)

workflow.add_edge(NODE_REPORT, END)
workflow.add_edge(NODE_ERROR, END)

compiled_graph = workflow.compile()

# def create_graph(extraction_chain: Any):
#     graph = compiled_graph.bind(extraction_chain=extraction_chain)
#     return graph
# app.debug = True

# compiled_graph.get_graph().draw_mermaid_png(output_file_path="financial_data_report_graph.png")
