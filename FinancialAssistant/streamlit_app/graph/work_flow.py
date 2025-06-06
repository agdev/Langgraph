import sys
from pathlib import Path

# Only add path manipulation for LangGraph server (not Streamlit Cloud)
try:
    # Test if we can import a local module
    import consts.consts
except ImportError:
    # We're in LangGraph server context - add streamlit_app to Python path
    current_dir = Path(__file__).parent
    streamlit_app_dir = current_dir.parent
    sys.path.insert(0, str(streamlit_app_dir))

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


def _create_llm_for_server():
    """Create LLM using existing config system for LangGraph server"""
    from utils.config_loader import create_config_from_env
    from methods.util import get_llm
    import os
    from consts.consts import PROVIDER_GROQ

    # Try to get default provider from environment, fallback to Groq
    default_provider = os.environ.get("LLM_PROVIDER", PROVIDER_GROQ)
    
    # Try each provider until we find one with valid keys
    providers_to_try = [default_provider]
    if default_provider != PROVIDER_GROQ:
        providers_to_try.append(PROVIDER_GROQ)
    if "OpenAI" not in providers_to_try:
        providers_to_try.append("OpenAI")
    if "Anthropic" not in providers_to_try:
        providers_to_try.append("Anthropic")
    
    for provider in providers_to_try:
        config = create_config_from_env(provider)
        if config is not None:
            print(f"Successfully loaded configuration for {provider}")
            return get_llm(config)
    
    # If no provider worked, show helpful error message
    raise ValueError(
        "Could not find valid API keys for any LLM provider. "
        "Please ensure you have set the required environment variables in your .env file:\n"
        "- FINANCIAL_MODELING_PREP_API_KEY (required for all providers)\n"
        "- At least one of: GROQ_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY\n"
        "- Optionally set LLM_PROVIDER to specify which provider to use"
    )


# Entry point for LangGraph server
def create_graph():
    """Factory function for LangGraph server using existing config system"""
    llm = _create_llm_for_server()
    return create_workflow(llm)