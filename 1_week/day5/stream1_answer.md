练习1：

因为非流式的message拿到的是完整消息，而Streaming拿到的delta是本次新增的一小块



练习2：

因为print(content)能够让用户看到消息不断被打印， 但是不会将一段一段的内容给自动保存，如果后面需要将流式生成的内容加入到上下文中时，就需要将流式打印的内容用full_content不断保存下来并返回。



练习3：

对于流式请求，首先需要将stream设置为True，然后调用stream() 流行请求方法，然后获得response请求对象后，然后再循环调用aiter_lines()方法将内容逐行迭代打印每一行的line内容，然后去掉里面内容的前面的data和空行等字段，然后把str的json格式用json.loads()方法转为dict格式，然后去除delta里面的content内容，也就是某一块流式生成的实际内容，然后进行打印，然后再用full_content空字符串不断追加生成的content内容，最后返回full_content。

