练习1：

因为只有等summary总结成功后，也就是把之前的一些历史消息总结保存下来后，放到当前agent的state里面后，才能把message之前的一些消息删掉，不然如果summary失败也删除后， 那么message之前的一些历史信息就真的没有了，现在这样就算summary失败后也不会删除message之前的一些消息，最差也是多保留一次之前的历史信息，比直接删除要好。



练习2：

recent_n=6意思是当message历史消息达到一定阈值时就保存最新的前6条消息。

max_messages=10意思就是出发summary的message的阈值长度。



练习3：

当前的messages的消息长度为12，超过了summarize_history()触发的长度大小，所以会触发，首先会把之前的6条历史信息和旧的summary信息组成summary_message，然后将summary_message由client发送给LLM，让LLM总结成新的summary，然后把新的summary放到state进行更新。



练习4：

当用户从客户端client向服务器提出问题后，contextmanager负责将此次提出的问题转为LLM实际接受的context全部内容，然后发送给LLM，LLM回答问题后给出答案answer，然后将答案等信息放到agent管理的state中去，进行更新，然后判断是不是达到总结历史信息的条件，是否需要总结历史信息，然后更新state后进入下一轮对话。

```
用户提出current_query
        ↓
ContextManager读取AgentState
        ↓
选择System、Constraints、
Summary、Recent Messages、
Current Query
        ↓
构造Context
        ↓
LLMClient把Context发送给LLM
        ↓
LLM生成Answer
        ↓
current_query + answer
写入state.messages
        ↓
判断messages是否超过阈值
        ↓
如果过长
→ summarize_history()
→ 更新conversation_summary
→ 只保留最近messages
        ↓
进入下一轮
```

