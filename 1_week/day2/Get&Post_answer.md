练习1：

用GET更符合

Params={

"name"="agent",

"top_k"=5

}



练习2：

用POST更适合，因为这个请求内容是让服务器来解释回答问题，然后把结果返回给客户端，不是单纯的让服务器搜索查找内容（这个用GET更合适），所以用POST



练习3：

首先body可能存储了请求的内容或其他参数，然后可能是用python的dict格式，而requests里的json=body会自动将dict转换为json格式。



练习4：

不一定，具体的要看API协议是什么。



