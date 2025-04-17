# Financial Assistant - Product Requirements Document (PRD)

## 1. Introduction

### 1.1 Purpose
The Financial Assistant is an intelligent agentic system designed to provide users with comprehensive financial data and analysis for publicly traded companies. It leverages LLM technology and financial APIs to deliver accurate, real-time financial information in a conversational interface.

### 1.2 Product Overview
The Financial Assistant is a Streamlit-based web application that combines Langgraph for orchestration, various LLM providers (GROQ, OpenAI, Anthropic), and the Financial Modeling Prep API to create an intelligent financial data retrieval and analysis system. The application allows users to query financial information about companies using natural language and receive structured, informative responses.

### 1.3 Target Audience
- Individual investors
- Financial analysts
- Business professionals
- Students and educators in finance
- Anyone interested in accessing financial data through a conversational interface

## 2. Features and Functionality

### 2.1 Core Features

#### 2.1.1 Financial Data Retrieval
- **Stock Price Information**: Retrieve current stock prices, volume, moving averages, EPS, PE ratio, and upcoming earnings announcements
- **Income Statement Analysis**: Access key income statement metrics including revenue, gross profit, net income, EBITDA, and EPS
- **Company Financial Overview**: Obtain company information including market capitalization, industry, sector, beta, and website

#### 2.1.2 Intelligent Query Processing
- **Symbol Extraction**: Automatically identify company stock symbols from natural language queries
- **Request Categorization**: Classify user requests into appropriate categories (stock price, income statement, company financials, comprehensive report, or general chat)
- **Error Handling**: Provide clear error messages when company symbols cannot be identified or data cannot be retrieved

#### 2.1.3 Report Generation
- **Comprehensive Financial Reports**: Generate detailed markdown reports combining stock price, income statement, and company overview data
- **Standalone Data Views**: Provide focused views of specific financial data types based on user requests

#### 2.1.4 Conversational Interface
- **Natural Language Input**: Allow users to ask questions in natural language
- **Contextual Responses**: Provide formatted, readable responses that directly address user queries
- **Chat History**: Maintain conversation history for reference

### 2.2 Configuration Features

#### 2.2.1 LLM Provider Selection
- Support for multiple LLM providers:
  - GROQ (default)
  - OpenAI
  - Anthropic

#### 2.2.2 API Key Management
- Secure input for LLM API keys
- Secure input for Financial Modeling Prep API key
- Session-based storage of API keys (not persisted)

## 3. User Experience

### 3.1 User Interface
- **Clean, Minimalist Design**: Streamlit-based interface with intuitive layout
- **Chat Interface**: Familiar chat-style interaction pattern
- **Sidebar Configuration**: Easy access to API configuration options
- **Markdown Rendering**: Well-formatted financial data presentation

### 3.2 User Flows

#### 3.2.1 First-Time Setup
1. User visits the application
2. User selects preferred LLM provider from sidebar
3. User enters LLM API key
4. User enters Financial Modeling Prep API key
5. User saves API configuration

#### 3.2.2 Financial Data Query
1. User enters natural language query about a company
2. System processes query, extracts company symbol, and categorizes request
3. System retrieves relevant financial data
4. System formats and presents data to user
5. Query and response are added to chat history

#### 3.2.3 Error Handling Flow
1. User enters query with unknown company or symbol
2. System attempts to extract symbol but fails
3. System returns clear error message explaining the issue
4. User can refine query and try again

### 3.3 Flow diagram
```mermaid
    Start([_start_]) --> Router

    Router -->|report| SymbolExtractionReport
    Router -->|alone| SymbolExtractionAlone
    Router -->|chat| ChatNode

    SymbolExtractionReport -->|True| Pass
    SymbolExtractionReport -->|False| ErrorNode

    Pass --> CompanyFinancials
    Pass --> IncomeStatement
    Pass --> StockPrice

    CompanyFinancials --> GenerateReport
    IncomeStatement --> GenerateReport
    StockPrice --> GenerateReport

    GenerateReport --> FinalAnswer
    ErrorNode --> FinalAnswer

    SymbolExtractionAlone -->|error| ErrorNode
    SymbolExtractionAlone -->|income_statement| IncomeStatementStandAlone
    SymbolExtractionAlone -->|company_financials| CompanyFinancialsStandAlone
    SymbolExtractionAlone -->|stock_price| StockPriceStandAlone

    IncomeStatementStandAlone --> FinalAnswer
    CompanyFinancialsStandAlone --> FinalAnswer
    StockPriceStandAlone --> FinalAnswer

    ChatNode --> FinalAnswer
    FinalAnswer --> End([_end_])
```

## 4. Technical Requirements

### 4.1 Architecture

#### 4.1.1 Langgraph Workflow
- **Router Node**: Determines the type of request (report, standalone data, chat)
- **Symbol Extraction Nodes**: Extract company symbols from user queries
- **Data Retrieval Nodes**: Fetch specific financial data types
- **Report Generation Node**: Combine data into comprehensive reports
- **Final Answer Node**: Format and return responses to user

#### 4.1.2 State Management
- Maintain graph state including:
  - Company symbol
  - Retrieved financial data
  - Generated reports
  - Error messages
  - Request categories

### 4.2 External Dependencies

#### 4.2.1 API Integrations
- **Financial Modeling Prep API**: Source of all financial data
- **LLM Provider APIs**: GROQ, OpenAI, or Anthropic for natural language processing

#### 4.2.2 Key Libraries
- **Langgraph**: For orchestrating the workflow
- **Streamlit**: For web interface
- **Langchain**: For LLM integration and chain creation
- **Pydantic**: For data validation and modeling

### 4.3 Performance Requirements
- **Response Time**: Aim for responses within 5 seconds for most queries
- **Scalability**: Support multiple concurrent users
- **Reliability**: Graceful handling of API failures or rate limits

## 5. Limitations and Constraints

### 5.1 Current Limitations
- Limited to publicly traded companies available in Financial Modeling Prep API
- Requires valid API keys for both LLM provider and Financial Modeling Prep
- No persistent storage of user preferences or conversation history
- No historical data analysis beyond what's provided in standard reports

### 5.2 Future Considerations
- Integration with additional financial data sources
- Support for historical data analysis and visualization
- Portfolio tracking and management features
- Customizable report templates
- Persistent user accounts and preferences

## 6. Success Metrics

### 6.1 Key Performance Indicators
- **Query Success Rate**: Percentage of queries that successfully return relevant data
- **Symbol Extraction Accuracy**: Accuracy of company symbol identification
- **User Engagement**: Average session duration and queries per session
- **Response Quality**: Relevance and completeness of responses to user queries

## 7. Project Structure

### 7.1 File Structure

```
FinancialAssistant/
├── docs/                      # Documentation files
│   ├── prd.md                 # Product Requirements Document
│   └── rules/                 # Development guidelines
│       └── python.md          # Python coding standards
├── documentation/             # Additional documentation
├── notebook/                  # Jupyter notebooks for development and testing
│   ├── langgraph_financial_assistant.ipynb  # Main development notebook
│   └── langgraph_financial_assistant.py     # Python version of the notebook
├── streamlit_app/            # Main application code
│   ├── app.py                # Main Streamlit application entry point
│   ├── classes/              # Data models and classes
│   │   ├── company_financials.py  # Company financials data model
│   │   ├── config.py              # Configuration class
│   │   ├── income_statement.py    # Income statement data model
│   │   └── stock_price.py         # Stock price data model
│   ├── chains/               # LLM chain definitions
│   │   ├── chat_chain.py          # Chain for general chat functionality
│   │   ├── extraction_chain.py    # Chain for extracting company symbols
│   │   └── route_chain.py         # Chain for routing user requests
│   ├── consts/               # Constants used throughout the application
│   │   └── consts.py              # Application constants
│   ├── graph/                # Langgraph workflow definition
│   │   ├── graph_state.py         # State definition for the graph
│   │   ├── nodes.py               # Node definitions for the workflow
│   │   └── work_flow.py           # Main workflow construction
│   ├── methods/              # Utility methods
│   │   ├── generate_methods.py    # Methods for generating markdown reports
│   │   └── util.py                # General utility functions
│   ├── streamlit_test.py    # Test file for Streamlit functionality
│   └── test_imports.py      # Test file for verifying imports
├── .idea/                   # IntelliJ IDEA configuration
├── .vscode/                 # VS Code configuration
│   └── launch.json          # VS Code launch configuration
└── README.MD               # Project overview
```

### 7.2 Key Components Explanation

#### 7.2.1 Application Structure
- **streamlit_app/**: Contains the main application code
  - **app.py**: Entry point for the Streamlit application, handles UI and user interaction
  - **classes/**: Data models using Pydantic for type validation
  - **chains/**: LLM chain definitions for different processing steps
  - **graph/**: Langgraph workflow definition and state management
  - **methods/**: Utility functions and report generation methods

#### 7.2.2 Data Models
- **company_financials.py**: Defines the structure for company overview data
- **income_statement.py**: Defines the structure for income statement data
- **stock_price.py**: Defines the structure for stock price information
- **config.py**: Manages API configuration

#### 7.2.3 LLM Chains
- **extraction_chain.py**: Extracts company symbols from user queries
- **route_chain.py**: Categorizes user requests into appropriate types
- **chat_chain.py**: Handles general conversational queries

#### 7.2.4 Workflow Components
- **work_flow.py**: Defines the Langgraph workflow with nodes and edges
- **nodes.py**: Implements the functionality for each node in the graph
- **graph_state.py**: Defines the state structure maintained throughout the workflow

#### 7.2.5 Development Resources
- **notebook/**: Contains Jupyter notebooks used during development
- **docs/**: Contains documentation including this PRD

## 8. Appendix

### 8.1 Glossary
- **LLM**: Large Language Model
- **API**: Application Programming Interface
- **EPS**: Earnings Per Share
- **PE Ratio**: Price-to-Earnings Ratio
- **EBITDA**: Earnings Before Interest, Taxes, Depreciation, and Amortization

### 8.2 References
- [Financial Modeling Prep API Documentation](https://financialmodelingprep.com/developer/docs/)
- [Langgraph Documentation](https://github.com/langchain-ai/langgraph)
- [Streamlit Documentation](https://docs.streamlit.io/)
