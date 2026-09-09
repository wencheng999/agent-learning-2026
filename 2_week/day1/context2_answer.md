练习1：

state：是LLM在当前状态的存储的全部信息。

Context：是某个LLM在某一阶段所需要的实际信息。

Memory：是LLM保存的有效的长久信息。



练习2：

因为这样会让LLM因为输入信息过多抓不住重点，而且有的信息根本没必要送到writer，只需要将writer所需要的给它就行。



练习3：

Planner ：user_query current_step

Searcher : user_query plan evidence current_step

Writer: user_query  current_step tool_results  evidence final_draft



练习4：

因为每个任务都创建单独的list，可以相互不影响



练习5：

8挑evidence，因为writer任务主要是写作，所以更需要将50篇原始的查找结果进行过滤、重排成高质量的信息。



练习6：

首先创建agentstate对象，来存储LLM当前状态的全部信息，然后再创建contextmanager对象，来存储每部任务LLM所需的实际context信息，这个过程通过选择state的哪些信息，然后进行压缩、精选，然后组织成合适的输入给LLM的信息结构，从而构建当前的context内容，然后送到LLM，LLM执行完毕后产生结果并更新state内容。

 