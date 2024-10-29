def generate_markdown_report(company_financials: CompanyFinancials, income_statement: IncomeStatement, stock_price: StockPrice) -> str:
    """
    Generates a markdown report from the GraphState instance.
    """

    company_info = f"""
      # Financial Report for {company_financials.companyName} ({company_financials.symbol})

      ## Company Overview
      - **Name**: {company_financials.companyName}
      - **Symbol**: {company_financials.symbol}
      - **Market Capitalization**: {company_financials.marketCap}
      - **Industry**: {company_financials.industry}
      - **Sector**: {company_financials.sector}
      - **Website**: [{company_financials.website}]({company_financials.website})
      - **Beta**: {company_financials.beta: .3f}
      - **Current Price**: ${company_financials.price: .2f}
      """ if (company_financials) else " No company financials were obtained"

    income_statement = f"""
    ## Income Statement (as of {income_statement.date_field})
    - **Revenue**: ${income_statement.revenue: .2f}
    - **Gross Profit**: ${income_statement.gross_profit: .2f}
    - **Net Income**: ${income_statement.net_income: .2f}
    - **EBITDA**: ${income_statement.ebitda: .2f}
    - **EPS**: {income_statement.eps: .2f}
    - **EPS (Diluted)**: {income_statement.eps_diluted: .2f}
    """ if income_statement else "No income statement was obtained"

    stock_price = f"""
      ## Stock Price Information
    - **Current Price**: ${stock_price.price: .2f}
    - **Volume**: {stock_price.volume: .2f}
    - **50-Day Average Price**: ${stock_price.priceAvg50: .2f}
    - **200-Day Average Price**: ${stock_price.priceAvg200: .2f}
    - **EPS**: {stock_price.eps: .2f}
    - **PE Ratio**: {stock_price.pe: .2f}
    - **Earnings Announcement**: {stock_price.earningsAnnouncement}
    """ if stock_price else "No stock price information was obtained"

    md_report = f"""
    {company_info}

    {income_statement}

    {stock_price}
    """
    return md_report