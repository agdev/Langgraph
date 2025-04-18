"""
Summarization Chain for Financial Assistant.

This module provides a chain for summarizing conversations in the Financial Assistant.
It uses a specialized prompt to generate concise summaries of financial conversations.
"""

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
    
    Args:
        llm: The language model to use for summarization
        
    Returns:
        A chain that takes conversation and existing summary as input and returns a summary
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
            ("human", "Previous summary: <previous_summary>{existing_summary}</previous_summary>\n\nConversation:<conversation> {conversation}</conversation>\n\n Provide an updated summary.")
        ]
    )
    
    # Create the chain using the pipe operator
    return summarization_prompt | llm.with_structured_output(SummarizationResult)
