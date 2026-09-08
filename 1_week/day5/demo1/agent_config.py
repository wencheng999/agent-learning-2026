import os
from dotenv import load_dotenv


load_dotenv()

class LLMConfig:
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL")
        self.model=os.getenv("LLM_MODEL")
        if not self.api_key:
            raise ValueError("LLM_API_KEY not set")
        if not self.base_url:
            raise ValueError("LLM_BASE_URL not set")
        if not self.model:
            raise ValueError("LLM_MODEL not set")

