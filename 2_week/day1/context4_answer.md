练习1：

因为contextManager主要负责将struct state+summary+recent information+current input整合成合适的context内容，然后送到当前任务的LLM中。

练习2：

因为LLM总结的内容有时候可能会把一些重要内容给丢弃或者忘记，所以一些重要内容要放到constraints中去。

练习3：

都应该加，首先current_query在发送LLM之前需要将其包装到context中，然后发送给LLM，LLM回答完后还需要将current_query放到message历史中，从而作为历史信息辅助下一次回答。

