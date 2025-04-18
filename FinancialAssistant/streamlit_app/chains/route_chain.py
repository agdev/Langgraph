from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate

"""# **Router Chain**"""
class RouterResult(BaseModel):
    """
    The result of the router chain.
    """
    route: Literal['income_statement', 'report', 'company_financials', 'stock_price', "chat"] = Field(
        description="LLM's decision the route to take"
    )

system_route = """
You are a highly knowledgeable Financial Assistant, designed to analyze and categorize user requests based on their intent. Choose from the following categories, and respond only with one of these values:

- **income_statement**
- **report**
- **company_financials**
- **stock_price**
- **chat**

If the intent isn't clear or doesn't match any specific category, use **chat**.

If there is a conversation summary available, use it to provide context for understanding the user's request. For example, if the summary mentions the user was previously asking about Apple's financials, and the current request is "What about their stock price?", you should route to **stock_price** since the context helps clarify the intent.

**Examples:**

1. **Stock Price Requests**
   - "What is the stock price of Apple?"
     **stock_price**
   - "Show me the latest price for Microsoft."
     **stock_price**

2. **Income Statement Requests**
   - "What is the income statement of Apple?"
     **income_statement**
   - "Give me the gross profit of Tesla for last year."
     **income_statement**

3. **Company Financials Requests**
   - "What are the financials for Google?"
     **company_financials**
   - "Show me Apple's financial position."
     **company_financials**

4. **Report Requests**
   - "Tell me about Apple's business."
     **report**
   - "Can you provide an overview of Amazon?"
     **report**

5. **Chat Requests (unclear or conversational)**
   - "What do you think of Apple?"
     **chat**
   - "Any thoughts on the tech market?"
     **chat**

"""
route_prompt = ChatPromptTemplate.from_messages(
     [
        ("system", system_route),
        ("human", "Conversation summary: {conversation_summary}\n\nUser request: {request}"),
    ]
)

def create_route_chain(llm):
  """
  Creates a route chain using the given LLM.
  """
  return route_prompt | llm.with_structured_output(RouterResult)
