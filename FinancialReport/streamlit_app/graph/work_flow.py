from graph.graph_state import GraphState
from graph.nodes import extraction_node, get_income_statement_node, get_company_financials_node, get_stock_price_node, error_node, generate_markdown_report_node, is_there_symbol
from langgraph.graph import END, StateGraph

EXTRACTION = 'Extraction'
STOCK_PRICE = 'StockPrice'
INCOME_STATEMENT ='IncomeStatement'
COMPANY_FINANCIALS ='CompanyFinancials'
ERROR_NODE='ErrorNode'
REPORT = 'Report'
PASS = 'Pass'

workflow = StateGraph(GraphState)
workflow.add_node(EXTRACTION, extraction_node)
workflow.add_node(PASS, lambda state: state)
workflow.add_node(INCOME_STATEMENT, get_income_statement_node)
workflow.add_node(COMPANY_FINANCIALS, get_company_financials_node)
workflow.add_node(STOCK_PRICE, get_stock_price_node)
workflow.add_node(REPORT, generate_markdown_report_node)
workflow.add_node(ERROR_NODE, error_node)

workflow.set_entry_point(EXTRACTION)

workflow.add_conditional_edges(EXTRACTION, is_there_symbol, {True:PASS, False: ERROR_NODE})


workflow.add_edge(PASS,INCOME_STATEMENT)
workflow.add_edge(PASS,COMPANY_FINANCIALS)
workflow.add_edge(PASS,STOCK_PRICE)

workflow.add_edge(INCOME_STATEMENT,REPORT)
workflow.add_edge(COMPANY_FINANCIALS,REPORT)
workflow.add_edge(STOCK_PRICE,REPORT)

workflow.add_edge(REPORT, END)
workflow.add_edge(ERROR_NODE, END)


compiled_graph = workflow.compile()

# def create_graph(extraction_chain: Any):
#     graph = compiled_graph.bind(extraction_chain=extraction_chain)
#     return graph
# app.debug = True

# compiled_graph.get_graph().draw_mermaid_png(output_file_path="financial_data_report_graph.png")