"""
Unit tests for the summarization node.
"""

import pytest
from graph.graph_state import GraphState
from graph.summarization_node import create_summarization_node
from chains.summarization_chain import SummarizationResult


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
    manager.update_conversation_summary(test_user_id, "Previous summary")

    return manager


@pytest.fixture
def mock_store(mocker):
    """
    Creates a mock store for the node function.
    """
    from methods.memory_manager import MemoryManager
    store = mocker.Mock(spec=MemoryManager)
    store.get_conversation_summary.return_value = "Previous summary"
    return store


@pytest.fixture
def test_state():
    """
    Creates a test state with request and final_answer.
    """
    return {
        "request": "What is the stock price of Apple?",
        "final_answer": "The current stock price of Apple (AAPL) is $150.25.",
        "symbol": "AAPL"
    }


@pytest.fixture
def test_config():
    """
    Creates a test config with user_id.
    """
    return {"configurable": {"user_id": "test_user"}}


@pytest.fixture
def mock_summarization_chain(mocker):
    """
    Creates a mock summarization chain.
    """
    chain = mocker.Mock()
    chain.invoke.return_value = SummarizationResult(summary="User asked about Apple stock price")
    return chain


def test_create_summarization_node(mock_llm):
    """
    Test that the summarization node can be created.
    """
    node = create_summarization_node(mock_llm)
    assert node is not None


def test_summarization_node_execution(mocker, mock_llm, memory_manager, test_state, test_config, mock_store, mock_summarization_chain):
    """
    Test that the summarization node executes correctly.
    """
    # Patch the create_summarization_chain function
    mocker.patch('graph.summarization_node.create_summarization_chain', return_value=mock_summarization_chain)

    # Create the node
    node = create_summarization_node(mock_llm)

    # Execute the node
    result = node(test_state, test_config, mock_store)

    # Verify the chain was called with the right inputs
    mock_summarization_chain.invoke.assert_called_once()
    call_args = mock_summarization_chain.invoke.call_args[0][0]
    assert call_args["existing_summary"] == "Previous summary"
    assert "User: What is the stock price of Apple?" in call_args["conversation"]
    assert "Assistant: The current stock price of Apple (AAPL) is $150.25." in call_args["conversation"]

    # Verify the store was updated
    mock_store.update_conversation_summary.assert_called_once_with("test_user", "User asked about Apple stock price")
    mock_store.update_last_symbol.assert_called_once_with("test_user", "AAPL")

    # Verify the state is unchanged
    assert result == test_state


def test_summarization_node_without_symbol(mocker, mock_llm, memory_manager, test_config, mock_store, mock_summarization_chain):
    """
    Test that the summarization node works correctly when there's no symbol in the state.
    """
    # Create a state without a symbol
    state_without_symbol = GraphState({
        "request": "What are the best tech stocks?",
        "final_answer": "Some of the best tech stocks include Apple, Microsoft, and Google."
    })
    # Patch the create_summarization_chain function
    mocker.patch('graph.summarization_node.create_summarization_chain', return_value=mock_summarization_chain)

    # Create the node
    node = create_summarization_node(mock_llm)

    # Execute the node
    result = node(state_without_symbol, test_config, mock_store)

    # Verify the store was updated with the summary but not with a symbol
    mock_store.update_conversation_summary.assert_called_once()
    mock_store.update_last_symbol.assert_not_called()

    # Verify the state is unchanged
    assert result == state_without_symbol
