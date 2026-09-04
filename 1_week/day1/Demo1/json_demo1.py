# 练习1
import json
user = {
    "name": "Tom",
    "age": 20,
    "skills": [
        "Python",
        "Agent"
    ]
}
json_text=json.dumps(user, ensure_ascii=False,indent=2)
print(json_text)
print(type(json_text))


#练习2
with open("data/user.json", "w", encoding="utf-8") as f:
    json.dump(user,f,ensure_ascii=False,indent=2)

with open("data/user.json", "r", encoding="utf-8") as f:
    user_data=json.load(f)

print(user_data)
print(type(user_data))

#练习3
import os
from dotenv import load_dotenv

load_dotenv()
api_key=os.getenv("LLM_API_KEY")
model=os.getenv("LLM_MODEL")
base_url=os.getenv("LLM_BASE_URL")
print(model)
print(base_url)

#练习4

class Config:
    def __init__(self):
        self.api_key=os.getenv("LLM_API_KEY")
        self.model=os.getenv("LLM_MODEL")
        self.base_url=os.getenv("LLM_BASE_URL")
        if self.api_key is None:
            raise ValueError("请配置LLM_API_KEY")

config = Config()
print(config.api_key is not None)
print(config.model)
print(config.base_url)