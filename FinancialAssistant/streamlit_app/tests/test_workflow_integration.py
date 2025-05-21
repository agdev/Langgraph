"""
Integration tests for the memory manager functionality.
"""

import pytest
from methods.memory_manager import MemoryManager


@pytest.fixture
def memory_manager():
    """
    Creates a real memory manager for integration testing.
    """
    return MemoryManager()


def test_memory_manager_conversation_summary(memory_manager):
    """
    Test that the memory manager can store and retrieve conversation summaries.
    """
    # Test user IDs
    user1 = "test_user_1"
    user2 = "test_user_2"
    
    # Test summaries
    summary1 = "User asked about Apple stock price."
    summary2 = "User asked about Microsoft financials."
    
    # Store summaries
    memory_manager.update_conversation_summary(user1, summary1)
    memory_manager.update_conversation_summary(user2, summary2)
    
    # Retrieve and verify summaries
    retrieved_summary1 = memory_manager.get_conversation_summary(user1)
    retrieved_summary2 = memory_manager.get_conversation_summary(user2)
    
    assert retrieved_summary1 == summary1
    assert retrieved_summary2 == summary2
    assert retrieved_summary1 != retrieved_summary2


def test_memory_manager_last_symbol(memory_manager):
    """
    Test that the memory manager can store and retrieve last used symbols.
    """
    # Test user IDs
    user1 = "test_user_1"
    user2 = "test_user_2"
    
    # Test symbols
    symbol1 = "AAPL"
    symbol2 = "MSFT"
    
    # Store symbols
    memory_manager.update_last_symbol(user1, symbol1)
    memory_manager.update_last_symbol(user2, symbol2)
    
    # Retrieve and verify symbols
    retrieved_symbol1 = memory_manager.get_last_symbol(user1)
    retrieved_symbol2 = memory_manager.get_last_symbol(user2)
    
    assert retrieved_symbol1 == symbol1
    assert retrieved_symbol2 == symbol2
    assert retrieved_symbol1 != retrieved_symbol2


def test_memory_manager_update_existing(memory_manager):
    """
    Test that the memory manager can update existing values.
    """
    # Test user ID
    user = "test_user"
    
    # Initial values
    initial_summary = "User asked about Apple."
    initial_symbol = "AAPL"
    
    # Updated values
    updated_summary = "User asked about Apple and then Microsoft."
    updated_symbol = "MSFT"
    
    # Store initial values
    memory_manager.update_conversation_summary(user, initial_summary)
    memory_manager.update_last_symbol(user, initial_symbol)
    
    # Verify initial values
    assert memory_manager.get_conversation_summary(user) == initial_summary
    assert memory_manager.get_last_symbol(user) == initial_symbol
    
    # Update values
    memory_manager.update_conversation_summary(user, updated_summary)
    memory_manager.update_last_symbol(user, updated_symbol)
    
    # Verify updated values
    assert memory_manager.get_conversation_summary(user) == updated_summary
    assert memory_manager.get_last_symbol(user) == updated_symbol


def test_memory_manager_nonexistent_values(memory_manager):
    """
    Test that the memory manager handles nonexistent values gracefully.
    """
    # Test user ID that doesn't exist
    nonexistent_user = "nonexistent_user"
    
    # Retrieve values for nonexistent user
    summary = memory_manager.get_conversation_summary(nonexistent_user)
    symbol = memory_manager.get_last_symbol(nonexistent_user)
    
    # Verify that None or empty string is returned
    assert summary is None or summary == ""
    assert symbol is None or symbol == ""
