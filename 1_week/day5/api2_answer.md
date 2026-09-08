练习1：

```
data["choices"][0]["message"]["content"]
```

因为data里面包含了很多LLM响应的全部信息，一般我们只想要看到LLM回答信息时就需要这样提取content。



练习2：

因为LLM一般时无状态的，也就是LLM回答第一个问题后，如果再发送第二个问题，LLM不知道第一个问题的答案是什么，所以LLM回答后每次都追加到messages里能够让LLM知道上下文内容是什么。



练习3：

```
messages.append({
    "role":"user",
    "content":"我叫Tom"
})
messages.append({
    "role":"assistant",
    "content":"你好Tom"
})
messages.append({
    "role":"user",
    "content":"我叫什么"
})
print(messages)
```



练习4：

因为服务器通常不会自动我保存用户的历史对话，对话历史通常时应用层面管理的。



练习5：

首先用户输入问题，然后加到message里面，调用客户端函数发送到LLM服务器，然后LLM服务器给出相应response，然后提取response里面的LLM的回答内容content，然后为了能够让LLM记住当前的聊天上下文，把LLM刚刚回答的content追加到message，然后继续下一轮的聊天。