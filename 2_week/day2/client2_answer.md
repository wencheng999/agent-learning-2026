 练习1：

state.messages[:-recent_n]得到前14条数据

state.messages[-recent_n:]得到后6条数据（也就是最近的6条）



练习2：

因为如果只考虑old_messages的话，新的到summary可能把原来旧的sunmmary信息给覆盖掉，所有在总结时尽可能加上旧的summary信息。





练习3：

因为随着不断summary，一些重要的信息会不断的压缩总结，最终重要的信息会不断的淡化甚至消失，所以重要的一些信息知识应该保存到结构化的state里面，这样能够让LLM持久保存理解到这些重要的信息。



练习4：

首先通过context_manager构建这次任务的context内容信息，然后发送给LLM，LLM回答完毕后将刚刚用户提问的问题和LLM的回答加入到历史的message当中，然后判断当前是否需要压缩历史信息，当历史信息message过长超过阈值时，context_manager就会调用压缩函数来压缩message信息，然后把新的总结信息放到state里面，message同时只保留最近的谈话信息，然后继续进行下一轮。



练习5：

1）其他一些无关紧要的信息可能会影响污染当前任务所需的真的的context信息。

2）花费的token也多；

3）无关紧要的信息会影响LLM的回答，导致后面的历史消息的质量也不好，从而导致其他比如summary等信息的质量也不高。

