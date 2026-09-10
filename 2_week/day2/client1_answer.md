练习1：

state.messages一般保存的是用户和LLM交互的信息。

context是这次任务发送给LLM的全部信息，一般包括历史总结信息，限制信息，最近信息，当前用户提问信息。



练习2：

context = manager.build_context(    state=state,    current_query=current_query )

这行代码通过context_manager利用state信息和当前用户提问的信息，并调用函数建立了当前任务需要向LLM发送的实际全部内容context。



练习3：

因为这样能够保存用户的历史提问内容，然后LLM在后面回答时根据用户的历史提问内容更好的回答当前用户的问题， 让LLM具有更好的记忆功能，如果只加入一次不保存的话，LLM就不记得前面用户提问的问题是啥了。



练习4：

因为这会让main.py整体太拥挤冗余，逻辑和功能也比较复杂，后面添加功能代码时比较困难，通过让各个部分进行职责分离，能够更好的维护代码。



练习5：

第二轮发给LLM的context大概包括：

{

messages:[

{

User: 我叫Tom

}

{

Assistant: 你好Tom

}

]

contraints:"..."

summary:"..."

current_query:{

User: 我叫什么？

}



}

