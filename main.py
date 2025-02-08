from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
# from pkg.plugin.events import PersonNormalMessageReceived, GroupNormalMessageReceived
from pkg.plugin.events import *  # 导入事件类
import subprocess
import os
import re
import asyncio  # 导入 asyncio
from mirai import Image, Plain
from pkg.platform.types import *

@register(name="小程序运行插件", 
          description="一个小插件运行插件不必开关程序直接运行程序简单（可以用gpt直接写功能添加）", 
          version="0.21", 
          author="sheetung")
class CommandExecutorPlugin(BasePlugin):

    lock = asyncio.Lock()  # 创建一个锁以确保线程安全
    command_queue = asyncio.Queue()  # 创建一个队列以存储待处理的命令

    # @handler(PersonNormalMessageReceived)
    @handler(PersonMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        await self.command_queue.put(ctx)  # 将命令上下文放入队列
        await self.process_commands()  # 处理命令

    # @handler(GroupNormalMessageReceived)
    @handler(GroupMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        await self.command_queue.put(ctx)  # 将命令上下文放入队列
        await self.process_commands()  # 处理命令

    async def process_commands(self):
        while not self.command_queue.empty():  # 当队列不为空时
            ctx = await self.command_queue.get()  # 从队列中获取命令上下文
            await self.execute_command(ctx)  # 执行命令
            await asyncio.sleep(2)  # 等待 2 秒再处理下一个命令

    async def execute_command(self, ctx: EventContext):
        async with self.lock:  # 使用锁确保线程安全
            # receive_text = ctx.event.text_message
            msg = str(ctx.event.message_chain).strip()
            cleaned_text = re.sub(r'@\S+\s*', '', msg).strip()  # 清理文本
            # 去掉了 startswith('/') 的判断
            parts = cleaned_text.split(' ', 1)  # 分割命令和参数
            command = parts[0]
            args = parts[1] if len(parts) > 1 else ''

             # 获取发送者信息
            sender_id = "Unknown"
            if hasattr(ctx.event, 'query'):
                message_event = ctx.event.query.message_event
                if hasattr(message_event, 'sender'):
                    sender = message_event.sender
                    # 优先使用qq id
                    if hasattr(sender, 'id') and sender.id:
                        sender_id = sender.id
                    elif hasattr(sender, 'card') and sender.card:
                        sender_id = sender.card
                    # 其次使用群昵称
                    elif hasattr(sender, 'member_name') and sender.member_name:
                        sender_id = sender.member_name
                    # 最后使用QQ昵称
                    elif hasattr(sender, 'nickname') and sender.nickname:
                        sender_id = sender.nickname

            script_path = os.path.join(os.path.dirname(__file__), 'data', f"{command}.py")
            if os.path.exists(script_path):  # 检查脚本是否存在
                try:
                    result = subprocess.check_output(['python', script_path, args], text=True, timeout=60)  # 设置超时为60秒
                    messages = self.convert_message(result, sender_id)  # 转换输出消息格式
                    # await ctx.send_message(ctx.event.launcher_type, str(ctx.event.launcher_id), MessageChain(messages))
                    # ctx.add_return("reply", messages)  # 返回处理后的消息
                    await ctx.reply(MessageChain(messages))
                except subprocess.CalledProcessError as e:  # 捕获脚本执行错误
                    # ctx.add_return("reply", [f"执行失败喵: {e.output}"])  # 返回错误消息
                    await ctx.reply(MessageChain([Plain(f"执行失败喵~ {e.output}")]))
                except Exception as e:  # 捕获其他异常
                    # ctx.add_return("reply", [f"发生错误了喵: {str(e)}"])  # 返回通用错误消息
                    await ctx.reply(MessageChain([Plain(f"发生错误了喵~ {str(e)}")]))
                ctx.prevent_default()  # 防止后续处理
            

    def convert_message(self, message, sender_id):
        parts = []
        last_end = 0
        image_pattern = re.compile(r'!\[.*?\]\((https?://\S+)\)')  # 定义图像链接的正则表达式
        # 检查消息中是否包含at指令
        if "atper_on" in message:
            parts.append(At(target=sender_id))  # 在消息开头加上At(sender_id)
            message = message.replace("atper_on", "\n\n")  # 从消息中移除"send_on"

        for match in image_pattern.finditer(message):  # 查找所有匹配的图像链接
            start, end = match.span()  # 获取匹配的起止位置
            if start > last_end:  # 如果有文本在图像之前
                parts.append(Plain(message[last_end:start]))  # 添加纯文本部分
            image_url = match.group(1)  # 提取图像 URL
            parts.append(Image(url=image_url))  # 添加图像消息
            last_end = end  # 更新最后结束位置
        if last_end < len(message):  # 如果还有剩余文本
            parts.append(Plain(message[last_end:]))  # 添加剩余的纯文本
        return parts if parts else [Plain(message)]  # 返回构建好的消息列表，如果没有部分则返回纯文本消息
