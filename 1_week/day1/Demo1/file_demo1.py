with open("note.txt","r",encoding="utf-8") as f:
    line=f.readlines()

print(line)

from pathlib import Path

DATA=Path("try_demo2.py")
print(DATA)