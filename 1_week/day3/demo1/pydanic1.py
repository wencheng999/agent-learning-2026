from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int

user1 = User(name="John", age="221")
print(user1.name)
print(type(user1.age))