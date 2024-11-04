
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

"""# **Chat chain**"""
class ChatResult(BaseModel):
  """
  The result of the chat chain.
  """
  response: str = Field(description="LLM's response")

system_chat = """
You are a very helpful Assistant, you are to answer user's request to the best of your ability. if you do not know respond with I do not know.
"""

chat_prompt = ChatPromptTemplate.from_messages(
     [
        ("system", system_chat),
        ("human", "{request}"),
    ]
)

def create_chat_chain(llm):
  """
  Creates a chat chain using the given LLM.
  """
  return chat_prompt | llm.with_structured_output(ChatResult)

