# XiaocxPlugin



更新了文档对部分小插件的使用讲解和图片示例

参考大佬[sanxianxiaohuntun/XiaocxPlugin](https://github.com/sanxianxiaohuntun/XiaocxPlugin)

## 安装

配置完成 [QChatGPT](https://github.com/RockChinQ/QChatGPT) 主程序后使用管理员账号向机器人发送命令即可安装：<br />

```
!plugin get https://github.com/sanxianxiaohuntun/XiaocxPlugin.git
```

或查看详细的[插件安装说明](https://github.com/RockChinQ/QChatGPT/wiki/5-%E6%8F%92%E4%BB%B6%E4%BD%BF%E7%94%A8)

## 目前集成



## 使用


> 这只是一个加载小程序的插件，data里内部包含一些小程序案例，可以让用户自主添加小程序，比如 天气  色图 运势 之类的各种小功能

> 小程序开发及其简单，把你需要的功能告诉gpt然后把我的案例程序代码给GPT，GPT生成后丢到data目录下即可，目前还在更新测试，如何写自己想要的功能请[参考](https://github.com/sanxianxiaohuntun/XiaocxPlugin)《小白专用GPT自制插件生成教程》

**versaBot**使用方法：输入data中任意关键词出发，例如输入 `菜单` 触发`菜单.py`

如不想修改当前bot触发关键词

要添加触发前缀，按照如下方法加入`main.py`中，在参数分割命令前添加命令判断，并把以后所有命令tab一格保持对齐

```python
if cleaned_text.startswith('/'):  # 检查是否为命令
```

如添加前缀后触发即改成`/菜单`



## 更新日志

V0.26 优化`main.py`对消息的消息处理，对纯图片消息优化