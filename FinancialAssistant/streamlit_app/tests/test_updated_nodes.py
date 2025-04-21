"""
Unit tests for the updated nodes (router, symbol extraction, and chat).
"""

import pytest
from graph.graph_state import GraphState
from graph.nodes.router_node import create_get_route_node
from graph.nodes.extraction_node import create_symbol_extraction_node
from graph.nodes.chat_node import create_chat_node
from chains.route_chain import RouterResult
from chains.extraction_chain import Extraction
from chains.chat_chain import ChatResult
from consts.consts import UNKNOWN


@pytest.fixture
def mock_llm(mocker):
    """
    Creates a mock LLM.
    """
    return mocker.Mock()


@pytest.fixture
def memory_manager():
    """
    Creates a real memory manager for testing.
    """
    from methods.memory_manager import MemoryManager
    manager = MemoryManager()

    # Pre-populate with test data
    test_user_id = "test_user"
    manager.update_conversation_summary(test_user_id, "Previous conversation about tech stocks")
    manager.update_last_symbol(test_user_id, "AAPL")

    return manager


@pytest.fixture
def test_config():
    """
    Creates a test config with user_id.
    """
    return {"configurable": {"user_id": "test_user"}}


@pytest.fixture
def test_state_with_request():
    """
    Creates a test state with a request.
    """
    return {"request": "What is the stock price?"}


# Router Node Tests
@pytest.fixture
def mock_route_chain(mocker):
    """
    Creates a mock route chain.
    """
    chain = mocker.Mock()
    result = RouterResult(route="stock_price")
    chain.invoke.return_value = result
    return chain


def test_router_node_with_summary(mocker, mock_llm, memory_manager, test_state_with_request, test_config, mock_route_chain):
    """
    Test that the router node uses the conversation summary.
    """
    # Patch the create_route_chain function
    mocker.patch('graph.nodes.router_node.create_route_chain', return_value=mock_route_chain)

    # Create the node
    node = create_get_route_node(mock_llm)

    # Execute the node
    result = node(test_state_with_request, test_config, memory_manager)

    # Verify the chain was called with the right inputs
    mock_route_chain.invoke.assert_called_once()
    call_args = mock_route_chain.invoke.call_args[0][0]
    assert call_args["request"] == "What is the stock price?"
    assert call_args["conversation_summary"] == "Previous conversation about tech stocks"

    # Verify the result contains the correct route
    assert result["request_category"] == "stock_price"


# Symbol Extraction Node Tests
@pytest.fixture
def mock_extraction_chain_unknown(mocker):
    """
    Creates a mock extraction chain that returns UNKNOWN.
    """
    chain = mocker.Mock()
    result = Extraction(symbol=UNKNOWN)
    chain.invoke.return_value = result
    return chain


@pytest.fixture
def mock_extraction_chain_with_symbol(mocker):
    """
    Creates a mock extraction chain that returns a valid symbol.
    """
    chain = mocker.Mock()
    result = Extraction(symbol="MSFT")
    chain.invoke.return_value = result
    return chain


def test_symbol_extraction_with_fallback(mocker, mock_llm, memory_manager, test_state_with_request, test_config, mock_extraction_chain_unknown):
    """
    Test that the symbol extraction node uses the last symbol when extraction returns UNKNOWN.
    """
    # Patch the create_extraction_chain function
    mocker.patch('graph.nodes.extraction_node.create_extraction_chain', return_value=mock_extraction_chain_unknown)

    # Create the node
    node = create_symbol_extraction_node(mock_llm)

    # Execute the node
    result = node(test_state_with_request, test_config, memory_manager)

    # Verify the result contains the fallback symbol
    assert result["symbol"] == "AAPL"


def test_symbol_extraction_without_fallback(mocker, mock_llm, memory_manager, test_state_with_request, test_config, mock_extraction_chain_with_symbol):
    """
    Test that the symbol extraction node uses the extracted symbol when available.
    """
    # Patch the create_extraction_chain function
    mocker.patch('graph.nodes.extraction_node.create_extraction_chain', return_value=mock_extraction_chain_with_symbol)

    # Create the node
    node = create_symbol_extraction_node(mock_llm)

    # Execute the node
    result = node(test_state_with_request, test_config, memory_manager)

    # Verify the result contains the extracted symbol
    assert result["symbol"] == "MSFT"


# Chat Node Tests
@pytest.fixture
def mock_chat_chain(mocker):
    """
    Creates a mock chat chain.
    """
    chain = mocker.Mock()
    result = ChatResult(response="This is a response that considers your previous questions about tech stocks.")
    chain.invoke.return_value = result
    return chain


def test_chat_node_with_summary(mocker, mock_llm, memory_manager, test_state_with_request, test_config, mock_chat_chain):
    """
    Test that the chat node uses the conversation summary.
    """
    # Patch the create_chat_chain function
    mocker.patch('graph.nodes.chat_node.create_chat_chain', return_value=mock_chat_chain)

    # Create the node
    node = create_chat_node(mock_llm)

    # Execute the node
    result = node(test_state_with_request, test_config, memory_manager)

    # Verify the chain was called with the right inputs
    mock_chat_chain.invoke.assert_called_once()
    call_args = mock_chat_chain.invoke.call_args[0][0]
    assert call_args["request"] == "What is the stock price?"
    assert call_args["conversation_summary"] == "Previous conversation about tech stocks"

    # Verify the result contains the correct response
    assert result["chat_response"] == "This is a response that considers your previous questions about tech stocks."
