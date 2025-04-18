"""
Unit tests for the MemoryManager class.
"""

import pytest
from methods.memory_manager import MemoryManager


@pytest.fixture
def memory_manager():
    """
    Creates a fresh MemoryManager instance for each test.
    """
    return MemoryManager()


@pytest.fixture
def user_id():
    """
    Returns a test user ID.
    """
    return "test_user"


def test_get_conversation_summary_empty(memory_manager, user_id):
    """
    Test getting a conversation summary when none exists.
    """
    summary = memory_manager.get_conversation_summary(user_id)
    assert summary is None


def test_update_and_get_conversation_summary(memory_manager, user_id):
    """
    Test updating and then getting a conversation summary.
    """
    test_summary = "This is a test summary"
    memory_manager.update_conversation_summary(user_id, test_summary)
    summary = memory_manager.get_conversation_summary(user_id)
    assert summary == test_summary


def test_get_last_symbol_empty(memory_manager, user_id):
    """
    Test getting a last symbol when none exists.
    """
    symbol = memory_manager.get_last_symbol(user_id)
    assert symbol is None


def test_update_and_get_last_symbol(memory_manager, user_id):
    """
    Test updating and then getting a last symbol.
    """
    test_symbol = "AAPL"
    memory_manager.update_last_symbol(user_id, test_symbol)
    symbol = memory_manager.get_last_symbol(user_id)
    assert symbol == test_symbol


def test_multiple_users(memory_manager):
    """
    Test that memory is isolated between different users.
    """
    user1 = "user1"
    user2 = "user2"

    # Set different summaries for different users
    memory_manager.update_conversation_summary(user1, "User 1 summary")
    memory_manager.update_conversation_summary(user2, "User 2 summary")

    # Set different symbols for different users
    memory_manager.update_last_symbol(user1, "AAPL")
    memory_manager.update_last_symbol(user2, "MSFT")

    # Verify each user gets their own data
    assert memory_manager.get_conversation_summary(user1) == "User 1 summary"
    assert memory_manager.get_conversation_summary(user2) == "User 2 summary"
    assert memory_manager.get_last_symbol(user1) == "AAPL"
    assert memory_manager.get_last_symbol(user2) == "MSFT"


def test_update_conversation_summary_overwrites(memory_manager, user_id):
    """
    Test that updating a conversation summary overwrites the previous value.
    """
    memory_manager.update_conversation_summary(user_id, "First summary")
    memory_manager.update_conversation_summary(user_id, "Second summary")

    summary = memory_manager.get_conversation_summary(user_id)
    assert summary == "Second summary"
    assert summary != "First summary"


def test_update_last_symbol_overwrites(memory_manager, user_id):
    """
    Test that updating a last symbol overwrites the previous value.
    """
    memory_manager.update_last_symbol(user_id, "AAPL")
    memory_manager.update_last_symbol(user_id, "MSFT")

    symbol = memory_manager.get_last_symbol(user_id)
    assert symbol == "MSFT"
    assert symbol != "AAPL"
