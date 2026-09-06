练习1：

name: str 表示name属性要求字符串类型，没有默认值。

name: str = "Tom" 表示name属性要求字符串类型，默认值为”Tom“

name: str | None = None 表示name属性要求字符串类型或None，默认值为None。



练习2：

default表示top_k字段的默认值为5，ge表示该字段要求大于等于1，le表示该字段le小于等于20。





练习4：

SearchInput(
    query="Agent",
    top_k=5
) 会过



SearchInput(
    query="Agent",
    top_k=0
)不会过（top_k要求大于等于1）

SearchInput(
    query="Agent",
    top_k=100
)不会过（top_k要求小于等于10）

SearchInput(
    query="Agent"
)不会过（top_k不能省略，language可以）

SearchInput(
    query="",
    top_k=5
)不会过（query至少1个字符）





只要字段有默认值，调用的时候通常就可以省略。