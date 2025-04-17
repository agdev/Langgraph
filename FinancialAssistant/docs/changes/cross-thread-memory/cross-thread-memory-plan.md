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
   def create_symbol_extraction_node(llm, memory_manager):
       chain = create_extraction_chain(llm)
       def symbol_extraction_node(state: GraphState, config: RunnableConfig, store: BaseStore):
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
               last_symbol = memory_manager.get_last_symbol(user_id)
               if last_symbol:
                   symbol = last_symbol

           return {"symbol": symbol}
       return symbol_extraction_node
   ```

3. **Update Router Node**:
   ```python
   def create_get_route_node(llm, memory_manager):
       chain = create_route_chain(llm)

       def get_route_node(state: GraphState, config: RunnableConfig, store: BaseStore):
           # Get the user ID from the config
           user_id = config["configurable"]["user_id"]

           # Get conversation summary
           summary = memory_manager.get_conversation_summary(user_id) or ""

           # Create a context-enhanced request
           context_request = state["request"]
           if summary:
               context_request = f"Context from previous conversations: {summary}\n\nCurrent request: {state['request']}"

           # Invoke the routing chain with the enhanced context
           result = chain.invoke({"request": context_request})

           return {"request_category": result.route}
       return get_route_node
   ```

4. **Add Summarization Node**:
   - Add the summarization node as the last node before the final answer
   - Connect it in the workflow to run after all other processing is complete

### 4.5 Summarization Chain Implementation

We will create a summarization chain to generate and update conversation summaries. This chain will be used by a dedicated summarization node that will be the last node before the final answer node:

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_core.runnables.config import RunnableConfig
from langgraph.store.base import BaseStore

def create_summarization_chain(llm):
    """
    Creates a chain for summarizing conversations.
    """
    summarization_template = """
    You are an AI assistant tasked with summarizing financial conversations.

    {existing_summary_prefix}:
    {existing_summary}

    Conversation:
    {conversation}

    Based on the conversation above and any existing summary, create a concise summary
    that captures the key points of the conversation, focusing on:
    - Financial questions asked by the user
    - Specific companies or symbols mentioned
    - Types of financial information requested (stock prices, income statements, etc.)
    - Any preferences expressed by the user

    Summary:
    """

    prompt = PromptTemplate(
        input_variables=["existing_summary", "existing_summary_prefix", "conversation"],
        template=summarization_template
    )

    return LLMChain(llm=llm, prompt=prompt)

def summarize_conversation_node(state: GraphState, config: RunnableConfig, store: BaseStore, summarization_chain):
    """
    Summarizes the conversation and updates the summary in the memory manager.
    This node should be placed right before the final answer node.
    """
    # Get the user ID from the config
    user_id = config["configurable"]["user_id"]

    # Get memory manager (assuming it's passed as store)
    memory_manager = store

    # Get existing summary
    existing_summary = memory_manager.get_conversation_summary(user_id) or ""

    # Format the conversation for summarization
    conversation = f"User: {state['request']}\nAssistant: {state['final_answer']}"

    # Prepare inputs for the summarization chain
    chain_inputs = {
        "existing_summary": existing_summary,
        "existing_summary_prefix": "Previous conversation summary" if existing_summary else "No previous summary",
        "conversation": conversation
    }

    # Generate the summary
    result = summarization_chain.invoke(chain_inputs)
    summary = result["text"]

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

### 6.2 Create summarization_chain.py

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def create_summarization_chain(llm):
    """
    Creates a chain for summarizing conversations.
    """
    summarization_template = """
    You are an AI assistant tasked with summarizing financial conversations.

    {existing_summary_prefix}:
    {existing_summary}

    Conversation:
    {conversation}

    Based on the conversation above and any existing summary, create a concise summary
    that captures the key points of the conversation, focusing on:
    - Financial questions asked by the user
    - Specific companies or symbols mentioned
    - Types of financial information requested (stock prices, income statements, etc.)
    - Any preferences expressed by the user

    Summary:
    """

    prompt = PromptTemplate(
        input_variables=["existing_summary", "existing_summary_prefix", "conversation"],
        template=summarization_template
    )

    return LLMChain(llm=llm, prompt=prompt)
```

### 6.3 Create summarization_node.py

```python
from graph.graph_state import GraphState
from methods.memory_manager import MemoryManager
from chains.summarization_chain import create_summarization_chain
from langgraph_core.runnables.config import RunnableConfig
from langgraph.store.base import BaseStore

def create_summarization_node(llm, memory_manager):
    """
    Creates a node for summarizing conversations and updating memory.
    This node should be placed right before the final answer node.
    """
    # Create the summarization chain
    summarization_chain = create_summarization_chain(llm)

    def summarization_node(state: GraphState, config: RunnableConfig, store: BaseStore):
        """
        Summarizes the conversation and updates the summary in the memory manager.
        """
        # Get the user ID from the config
        user_id = config["configurable"]["user_id"]

        # Get existing summary
        existing_summary = memory_manager.get_conversation_summary(user_id) or ""

        # Format the conversation for summarization
        conversation = f"User: {state['request']}\nAssistant: {state['final_answer']}"

        # Prepare inputs for the summarization chain
        chain_inputs = {
            "existing_summary": existing_summary,
            "existing_summary_prefix": "Previous conversation summary" if existing_summary else "No previous summary",
            "conversation": conversation
        }

        # Generate the summary
        result = summarization_chain.invoke(chain_inputs)
        summary = result["text"]

        # Update the summary in memory
        memory_manager.update_conversation_summary(user_id, summary)

        # If there's a symbol in the state, update the last symbol
        if state.get("symbol") and state["symbol"] != "UNKNOWN":
            memory_manager.update_last_symbol(user_id, state["symbol"])

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

    # Create nodes with memory manager
    workflow.add_node(NODE_ROUTER, create_get_route_node(llm, memory_manager))
    workflow.add_node(NODE_SYMBOL_EXTRACTION_REPORT, create_symbol_extraction_node(llm, memory_manager))
    workflow.add_node(NODE_SYMBOL_EXTRACTION_ALONE, create_symbol_extraction_node(llm, memory_manager))

    # Add the summarization node
    workflow.add_node(NODE_SUMMARIZE, create_summarization_node(llm, memory_manager))

    # Add other existing nodes
    workflow.add_node(NODE_PASS, lambda state: state)
    workflow.add_node(NODE_INCOME_STATEMENT, get_income_statement_node)
    workflow.add_node(NODE_COMPANY_FINANCIALS, get_company_financials_node)
    workflow.add_node(NODE_STOCK_PRICE, get_stock_price_node)
    workflow.add_node(NODE_INCOME_STATEMENT_STAND_ALONE, get_income_statement_node)
    workflow.add_node(NODE_COMPANY_FINANCIALS_STAND_ALONE, get_company_financials_node)
    workflow.add_node(NODE_STOCK_PRICE_STAND_ALONE, get_stock_price_node)
    workflow.add_node(NODE_CHAT, create_chat_node(llm))
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

1. **Unit Tests**:
   - Test MemoryManager functionality
   - Test summarization chain
   - Test symbol extraction with memory fallback

2. **Integration Tests**:
   - Test memory persistence across different sessions
   - Test conversation summarization
   - Test symbol recall functionality

3. **End-to-End Tests**:
   - Test the complete workflow with memory integration
   - Verify that past interactions influence current responses
   - Ensure last symbol is properly used when needed

## 8. Conclusion

Implementing cross-thread memory in the Financial Assistant will significantly enhance the user experience by providing more contextual and personalized interactions. The proposed approach leverages Langgraph's InMemoryStore for cross-thread memory and implements conversation summarization to maintain context across different sessions.

Key benefits of this implementation include:

1. **Simplified Memory Architecture**: By having the MemoryManager inherit from InMemoryStore, we've created a clean, focused implementation that encapsulates all memory operations.

2. **Improved Symbol Extraction**: The system will remember the last used symbol, allowing for more natural follow-up questions about the same company.

3. **Enhanced Routing**: The router node will use conversation summaries to better understand the context of user requests.

4. **Efficient Memory Management**: By summarizing conversations and storing only essential information, we prevent memory bloat while preserving context.

This implementation follows best practices from Langchain Academy, particularly the approaches demonstrated in the memory store and conversation summarization modules. By focusing on the essential functionality of maintaining conversation context across different sessions, we've created a streamlined solution that can be easily extended in the future if needed.


