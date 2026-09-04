class Agent:
    def __init__(self, name:str, model:str, tools:list[str]):
        self.name = name
        self.model = model
        self.tools = tools
    def show_info(self):
        print(f"Agent名称：{self.name}\n"
              f"模型：{self.model}\n"
              f"工具：{self.tools}")

agent1=Agent(name="ResearchAgent",model="Qwen",tools=['search', 'calculator'])
agent1.show_info()