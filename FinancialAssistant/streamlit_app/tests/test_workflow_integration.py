"""
Integration tests for the workflow with cross-thread memory.
"""

import pytest
from graph.work_flow import create_workflow
from methods.memory_manager import MemoryManager
from chains.route_chain import RouterResult
from chains.extraction_chain import Extraction
from chains.chat_chain import ChatResult
from chains.summarization_chain import SummarizationResult
from consts.consts import UNKNOWN


@pytest.fixture
def mock_llm(mocker):
    """
    Creates a mock LLM that returns appropriate responses for different chains.
    """
    # Create the base mock LLM
    llm = mocker.Mock()

    # Create mocks for each structured output type
    router_chain = mocker.Mock()

    # Create actual RouterResult objects
    result1 = RouterResult(route="chat")
    result2 = RouterResult(route="stock_price")

    # Configure the mock to return these objects
    router_chain.invoke.side_effect = [result1, result2]

    extraction_chain = mocker.Mock()
    extraction_chain.invoke.side_effect = [
        Extraction(symbol="AAPL"),
        Extraction(symbol=UNKNOWN)
    ]

    chat_chain = mocker.Mock()
    chat_chain.invoke.side_effect = [
        ChatResult(response="Apple is a technology company."),
        ChatResult(response="The stock price is high.")
    ]

    summarization_chain = mocker.Mock()
    summarization_chain.invoke.side_effect = [
        SummarizationResult(summary="User asked about Apple."),
        SummarizationResult(summary="User asked about Apple and its stock price.")
    ]

    # Configure the with_structured_output method
    def with_structured_output_side_effect(cls):
        if cls.__name__ == "RouterResult":
            return router_chain
        elif cls.__name__ == "Extraction":
            return extraction_chain
        elif cls.__name__ == "ChatResult":
            return chat_chain
        elif cls.__name__ == "SummarizationResult":
            return summarization_chain
        else:
            default_mock = mocker.Mock()
            default_mock.invoke.return_value = "Unknown response"
            return default_mock

    llm.with_structured_output.side_effect = with_structured_output_side_effect

    return llm


@pytest.fixture
def memory_manager():
    """
    Creates a real memory manager for integration testing.
    """
    return MemoryManager()


@pytest.fixture
def workflow(mock_llm):
    """
    Creates a workflow with the mock LLM.
    """
    return create_workflow(mock_llm)


def test_workflow_with_memory(workflow, memory_manager):
    """
    Test that the workflow maintains memory across different requests.
    """
    # First request - should use the chat route
    result1 = workflow.invoke(
        {"request": "Tell me about Apple"},
        {"configurable": {"thread_id": "test_thread", "user_id": "test_user", "checkpoint_ns": "test", "checkpoint_id": "test"}}
    )

    # Verify the result
    assert result1["request_category"] == "chat"
    assert result1["chat_response"] == "Apple is a technology company."

    # Verify the memory was updated
    summary = memory_manager.get_conversation_summary("test_user")
    assert summary == "User asked about Apple."

    # Second request - should use the stock_price route and remember the symbol
    result2 = workflow.invoke(
        {"request": "What's the stock price?"},
        {"configurable": {"thread_id": "test_thread", "user_id": "test_user", "checkpoint_ns": "test", "checkpoint_id": "test"}}
    )

    # Verify the result
    assert result2["request_category"] == "stock_price"
    assert result2["symbol"] == "AAPL"  # Should use the remembered symbol

    # Verify the memory was updated
    summary = memory_manager.get_conversation_summary("test_user")
    assert summary == "User asked about Apple and its stock price."


def test_workflow_with_different_users(workflow, memory_manager):
    """
    Test that the workflow maintains separate memory for different users.
    """
    # First user request
    workflow.invoke(
        {"request": "Tell me about Microsoft"},
        {"configurable": {"thread_id": "thread1", "user_id": "user1", "checkpoint_ns": "test1", "checkpoint_id": "test1"}}
    )

    # Second user request
    workflow.invoke(
        {"request": "Tell me about Apple"},
        {"configurable": {"thread_id": "thread2", "user_id": "user2", "checkpoint_ns": "test2", "checkpoint_id": "test2"}}
    )

    # Verify each user has their own memory
    summary1 = memory_manager.get_conversation_summary("user1")
    summary2 = memory_manager.get_conversation_summary("user2")

    assert "Microsoft" in summary1
    assert "Apple" in summary2
    assert summary1 != summary2
