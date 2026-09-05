import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.base_url=os.getenv("API_BASE_URL",
                                "https://httpbin.org/")
        self.timeout=int(os.getenv("API_TIMEOUT", "10"))

