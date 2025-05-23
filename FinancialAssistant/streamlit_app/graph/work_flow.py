from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from consts.consts import (
    NODE_STOCK_PRICE, NODE_INCOME_STATEMENT,
    NODE_COMPANY_FINANCIALS, NODE_ERROR, NODE_REPORT, NODE_PASS,
    NODE_ROUTER, NODE_SYMBOL_EXTRACTION_REPORT, NODE_SYMBOL_EXTRACTION_ALONE,
    NODE_STOCK_PRICE_STAND_ALONE, NODE_INCOME_STATEMENT_STAND_ALONE,
    NODE_COMPANY_FINANCIALS_STAND_ALONE, NODE_CHAT, NODE_FINAL_ANSWER, NODE_GENERATE_REPORT,
    NODE_SUMMARIZE  # Added summarize node constant
)
from graph.state.graph_state import GraphState
from graph.nodes import (
    get_income_statement_node, get_company_financials_node, get_stock_price_node,
    error_node, generate_markdown_report_node, is_there_symbol,
    create_get_route_node, create_chat_node, where_to, where_to_alone,
    final_answer_node, create_symbol_extraction_node, create_summarization_node
)
from methods.memory_manager import MemoryManager

def create_workflow(llm):
    # Create a global memory manager instance
    memory_manager = MemoryManager()

    workflow = StateGraph(GraphState)

    # Add nodes to workflow
    workflow.add_node(NODE_ROUTER, create_get_route_node(llm),)
    workflow.add_node(NODE_SYMBOL_EXTRACTION_REPORT, create_symbol_extraction_node(llm))
    workflow.add_node(NODE_SYMBOL_EXTRACTION_ALONE, create_symbol_extraction_node(llm))
    workflow.add_node(NODE_CHAT, create_chat_node(llm))
    workflow.add_node(NODE_SUMMARIZE, create_summarization_node(llm))

    # Add other existing nodes
    workflow.add_node(NODE_PASS, lambda state: state)
    workflow.add_node(NODE_INCOME_STATEMENT, get_income_statement_node)
    workflow.add_node(NODE_COMPANY_FINANCIALS, get_company_financials_node)
    workflow.add_node(NODE_STOCK_PRICE, get_stock_price_node)
    workflow.add_node(NODE_INCOME_STATEMENT_STAND_ALONE, get_income_statement_node)
    workflow.add_node(NODE_COMPANY_FINANCIALS_STAND_ALONE, get_company_financials_node)
    workflow.add_node(NODE_STOCK_PRICE_STAND_ALONE, get_stock_price_node)
    workflow.add_node(NODE_FINAL_ANSWER, final_answer_node)
    workflow.add_node(NODE_GENERATE_REPORT, generate_markdown_report_node)
    workflow.add_node(NODE_ERROR, error_node)

    # Set entry point
    workflow.set_entry_point(NODE_ROUTER)

    workflow.add_conditional_edges(NODE_ROUTER, where_to,  path_map={
        'report': NODE_SYMBOL_EXTRACTION_REPORT,
        'alone': NODE_SYMBOL_EXTRACTION_ALONE,
        'chat': NODE_CHAT
    })

    workflow.add_conditional_edges(NODE_SYMBOL_EXTRACTION_REPORT, is_there_symbol, {True:NODE_PASS, False: NODE_ERROR})
    workflow.add_conditional_edges(NODE_SYMBOL_EXTRACTION_ALONE, where_to_alone, {
        'error': NODE_ERROR,
        'income_statement': NODE_INCOME_STATEMENT_STAND_ALONE,
        'company_financials': NODE_COMPANY_FINANCIALS_STAND_ALONE,
        'stock_price': NODE_STOCK_PRICE_STAND_ALONE,
        })

    # workflow.add_conditional_edges(ROUTER, lambda x: x['request_category'],  path_map={
    #     'report': SYMBOL_EXTRACTION_REPORT,
    #     'income_statement': INCOME_STATEMENT_STAND_ALONE,
    #     'company_financials': COMPANY_FINANCIALS_STAND_ALONE,
    #     'stock_price': STOCK_PRICE_STAND_ALONE,
    #     'chat': CHAT_NODE
    # })


    # workflow.add_conditional_edges(SYMBOL_EXTRACTION_REPORT, is_there_symbol, {True:PASS, False: ERROR_NODE})

    workflow.add_edge(NODE_PASS,NODE_INCOME_STATEMENT)
    workflow.add_edge(NODE_PASS,NODE_COMPANY_FINANCIALS)
    workflow.add_edge(NODE_PASS,NODE_STOCK_PRICE)

    workflow.add_edge(NODE_INCOME_STATEMENT,NODE_GENERATE_REPORT)
    workflow.add_edge(NODE_COMPANY_FINANCIALS,NODE_GENERATE_REPORT)
    workflow.add_edge(NODE_STOCK_PRICE,NODE_GENERATE_REPORT)

    workflow.add_edge(NODE_GENERATE_REPORT, NODE_FINAL_ANSWER)
    workflow.add_edge(NODE_ERROR, NODE_FINAL_ANSWER)

    workflow.add_edge(NODE_INCOME_STATEMENT_STAND_ALONE,NODE_FINAL_ANSWER)
    workflow.add_edge(NODE_COMPANY_FINANCIALS_STAND_ALONE,NODE_FINAL_ANSWER)
    workflow.add_edge(NODE_STOCK_PRICE_STAND_ALONE,NODE_FINAL_ANSWER)
    workflow.add_edge(NODE_CHAT,NODE_FINAL_ANSWER)

    # Add summarization node before END
    workflow.add_edge(NODE_FINAL_ANSWER, NODE_SUMMARIZE)
    workflow.add_edge(NODE_SUMMARIZE, END)

    # Use a checkpointer for within-thread memory
    within_thread_memory = MemorySaver()

    # Compile with both within-thread and across-thread memory
    app = workflow.compile(checkpointer=within_thread_memory, store=memory_manager)
    # app.get_graph().draw_mermaid_png(output_file_path="financial_asstant_graph.png")
    return app


