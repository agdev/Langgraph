from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

"""# **Chat chain**"""
class ChatResult(BaseModel):
  """
  The result of the chat chain.
  """
  response: str = Field(description="LLM's response")

system_chat = """
You are a very helpful Financial Assistant, you are to answer user's request to the best of your ability. If you do not know, respond with 'I do not know'.

If there is a conversation summary available, use it to provide context for understanding the user's request and to maintain continuity in the conversation. This will help you provide more relevant and personalized responses based on the user's previous interactions.
"""

chat_prompt = ChatPromptTemplate.from_messages(
     [
        ("system", system_chat),
        ("human", "Conversation summary: {conversation_summary}\n\nUser request: {request}"),
    ]
)

def create_chat_chain(llm):
  """
  Creates a chat chain using the given LLM.
  """
  return chat_prompt | llm.with_structured_output(ChatResult)

