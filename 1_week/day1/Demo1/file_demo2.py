with open("note.txt","r",encoding="utf-8") as f:
    print(f.read())

with open("memory.txt","w",encoding="utf-8") as f:
    f.write("用户正在学习Agent\n")

with open("memory.txt","a",encoding="utf-8") as f:
    f.write("用户正在学习Python")


def load_file(path:str)->str|None:
    try:
        with open(path,"r",encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("文件不存在")
        return None

def save_memory(content:str):
    with open("memory.txt","a",encoding="utf-8") as f:
        f.write(content)

def load_memory(path:str)->str:
    with open("memory.txt","r",encoding="utf-8") as f:
        return f.read()

