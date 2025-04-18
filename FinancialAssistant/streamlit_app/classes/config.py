from pydantic import SecretStr


class Config():
    def __init__(self, llm_api_key: SecretStr, fmp_api_key:SecretStr, provider:str):
        self.llm_api_key:SecretStr = llm_api_key
        self.fmp_api_key:SecretStr = fmp_api_key
        self.provider = provider
    # api_keys_set = True
