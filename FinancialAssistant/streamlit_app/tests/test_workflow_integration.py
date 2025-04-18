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


from langchain_core.language_models.llms import BaseLLM
from langchain_core.outputs import LLMResult, Generation
from typing import Any, List
from pydantic import PrivateAttr

class MockLLM(BaseLLM):
    """
    A mock LLM that returns predefined responses based on the output class.
    """
    # Define model config to allow extra fields
    model_config = {"extra": "allow"}

    # Use private attributes for the responses and call count
    _responses: List[Any] = PrivateAttr(default_factory=list)
    _call_count: int = PrivateAttr(default=0)

    def __init__(self, responses, **kwargs):
        super().__init__(**kwargs)
        self._responses = responses
        self._call_count = 0

    def _generate(self, prompts, stop=None, run_manager=None, **kwargs) -> LLMResult:
        """Return a mock response."""
        # We ignore the prompts and just return the next response
        response = self._responses[self._call_count % len(self._responses)]
        self._call_count += 1
        # Return a dummy LLMResult
        # For structured output, we need to return the actual object as JSON
        if hasattr(response, 'model_dump_json'):
            # For Pydantic models
            text = response.model_dump_json()
        else:
            # Fallback
            text = str(response)
        return LLMResult(generations=[[Generation(text=text)]])

    @property
    def _llm_type(self) -> str:
        """Return the type of LLM."""
        return "mock"


@pytest.fixture
def mock_responses():
    """
    Creates mock responses for different chains.
    """
    return {
        "RouterResult": [
            RouterResult(route="chat"),
            RouterResult(route="stock_price")
        ],
        "Extraction": [
            Extraction(symbol="AAPL"),
            Extraction(symbol=UNKNOWN)
        ],
        "ChatResult": [
            ChatResult(response="Apple is a technology company."),
            ChatResult(response="The stock price is high.")
        ],
        "SummarizationResult": [
            SummarizationResult(summary="User asked about Apple."),
            SummarizationResult(summary="User asked about Apple and its stock price.")
        ]
    }


@pytest.fixture
def mock_llm(mocker, mock_responses):
    """
    Creates a mock LLM that returns different responses for different chains.
    """
    llm = mocker.Mock()

    def side_effect(cls):
        class_name = cls.__name__
        responses = mock_responses.get(class_name, ["Unknown response"])
        return MockLLM(responses)

    llm.with_structured_output.side_effect = side_effect
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
