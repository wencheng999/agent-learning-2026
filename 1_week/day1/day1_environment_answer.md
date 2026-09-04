练习1：

因为这两个项目所用的python版本和Pydantic 都不一致，如果使用同一个环境会产生冲突。



练习2：

git status

git add .

git  commit

git push



练习3：

git add. 表示将新修改的改动部分准备提交了，然后进入暂存区，而git commit表示真正提交到本体git仓库中，是真正创建一个版本。





练习4：

因为.env文件一般存储像LLM_API_KEY这种具体数据，隐私性比较高，.gitignore文件表示哪些文件不上传到git上，但是为了便于复现，知道有哪些具体的变量名字，所以需要.env.example文件来存储，但是里面不存储这些变量的值，所以可以上传到git仓库上面。



