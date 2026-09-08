练习1：

普通的LLM Response一般是等LLM全部回答完内容后一次性返回给用户，用户一般会有一段空白等待期，然后突然给出全部的回复，而Streaming Response是一段一段的回复给用户，向chatgpt那样，这样用户不用等待就能看到内容在不断生成，用户体验感比较好。



练习2：

async for 表示异步循环，这不是普通的循环，这表示在循环过程中若出现服务器阻塞现象，也可以转向其他任务执行，然后阻塞结束后继续执行循环这个任务。

aiter_lines()表示异步逐行读取服务器流式返回的内容。

line就是读取到的内容。



练习3：

因为streaming中也不是一些把全部内容直接俄返回的，是一个chunk一个chunk逐步返回的，所以不能一次性拿到内容。



练习4：

end""表示答应content内容不换行，flush=True表示尽快将当前内容真正显示到终端，不是让输出缓冲区等一会再统一显示。





练习5：

```
full_content = ""
content="Agent"
full_content+=content
content=" 是一种"
full_content+=content
content=" 智能系统"
full_content+=content
print(full_content)
```

