from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from consts.consts import UNKNOWN


class Extraction(BaseModel):
    symbol: str = Field(description="The symbol of the company")


system = f"""You are very helpful Financial assistant.User will request financial data/information for a company.You are to return company's symbol on a stock market.
            do not make anything up. if you do not know reply {UNKNOWN} UPPER case.
"""

extraction_prompt = ChatPromptTemplate.from_messages(
     [
        ("system", system),
        ("human", "{request}"),
    ]
)

def create_extraction_chain(llm):
    """
    Creates an extraction chain using the given LLM.
    """
    extraction_chain = extraction_prompt | llm.with_structured_output(Extraction)
    return extraction_chain
