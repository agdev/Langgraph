# Cross-Thread Memory Implementation Plan for Financial Assistant

## 1. Overview

This document outlines the plan to implement cross-thread memory functionality in the Financial Assistant application. This feature will allow nodes in the Langgraph workflow to access and share memory across different executions, enabling more contextual and personalized interactions with users.

## 2. Current Architecture

The Financial Assistant currently uses Langgraph for orchestrating the workflow with the following key components:

- **StateGraph**: Defines the structure of the workflow with nodes and edges
- **GraphState**: TypedDict that represents the state of the graph
- **MemorySaver**: Used for checkpointing to maintain conversation state across sessions
- **Nodes**: Various nodes for routing, symbol extraction, data retrieval, and report generation

Currently, the application maintains state within a single execution thread using the `MemorySaver` checkpointer, but there's no mechanism for sharing information across different execution threads or for maintaining long-term memory beyond the immediate conversation context.

## 3. Implementation Goals

1. Enable nodes to access shared memory across different execution threads
2. Implement conversation summarization to maintain context across sessions
3. Store and retrieve the last used symbol for improved user experience
4. Enhance the router node with conversation context for better intent determination

## 4. Technical Approach

### 4.1 Memory Structure Design

We will implement a new memory structure with the following components:

```python
# We will store conversation summaries directly in the InMemoryStore
# No need for a separate CrossThreadMemory class
```

### 4.2 Memory Storage Implementation

We will implement a memory storage mechanism using Langgraph's InMemoryStore, which provides a simple key-value store for cross-thread memory:

```python
from langgraph.store.memory import InMemoryStore

# Initialize the store
across_thread_memory = InMemoryStore()
```

The InMemoryStore provides the following key operations:

1. **put**: Save an object to the store by namespace and key
   ```python
   # Save a memory to namespace as key and value
   namespace = (user_id, "memories")
   key = "user_memory"
   value = {"conversation_summary": "User asked about Apple stock price"}
   store.put(namespace, key, value)
   ```

2. **get**: Retrieve an object by namespace and key
   ```python
   memory = store.get(namespace, key)
   ```

3. **search**: Retrieve objects from the store by namespace
   ```python
   memories = store.search(namespace)
   ```

### 4.3 Memory Manager Implementation

Create a dedicated memory manager class that inherits from InMemoryStore to handle all memory operations:

```python
from langgraph.store.memory import InMemoryStore
from typing import Optional

class MemoryManager(InMemoryStore):
    """
    Memory manager for cross-thread memory in Financial Assistant.
    Inherits from InMemoryStore to encapsulate all memory operations.
    """

    def __init__(self):
        super().__init__()

    def get_conversation_summary(self, user_id: str) -> Optional[str]:
        """
        Retrieves the conversation summary for a user.
        """
        namespace = (user_id, "memories")
        key = "conversation_summary"
        try:
            memory = self.get(namespace, key)
            return memory.value.get("summary", "")
        except:
            return None

    def update_conversation_summary(self, user_id: str, summary: str):
        """
        Updates the conversation summary for a user.
        """
        namespace = (user_id, "memories")
        key = "conversation_summary"
        self.put(namespace, key, {"summary": summary})

    def get_last_symbol(self, user_id: str) -> Optional[str]:
        """
        Retrieves the last used symbol for a user.
        """
        namespace = (user_id, "memories")
        key = "last_symbol"
        try:
            memory = self.get(namespace, key)
            return memory.value.get("symbol", "")
        except:
            return None

    def update_last_symbol(self, user_id: str, symbol: str):
        """
        Updates the last used symbol for a user.
        """
        namespace = (user_id, "memories")
        key = "last_symbol"
        self.put(namespace, key, {"symbol": symbol})
```

### 4.4 Integration with Langgraph

Modify the existing Langgraph workflow to incorporate the cross-thread memory:

1. **Keep GraphState the same as is**:
   - We will not modify the GraphState class
   - All cross-thread memory will be stored in the MemoryManager

2. **Update Symbol Extraction Nodes**:
   ```python
   def create_symbol_extraction_node(llm):
       chain = create_extraction_chain(llm)
       def symbol_extraction_node(state: GraphState, config: RunnableConfig, store: MemoryManager):
           # Get the user ID from the config
           user_id = config["configurable"]["user_id"]

           # Try to extract symbol from request
           symbol = "UNKNOWN"
           try:
               result = chain.invoke(state["request"])
               symbol = result.symbol
           except Exception as e:
               print("Error:", e)

           # If symbol is unknown, try to get the last used symbol
           if symbol == "UNKNOWN":
               # Use the store parameter which is the memory manager
               last_symbol = store.get_last_symbol(user_id)
               if last_symbol:
                   symbol = last_symbol

           return {"symbol": symbol}
       return symbol_extraction_node
   ```

3. **Update Router Node**:
   ```python
   def create_get_route_node(llm):
       # First, we need to update the route_chain.py to accept a conversation_summary parameter
       # Update the RouteResult class and prompt in route_chain.py
       chain = create_route_chain(llm)

       def get_route_node(state: GraphState, config: RunnableConfig, store: MemoryManager):
           # Get the user ID from the config
           user_id = config["configurable"]["user_id"]

           # Get conversation summary using the store parameter
           summary = store.get_conversation_summary(user_id) or ""

           # Pass the summary as a separate property
           result = chain.invoke({
               "request": state["request"],
               "conversation_summary": summary
           })

           return {"request_category": result.route}
       return get_route_node
   ```

4. **Update Chat Node**:
   ```python
   def create_chat_node(llm):
       # First, we need to update the chat_chain.py to accept a conversation_summary parameter
       # Update the ChatPromptTemplate in chat_chain.py
       chain = create_chat_chain(llm)

       def chat_node(state: GraphState, config: RunnableConfig, store: MemoryManager):
           # Get the user ID from the config
           user_id = config["configurable"]["user_id"]

           # Get conversation summary using the store parameter
           summary = store.get_conversation_summary(user_id) or ""

           # Pass the summary as a separate property
           result = chain.invoke({
               "request": state["request"],
               "conversation_summary": summary
           })

           return {"chat_response": result.response}
       return chat_node
   ```

5. **Add Summarization Node**:
   - Add the summarization node as the last node before the final answer
   - Connect it in the workflow to run after all other processing is complete

### 4.5 Summarization Chain Implementation

We will create a summarization chain to generate and update conversation summaries. This chain will be used by a dedicated summarization node that will be the last node before the final answer node:

```python
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.config import RunnableConfig
from langgraph.store.base import BaseStore

class SummarizationResult(BaseModel):
    """
    The result of the summarization chain.
    """
    summary: str = Field(description="Summarized conversation")

def create_summarization_chain(llm):
    """
    Creates a chain for summarizing conversations using the modern chain approach.
    """
    system_template = """
    You are an AI assistant tasked with summarizing financial conversations.

    Based on the conversation and any existing summary, create a concise summary
    that captures the key points of the conversation, focusing on:
    - Financial questions asked by the user
    - Specific companies or symbols mentioned
    - Types of financial information requested (stock prices, income statements, etc.)
    - Any preferences expressed by the user
    """

    summarization_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            ("human", "Previous summary: {existing_summary}\n\nConversation: {conversation}\n\nPlease provide an updated summary.")
        ]
    )

    # Create the chain using the pipe operator
    return summarization_prompt | llm.with_structured_output(SummarizationResult)

def summarize_conversation_node(state: GraphState, config: RunnableConfig, store: MemoryManager, summarization_chain):
    """
    Summarizes the conversation and updates the summary in the memory manager.
    This node should be placed right before the final answer node.
    """
    # Get the user ID from the config
    user_id = config["configurable"]["user_id"]

    # Get memory manager (assuming it's passed as store)
    memory_manager = store

    # Get existing summary
    existing_summary = memory_manager.get_conversation_summary(user_id) or "No previous summary available."

    # Format the conversation for summarization
    conversation = f"User: {state['request']}\nAssistant: {state['final_answer']}"

    # Prepare inputs for the summarization chain
    chain_inputs = {
        "existing_summary": existing_summary,
        "conversation": conversation
    }

    # Generate the summary
    result = summarization_chain.invoke(chain_inputs)
    summary = result.summary

    # Update the summary in memory
    memory_manager.update_conversation_summary(user_id, summary)

    # If there's a symbol in the state, update the last symbol
    if state.get("symbol") and state["symbol"] != "UNKNOWN":
        memory_manager.update_last_symbol(user_id, state["symbol"])

    # Return the state unchanged
    return state
```

This approach allows us to:
1. Maintain a running summary of the conversation
2. Use a dedicated chain for summarization with a specialized prompt
3. Update the last used symbol for future reference
4. Place the summarization as the last step before returning the final answer

## 5. Implementation Steps

1. **Phase 1: Memory Manager Implementation**
   - Create the MemoryManager class that inherits from InMemoryStore
   - Implement methods for conversation summary and last symbol management

2. **Phase 2: Summarization Chain Implementation**
   - Create a specialized chain for conversation summarization
   - Implement the summarization node that uses this chain

3. **Phase 3: Node Modifications**
   - Update the symbol extraction nodes to use last symbol from memory
   - Enhance the router node to use conversation summary for context
   - Add the summarization node to the workflow

4. **Phase 4: Workflow Integration**
   - Update the workflow to include the summarization node
   - Configure the workflow to use the MemoryManager as the store
   - Ensure proper user_id is passed in the config

5. **Phase 5: Testing and Optimization**
   - Test memory persistence across different sessions
   - Verify symbol recall functionality
   - Ensure conversation context is properly maintained

## 6. Code Changes

### 6.1 Create memory_manager.py

```python
from langgraph.store.memory import InMemoryStore
from typing import Optional

class MemoryManager(InMemoryStore):
    """
    Memory manager for cross-thread memory in Financial Assistant.
    Inherits from InMemoryStore to encapsulate all memory operations.
    """

    def __init__(self):
        super().__init__()

    def get_conversation_summary(self, user_id: str) -> Optional[str]:
        """
        Retrieves the conversation summary for a user.
        """
        namespace = (user_id, "memories")
        key = "conversation_summary"
        try:
            memory = self.get(namespace, key)
            return memory.value.get("summary", "")
        except:
            return None

    def update_conversation_summary(self, user_id: str, summary: str):
        """
        Updates the conversation summary for a user.
        """
        namespace = (user_id, "memories")
        key = "conversation_summary"
        self.put(namespace, key, {"summary": summary})

    def get_last_symbol(self, user_id: str) -> Optional[str]:
        """
        Retrieves the last used symbol for a user.
        """
        namespace = (user_id, "memories")
        key = "last_symbol"
        try:
            memory = self.get(namespace, key)
            return memory.value.get("symbol", "")
        except:
            return None

    def update_last_symbol(self, user_id: str, symbol: str):
        """
        Updates the last used symbol for a user.
        """
        namespace = (user_id, "memories")
        key = "last_symbol"
        self.put(namespace, key, {"symbol": symbol})
```

### 6.2 Update route_chain.py

```python
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

class RouteResult(BaseModel):
    """
    The result of the route chain.
    """
    route: str = Field(description="The route to take")

system_route = """
    You are a helpful assistant that routes user requests to the appropriate category.

    If the user is asking about a company's stock price, price-to-earnings ratio, or other stock metrics, route to 'stock_price'.
    If the user is asking about a company's income statement, revenue, profit, or earnings, route to 'income_statement'.
    If the user is asking about a company's general information, industry, or overview, route to 'company_financials'.
    If the user is asking for a comprehensive report on a company, route to 'report'.
    If the user is asking a general question not related to specific financial data, route to 'chat'.

    If there is a conversation summary available, use it to provide context for understanding the user's request.
"""

route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_route),
        ("human", "Conversation summary: {conversation_summary}\n\nUser request: {request}\n\nWhat category should this request be routed to?")
    ]
)

def create_route_chain(llm):
    """
    Creates a route chain using the given LLM.
    """
    return route_prompt | llm.with_structured_output(RouteResult)
```

### 6.3 Update chat_chain.py

```python
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

class ChatResult(BaseModel):
    """
    The result of the chat chain.
    """
    response: str = Field(description="LLM's response")

system_chat = """
    You are a very helpful Assistant, you are to answer user's request to the best of your ability. If you do not know, respond with 'I do not know'.

    If there is a conversation summary available, use it to provide context for understanding the user's request and to maintain continuity in the conversation.
"""

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_chat),
        ("human", "Conversation summary: {conversation_summary}\n\nUser request: {request}")
    ]
)

def create_chat_chain(llm):
    """
    Creates a chat chain using the given LLM.
    """
    return chat_prompt | llm.with_structured_output(ChatResult)
```

### 6.4 Create summarization_chain.py

```python
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

class SummarizationResult(BaseModel):
    """
    The result of the summarization chain.
    """
    summary: str = Field(description="Summarized conversation")

def create_summarization_chain(llm):
    """
    Creates a chain for summarizing conversations using the modern chain approach.
    """
    system_template = """
    You are an AI assistant tasked with summarizing financial conversations.

    Based on the conversation and any existing summary, create a concise summary
    that captures the key points of the conversation, focusing on:
    - Financial questions asked by the user
    - Specific companies or symbols mentioned
    - Types of financial information requested (stock prices, income statements, etc.)
    - Any preferences expressed by the user
    """

    summarization_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            ("human", "Previous summary: {existing_summary}\n\nConversation: {conversation}\n\nPlease provide an updated summary.")
        ]
    )

    # Create the chain using the pipe operator
    return summarization_prompt | llm.with_structured_output(SummarizationResult)
```

### 6.5 Create summarization_node.py

```python
from graph.graph_state import GraphState
from methods.memory_manager import MemoryManager
from chains.summarization_chain import create_summarization_chain
from langchain_core.runnables.config import RunnableConfig

def create_summarization_node(llm):
    """
    Creates a node for summarizing conversations and updating memory.
    This node should be placed right before the final answer node.
    """
    # Create the summarization chain
    summarization_chain = create_summarization_chain(llm)

    def summarization_node(state: GraphState, config: RunnableConfig, store: MemoryManager):
        """
        Summarizes the conversation and updates the summary in the memory manager.
        """
        # Get the user ID from the config
        user_id = config["configurable"]["user_id"]

        # Get existing summary using the store parameter
        existing_summary = store.get_conversation_summary(user_id) or "No previous summary available."

        # Format the conversation for summarization
        conversation = f"User: {state['request']}\nAssistant: {state['final_answer']}"

        # Prepare inputs for the summarization chain
        chain_inputs = {
            "existing_summary": existing_summary,
            "conversation": conversation
        }

        # Generate the summary
        result = summarization_chain.invoke(chain_inputs)
        summary = result.summary

        # Update the summary in memory using the store parameter
        store.update_conversation_summary(user_id, summary)

        # If there's a symbol in the state, update the last symbol using the store parameter
        if state.get("symbol") and state["symbol"] != "UNKNOWN":
            store.update_last_symbol(user_id, state["symbol"])

        # Return the state unchanged
        return state

    return summarization_node
```

### 6.4 Update work_flow.py

```python
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from consts.consts import (
    NODE_STOCK_PRICE, NODE_INCOME_STATEMENT,
    NODE_COMPANY_FINANCIALS, NODE_ERROR, NODE_REPORT, NODE_PASS,
    NODE_ROUTER, NODE_SYMBOL_EXTRACTION_REPORT, NODE_SYMBOL_EXTRACTION_ALONE,
    NODE_STOCK_PRICE_STAND_ALONE, NODE_INCOME_STATEMENT_STAND_ALONE,
    NODE_COMPANY_FINANCIALS_STAND_ALONE, NODE_CHAT, NODE_FINAL_ANSWER, NODE_GENERATE_REPORT,
    NODE_SUMMARIZE  # New node constant
)
from graph.graph_state import GraphState
from graph.nodes import get_income_statement_node, get_company_financials_node, get_stock_price_node, error_node, generate_markdown_report_node, is_there_symbol, create_get_route_node, create_chat_node, where_to, where_to_alone, final_answer_node, create_symbol_extraction_node
from methods.memory_manager import MemoryManager
from graph.summarization_node import create_summarization_node

# Create a global memory manager instance
memory_manager = MemoryManager()

def create_workflow(llm):
    workflow = StateGraph(GraphState)

    # Create node factories
    router_node_factory = create_get_route_node(llm)
    symbol_extraction_node_factory = create_symbol_extraction_node(llm)
    chat_node_factory = create_chat_node(llm)
    summarization_node_factory = create_summarization_node(llm, memory_manager)

    # Create wrapper functions that only take state parameter
    # These wrappers are needed because StateGraph expects functions that only take a state parameter,
    # but our node functions need config and store parameters to access the user_id and memory
    def router_node(state):
        # The user_id is passed in the config when invoking the workflow
        # We don't need to extract it from the state
        return router_node_factory(state, None, memory_manager)

    def symbol_extraction_report_node(state):
        return symbol_extraction_node_factory(state, None, memory_manager)

    def symbol_extraction_alone_node(state):
        return symbol_extraction_node_factory(state, None, memory_manager)

    def chat_node(state):
        return chat_node_factory(state, None, memory_manager)

    def summarization_node(state):
        return summarization_node_factory(state, None, memory_manager)

    # Add nodes to workflow
    workflow.add_node(NODE_ROUTER, router_node)
    workflow.add_node(NODE_SYMBOL_EXTRACTION_REPORT, symbol_extraction_report_node)
    workflow.add_node(NODE_SYMBOL_EXTRACTION_ALONE, symbol_extraction_alone_node)
    workflow.add_node(NODE_CHAT, chat_node)
    workflow.add_node(NODE_SUMMARIZE, summarization_node)

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

    # Add conditional edges
    workflow.add_conditional_edges(NODE_ROUTER, where_to, path_map={
        'report': NODE_SYMBOL_EXTRACTION_REPORT,
        'alone': NODE_SYMBOL_EXTRACTION_ALONE,
        'chat': NODE_CHAT
    })

    workflow.add_conditional_edges(NODE_SYMBOL_EXTRACTION_REPORT, is_there_symbol, {True: NODE_PASS, False: NODE_ERROR})
    workflow.add_conditional_edges(NODE_SYMBOL_EXTRACTION_ALONE, where_to_alone, {
        'error': NODE_ERROR,
        'income_statement': NODE_INCOME_STATEMENT_STAND_ALONE,
        'company_financials': NODE_COMPANY_FINANCIALS_STAND_ALONE,
        'stock_price': NODE_STOCK_PRICE_STAND_ALONE,
    })

    # Add regular edges
    workflow.add_edge(NODE_PASS, NODE_INCOME_STATEMENT)
    workflow.add_edge(NODE_PASS, NODE_COMPANY_FINANCIALS)
    workflow.add_edge(NODE_PASS, NODE_STOCK_PRICE)

    workflow.add_edge(NODE_INCOME_STATEMENT, NODE_GENERATE_REPORT)
    workflow.add_edge(NODE_COMPANY_FINANCIALS, NODE_GENERATE_REPORT)
    workflow.add_edge(NODE_STOCK_PRICE, NODE_GENERATE_REPORT)

    workflow.add_edge(NODE_GENERATE_REPORT, NODE_FINAL_ANSWER)
    workflow.add_edge(NODE_ERROR, NODE_FINAL_ANSWER)

    workflow.add_edge(NODE_INCOME_STATEMENT_STAND_ALONE, NODE_FINAL_ANSWER)
    workflow.add_edge(NODE_COMPANY_FINANCIALS_STAND_ALONE, NODE_FINAL_ANSWER)
    workflow.add_edge(NODE_STOCK_PRICE_STAND_ALONE, NODE_FINAL_ANSWER)
    workflow.add_edge(NODE_CHAT, NODE_FINAL_ANSWER)

    # Add summarization node before END
    workflow.add_edge(NODE_FINAL_ANSWER, NODE_SUMMARIZE)
    workflow.add_edge(NODE_SUMMARIZE, END)

    # Use a checkpointer for within-thread memory
    within_thread_memory = MemorySaver()

    # Compile with both within-thread and across-thread memory
    app = workflow.compile(checkpointer=within_thread_memory, store=memory_manager)
    return app
```

## 7. Testing Plan

### 7.1 Unit Tests

```python
import pytest
from unittest.mock import MagicMock, patch
from methods.memory_manager import MemoryManager
from chains.summarization_chain import create_summarization_chain, SummarizationResult
from graph.summarization_node import create_summarization_node
from graph.nodes import create_symbol_extraction_node, create_get_route_node, create_chat_node
from graph.graph_state import GraphState
from langchain_core.runnables.config import RunnableConfig

# Fixtures
@pytest.fixture
def memory_manager():
    return MemoryManager()

@pytest.fixture
def user_id():
    return "test_user"

@pytest.fixture
def state_with_symbol():
    return GraphState({
        "request": "Tell me about Apple",
        "final_answer": "Apple Inc. is a technology company that makes iPhones.",
        "symbol": "AAPL"
    })

@pytest.fixture
def state_without_symbol():
    return GraphState({"request": "What's the latest on that tech company?"})

@pytest.fixture
def config():
    return {"configurable": {"user_id": "test_user"}}

@pytest.fixture
def mock_llm():
    return MagicMock()

@pytest.fixture
def mock_store():
    store = MagicMock()
    store.get_conversation_summary.return_value = "Previous summary"
    store.get_last_symbol.return_value = "AAPL"
    return store

# Memory Manager Tests
def test_get_conversation_summary_empty(memory_manager, user_id):
    # Test getting a summary when none exists
    summary = memory_manager.get_conversation_summary(user_id)
    assert summary is None

def test_update_and_get_conversation_summary(memory_manager, user_id):
    # Test updating and then getting a summary
    test_summary = "This is a test summary"
    memory_manager.update_conversation_summary(user_id, test_summary)
    summary = memory_manager.get_conversation_summary(user_id)
    assert summary == test_summary

def test_get_last_symbol_empty(memory_manager, user_id):
    # Test getting a symbol when none exists
    symbol = memory_manager.get_last_symbol(user_id)
    assert symbol is None

def test_update_and_get_last_symbol(memory_manager, user_id):
    # Test updating and then getting a symbol
    test_symbol = "AAPL"
    memory_manager.update_last_symbol(user_id, test_symbol)
    symbol = memory_manager.get_last_symbol(user_id)
    assert symbol == test_symbol

# Summarization Node Tests
@pytest.fixture
def mock_summarization_chain():
    chain = MagicMock()
    chain.invoke.return_value = SummarizationResult(summary="User asked about Apple Inc.")
    return chain

@pytest.fixture
def summarization_node_factory(mock_llm, mock_summarization_chain):
    with patch('chains.summarization_chain.create_summarization_chain', return_value=mock_summarization_chain):
        yield create_summarization_node(mock_llm, MagicMock())

def test_summarization_node(summarization_node_factory, state_with_symbol, config, mock_store):
    # Call the node
    result = summarization_node_factory(state_with_symbol, config, mock_store)

    # Verify the chain was called with the right inputs
    mock_store.get_conversation_summary.assert_called_once_with("test_user")

    # Verify the store was updated
    mock_store.update_conversation_summary.assert_called_once_with("test_user", "User asked about Apple Inc.")
    mock_store.update_last_symbol.assert_called_once_with("test_user", "AAPL")

    # Verify the state is unchanged
    assert result == state_with_symbol

# Symbol Extraction Node Tests
@pytest.fixture
def mock_extraction_chain():
    chain = MagicMock()
    result = MagicMock()
    result.symbol = "UNKNOWN"  # Default to unknown, can be changed in tests
    chain.invoke.return_value = result
    return chain, result

@pytest.fixture
def symbol_extraction_node_factory(mock_llm, mock_extraction_chain):
    chain, _ = mock_extraction_chain
    with patch('chains.extraction_chain.create_extraction_chain', return_value=chain):
        yield create_symbol_extraction_node(mock_llm, MagicMock())

def test_symbol_extraction_with_fallback(symbol_extraction_node_factory, state_without_symbol, config, mock_store):
    # Call the node
    result = symbol_extraction_node_factory(state_without_symbol, config, mock_store)

    # Verify the store was queried for the last symbol
    mock_store.get_last_symbol.assert_called_once_with("test_user")

    # Verify the result contains the fallback symbol
    assert result["symbol"] == "AAPL"

def test_symbol_extraction_without_fallback(symbol_extraction_node_factory, state_without_symbol, config, mock_extraction_chain):
    # Set up the extraction chain to return a valid symbol
    _, mock_result = mock_extraction_chain
    mock_result.symbol = "MSFT"

    # Create a store that won't be called
    store = MagicMock()

    # Call the node
    result = symbol_extraction_node_factory(state_without_symbol, config, store)

    # Verify the store was not queried for the last symbol
    store.get_last_symbol.assert_not_called()

    # Verify the result contains the extracted symbol
    assert result["symbol"] == "MSFT"

# Router Node Tests
@pytest.fixture
def router_state():
    return GraphState({"request": "Tell me about Apple's stock price"})

@pytest.fixture
def mock_route_chain():
    chain = MagicMock()
    result = MagicMock()
    result.route = "stock_price"
    chain.invoke.return_value = result
    return chain

@pytest.fixture
def router_node_factory(mock_llm, mock_route_chain):
    with patch('chains.route_chain.create_route_chain', return_value=mock_route_chain):
        yield create_get_route_node(mock_llm, MagicMock())

def test_router_node_with_summary(router_node_factory, router_state, config, mock_store):
    # Set up the store to return a specific summary
    mock_store.get_conversation_summary.return_value = "User previously asked about Apple's financials."

    # Call the node
    result = router_node_factory(router_state, config, mock_store)

    # Verify the store was queried for the conversation summary
    mock_store.get_conversation_summary.assert_called_once_with("test_user")

    # Verify the result contains the correct route
    assert result["request_category"] == "stock_price"

# Chat Node Tests
@pytest.fixture
def chat_state():
    return GraphState({"request": "What's the best tech stock to buy?"})

@pytest.fixture
def mock_chat_chain():
    chain = MagicMock()
    result = MagicMock()
    result.response = "It depends on your investment goals."
    chain.invoke.return_value = result
    return chain

@pytest.fixture
def chat_node_factory(mock_llm, mock_chat_chain):
    with patch('chains.chat_chain.create_chat_chain', return_value=mock_chat_chain):
        yield create_chat_node(mock_llm, MagicMock())

def test_chat_node_with_summary(chat_node_factory, chat_state, config, mock_store):
    # Set up the store to return a specific summary
    mock_store.get_conversation_summary.return_value = "User previously asked about investment strategies."

    # Call the node
    result = chat_node_factory(chat_state, config, mock_store)

    # Verify the store was queried for the conversation summary
    mock_store.get_conversation_summary.assert_called_once_with("test_user")

    # Verify the result contains the correct response
    assert result["chat_response"] == "It depends on your investment goals."
```

### 7.2 Integration Tests

```python
import pytest
from unittest.mock import MagicMock
from methods.memory_manager import MemoryManager
from graph.work_flow import create_workflow
from langchain_core.language_models import BaseLLM

class MockLLM(BaseLLM):
    def __init__(self, responses):
        super().__init__()
        self.responses = responses
        self.call_count = 0

    def invoke(self, prompt, **kwargs):
        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        return response

@pytest.fixture
def mock_responses():
    return {
        "RouteResult": [{"route": "chat"}, {"route": "stock_price"}],
        "Extraction": [{"symbol": "AAPL"}, {"symbol": "UNKNOWN"}],
        "ChatResult": [{"response": "Apple is a technology company."}, {"response": "The stock price is high."}],
        "SummarizationResult": [{"summary": "User asked about Apple."}, {"summary": "User asked about Apple and its stock price."}]
    }

@pytest.fixture
def mock_llm(mock_responses):
    llm = MagicMock()

    def side_effect(cls):
        class_name = cls.__name__
        responses = mock_responses.get(class_name, ["Unknown response"])
        return MockLLM(responses)

    llm.with_structured_output.side_effect = side_effect
    return llm

@pytest.fixture
def memory_manager():
    return MemoryManager()

@pytest.fixture
def workflow(mock_llm, memory_manager):
    return create_workflow(mock_llm)

def test_workflow_with_memory(workflow, memory_manager):
    # First request - should use the chat route
    result1 = workflow.invoke({"request": "Tell me about Apple", "user_id": "test_user"})

    # Verify the result
    assert result1["request_category"] == "chat"
    assert result1["chat_response"] == "Apple is a technology company."

    # Verify the memory was updated
    summary = memory_manager.get_conversation_summary("test_user")
    assert summary == "User asked about Apple."

    # Second request - should use the stock_price route and remember the symbol
    result2 = workflow.invoke({"request": "What's the stock price?", "user_id": "test_user"})

    # Verify the result
    assert result2["request_category"] == "stock_price"
    assert result2["symbol"] == "AAPL"  # Should use the remembered symbol

    # Verify the memory was updated
    summary = memory_manager.get_conversation_summary("test_user")
    assert summary == "User asked about Apple and its stock price."
```

### 7.3 End-to-End Tests

```python
import pytest
from methods.memory_manager import MemoryManager
from graph.work_flow import create_workflow
from langchain_openai import ChatOpenAI

@pytest.fixture(scope="module")
def real_llm():
    # Use a real LLM for end-to-end tests
    return ChatOpenAI()

@pytest.fixture(scope="module")
def memory_manager():
    return MemoryManager()

@pytest.fixture(scope="module")
def workflow(real_llm, memory_manager):
    return create_workflow(real_llm)

@pytest.mark.e2e
def test_conversation_summary_persistence(workflow, memory_manager):
    # First request about a company
    user_id = "e2e_test_user"
    result1 = workflow.invoke({"request": "Tell me about Microsoft", "user_id": user_id})

    # Verify a summary was created
    summary1 = memory_manager.get_conversation_summary(user_id)
    assert summary1 is not None
    assert "Microsoft" in summary1

    # Second request that doesn't mention the company
    result2 = workflow.invoke({"request": "What's their stock price?", "user_id": user_id})

    # Verify the symbol was remembered
    assert result2["symbol"] == "MSFT"

    # Verify the summary was updated
    summary2 = memory_manager.get_conversation_summary(user_id)
    assert summary2 is not None
    assert summary2 != summary1  # Summary should have been updated
    assert "stock price" in summary2.lower()

@pytest.mark.e2e
def test_router_with_context(workflow, memory_manager):
    # First request about investments
    user_id = "e2e_test_user2"
    result1 = workflow.invoke({"request": "I'm interested in tech stocks", "user_id": user_id})

    # Second request that's ambiguous but should be routed correctly with context
    result2 = workflow.invoke({"request": "What do you recommend?", "user_id": user_id})

    # Verify it was routed to chat (not something else) because of the context
    assert result2["request_category"] == "chat"
    assert "tech" in result2["chat_response"].lower() or "stock" in result2["chat_response"].lower()
```

## 8. Conclusion

Implementing cross-thread memory in the Financial Assistant will significantly enhance the user experience by providing more contextual and personalized interactions. The proposed approach leverages Langgraph's InMemoryStore for cross-thread memory and implements conversation summarization to maintain context across different sessions.

Key benefits of this implementation include:

1. **Simplified Memory Architecture**: By having the MemoryManager inherit from InMemoryStore, we've created a clean, focused implementation that encapsulates all memory operations.

2. **Improved Symbol Extraction**: The system will remember the last used symbol, allowing for more natural follow-up questions about the same company.

3. **Enhanced Routing and Chat**: Both the router and chat nodes will use conversation summaries to better understand the context of user requests, providing more coherent and contextually relevant responses.

4. **Comprehensive Context Awareness**: By integrating memory into multiple nodes (router, symbol extraction, and chat), we ensure that the entire system benefits from the conversation history.

5. **Efficient Memory Management**: By summarizing conversations and storing only essential information, we prevent memory bloat while preserving context.

This implementation follows best practices from Langchain Academy, particularly the approaches demonstrated in the memory store and conversation summarization modules. By focusing on the essential functionality of maintaining conversation context across different sessions, we've created a streamlined solution that can be easily extended in the future if needed.


