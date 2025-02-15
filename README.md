# versaBotPlugin

一个基于 [QChatGPT](https://github.com/RockChinQ/QChatGPT) 的多功能插件，允许用户在 `data` 目录下自由编写和扩展自己的小程序，轻松实现各种实用功能，如天气查询、图片生成、运势预测等。

## 🌟 特性

- **高度可扩展**：用户可以在 `data` 目录下自由编写 Python 脚本，快速扩展新功能。
- **简单易用**：无需复杂配置，只需将脚本放入指定目录，即可通过命令触发。
- **灵活定制**：支持自定义命令前缀，满足不同用户的需求。
- **丰富的功能示例**：内置多种实用小程序示例，涵盖图片、文本等多种类型。

## 🚀 安装

1. **配置 QChatGPT 主程序**：确保你已正确安装并配置 [QChatGPT](https://github.com/RockChinQ/QChatGPT)。

2. **安装 versaBotPlugin**：

   - 使用管理员账号向机器人发送以下命令：

     ```
     !plugin get https://github.com/sanxianxiaohuntun/XiaocxPlugin.git
     ```

   - 或参考详细的 [插件安装说明](https://github.com/RockChinQ/QChatGPT/wiki/5-插件使用)。

## 🛠️ 使用方法

1. **编写小程序**：

   - 在 `data` 目录下创建 `.py` 文件，例如 `菜单.py`。
   - 参考内置示例或使用 GPT 生成代码，实现所需功能。
   - 将脚本文件放入 `data` 目录，无需重启主程序即可生效。

2. **触发小程序**：

   - 输入小程序文件名作为命令，例如输入 `菜单` 触发 `菜单.py`。

   - 如需自定义命令前缀，可在 `main.py` 中修改：

     Python复制

     ```python
     if cleaned_text.startswith('/'):  # 检查是否为命令
     ```

   - 修改后，命令触发方式将变为 `/菜单`。

## 📚 示例功能

- **天气查询**：输入 `/天气 北京`，获取北京的天气信息。
- **运势预测**：输入 `/运势 星座`，获取星座运势。
- **随机图片**：输入 `/色图`，随机返回一张图片。

## 📚 开发指南

- **小程序开发**：将所需功能描述清晰，结合内置示例代码，使用 GPT 生成脚本。

- **文件结构**：

  复制

  ```
  versaBotPlugin/
  ├── data/
  │   ├── 菜单.py
  │   ├── 天气.py
  │   └── 画图.py
  ├── main.py
  └── settings.json
  ```

- **命令冲突**：如遇到命令冲突，可在 `main.py` 中修改命令前缀。

## 📚 参考资料

- [XiaocxPlugin](https://github.com/sanxianxiaohuntun/XiaocxPlugin)：一个功能丰富的参考插件。
- [QChatGPT 插件使用文档](https://github.com/RockChinQ/QChatGPT/wiki/5-插件使用)：了解更多插件使用方法。

## 📝 更新日志

- **v0.3.0**：优化命令传入逻辑，提升用户体验。
- **v0.2.6**：优化 `main.py` 对消息的处理，支持纯图片消息。