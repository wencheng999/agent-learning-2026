练习1：

AsyncClient 是httpx里面的一个异步向服务器请求的客户端对象，相当于之前的requests，但目前变成异步的了

async with  表示异步打开网络请求，类比之前的with open 文件，可以结束时自动关闭网络资源。

await 表示异步等待当前任务执行完毕

response 表示一个响应对象。



练习2：

requests.get(url) 请求服务器时，若服务器一直没有响应就会一直等待，资源利用率低

而await client.get(url)请求服务器时，若服务器没有响应则运行执行其他任务，等服务器响应后再执行当前任务。

