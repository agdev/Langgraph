"""
Memory Manager for cross-thread memory in Financial Assistant.

This module provides a MemoryManager class that inherits from InMemoryStore
to handle cross-thread memory operations, including conversation summaries
and last used symbols.
"""

from typing import Optional
from langgraph.store.base import Item
from langgraph.store.memory import InMemoryStore


class MemoryManager(InMemoryStore):
    """
    Memory manager for cross-thread memory in Financial Assistant.
    Inherits from InMemoryStore to encapsulate all memory operations.
    
    This class provides methods to store and retrieve conversation summaries
    and last used symbols across different execution threads.
    """
    
    def __init__(self):
        """Initialize the MemoryManager with an InMemoryStore."""
        super().__init__()
    
    def __get_key__(self, namespace: tuple[str,...], key: str, key_value: str) -> str | None:
        
        try:
            memory: Item | None = self.get(namespace, key)
            if memory is None:
                return None
            return memory.value.get(key_value, "")
        except:
            return None

    def get_conversation_summary(self, user_id: str) -> Optional[str]:
        """
        Retrieve the conversation summary for a user.
        
        Args:
            user_id: The ID of the user whose summary to retrieve
            
        Returns:
            The conversation summary as a string, or None if no summary exists
        """
        namespace = (user_id, "memories")
        key = "conversation_summary"
        return self.__get_key__(namespace, key, "summary")
    
    def update_conversation_summary(self, user_id: str, summary: str) -> None:
        """
        Update the conversation summary for a user.
        
        Args:
            user_id: The ID of the user whose summary to update
            summary: The new conversation summary
        """
        namespace = (user_id, "memories")
        key = "conversation_summary"
        self.put(namespace, key, {"summary": summary})
    
    def get_last_symbol(self, user_id: str) -> Optional[str]:
        """
        Retrieve the last used symbol for a user.
        
        Args:
            user_id: The ID of the user whose last symbol to retrieve
            
        Returns:
            The last used symbol as a string, or None if no symbol exists
        """
        namespace = (user_id, "memories")
        key = "last_symbol"
        return self.__get_key__(namespace, key, "symbol")   
        
    def update_last_symbol(self, user_id: str, symbol: str) -> None:
        """
        Update the last used symbol for a user.
        
        Args:
            user_id: The ID of the user whose last symbol to update
            symbol: The new symbol
        """
        namespace = (user_id, "memories")
        key = "last_symbol"
        self.put(namespace, key, {"symbol": symbol})
