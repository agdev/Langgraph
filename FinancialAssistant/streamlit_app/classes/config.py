class Config():
    def __init__(self, llm_api_key: str, fmp_api_key:str, provider:str):
        self.llm_api_key = llm_api_key
        self.fmp_api_key = fmp_api_key
        self.provider = provider
    # api_keys_set = True
