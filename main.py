from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import subprocess
import os
import re
import asyncio  # 导入 asyncio
from pkg.platform.types import *
from .forward import ForwardMessage 
from typing import List, Dict

import base64
from io import BytesIO
from plugins.versaBotPlugin.func.贤者模式 import SageSystem

@register(name="versaBotPlugin", 
          description="一个小插件运行插件不必开关程序直接运行程序简单（可以用gpt直接写功能添加）", 
          version="0.7", 
          author="sheetung")
class MyPlugin(BasePlugin):

    def __init__(self, host: APIHost):
        # pass
        self.forwarder = ForwardMessage("127.0.0.1", 3000)
        self.sagesys = SageSystem()
        self.forward_config = {
            '流量卡': {  # 命令名称
                'enable': True,  # 是否启用转发
                'dftcmd': '19元',
                'prompt': '流量卡查询结果',
                'summary': '最新套餐信息',
                'source': '流量卡小助手',
                'user_id': '1048643088',    # 自定义QQ号
                'nickname': '流量卡小助手',  # 自定义昵称
                'mode': 'multi'  # single/multi 对应单条发出还是分条发出
            },
            '看妹妹': {  
                'enable': True,  
                'dftcmd': '1',
                'prompt': '看妹妹',
                'summary': '看妹妹',
                'source': '沙耶香不看',
                'user_id': '1048643088',    
                'nickname': 'bot妹妹',
                'mode': 'multi'   
            },
            '天气': {  
                'enable': False,  
                'dftcmd': '贵阳',
                'prompt': '看妹妹',
                'summary': '看妹妹',
                'source': '沙耶香不看',
                'user_id': '1048643088',    
                'nickname': 'bot妹妹',
                'mode': 'multi'   
            },
            '贤者模式': {  
                'enable': False,  
                'dftcmd': 'off',
                'prompt': '',
                'summary': '',
                'source': '',
                'user_id': '',    
                'nickname': '',
                'mode': ''   
            },
            '热搜': {  
                'enable': True,  
                'dftcmd': 'off',
                'prompt': '微博热搜榜',
                'summary': '微博热搜榜',
                'source': '微博热搜榜',
                'user_id': '1048643088',    
                'nickname': '追热点的沙耶香',
                'mode': ''   
            },
            '猫眼': {  
                'enable': True,  
                'dftcmd': 'off',
                'prompt': '猫眼票房排行榜',
                'summary': '猫眼票房排行榜',
                'source': '猫眼票房排行榜',
                'user_id': '1048643088',    
                'nickname': '猫眼沙耶香',
                'mode': ''   
            }
        }
    # 异步初始化
    async def initialize(self):
        pass
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
            # self.ap.logger.info(f'[verbot]msg---\n{msg}\n---')
            # 修改正则表达式，保留 @ 后面的 QQ 号
            cleaned_text = re.sub(r'@(\d+)', r' \1', msg).strip()  # 清理文本，保留 QQ     
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            # 去掉了 startswith('/') 的判断,恢复如下
            # if cleaned_text.startswith('/'):  # 检查是否为命令
            parts = cleaned_text.split(' ', 1)  # 分割命令和参数
            cmd = parts[0]
            cmd1 = parts[1] if len(parts) > 1 else str(ctx.event.sender_id)

            sender_id = ctx.event.sender_id
            launcher_id = str(ctx.event.launcher_id)
            launcher_type = str(ctx.event.launcher_type)
            # 获取黑/白名单
            # 临时适配langbot4.0特性
            pipeline_data = getattr(self.ap.pipeline_cfg, 'data', None)
            if not pipeline_data:
                # add langbot 4.0 适配
                try:
                    mode = ctx.event.query.pipeline_config['trigger']['access-control']['mode']
                    sess_list = ctx.event.query.pipeline_config['trigger']['access-control'][mode]
                except Exception as e:
                    logger.error(f"无法从 ctx 获取 access-control 设置: {e}")
                    return
            else:
                mode = pipeline_data['access-control']['mode']
                sess_list = pipeline_data['access-control'][mode]

            found = False
            if (launcher_type== 'group' and 'group_*' in sess_list) \
                or (launcher_type == 'person' and 'person_*' in sess_list):
                found = True
            else:
                for sess in sess_list:
                    if sess == f"{launcher_type}_{launcher_id}":
                        found = True
                        break 
            ctn = False
            if mode == 'whitelist':
                ctn = found
            else:
                ctn = not found
            if not ctn:
                # print(f'您被杀了哦')
                return

            script_path = os.path.join(os.path.dirname(__file__), 'func', f"{cmd}.py")
            if os.path.exists(script_path):  # 检查脚本是否存在
                # 贤者模式判断
                if self.sagesys.check_user(sender_id, cmd):
                    remain  = self.sagesys.get_remaining(sender_id, cmd)
                    message_c = MessageChain([Plain(f'贤者模式 | {cmd}请 {remain:.1f} 小时后再尝试')])
                    await ctx.reply(message_c)
                    return
                try:
                    if cmd in self.forward_config :  #在config里面
                        if cmd1 == str(sender_id) and self.forward_config[cmd]['dftcmd'] != 'off': # 但是没传入参数
                            # 指定‘dftcmd’默认参数
                            cmd1 = self.forward_config[cmd]['dftcmd']
                        elif self.forward_config[cmd]['dftcmd'] == 'off' : # 有参数传入但是不希望传参
                            cmd1 = str(sender_id)
                            
                    result = subprocess.check_output(['python', script_path, cmd1], text=True, timeout=60)  # 设置超时为60秒
                    # self.ap.logger.info(f'[verbot]result---\n{result}\n---')
                    if cmd in self.forward_config and self.forward_config[cmd]['enable']:
                        if cmd1 == '1' and cmd == '看妹妹':
                            messages = self.convert_message(result, sender_id)  # 转换输出消息格式
                            await ctx.reply(messages)
                            return
                        # 转换为合并转发格式
                        forward_messages = self.forwarder.convert_to_forward(result)
                        # self.ap.logger.info(f'forward_messages:\n{forward_messages}')
                        config = self.forward_config[cmd]
                        # 发送合并转发
                        await self.forwarder.send_forward(
                            launcher_id=launcher_id,
                            messages=forward_messages,
                            prompt=config['prompt'],
                            summary=config['summary'],
                            source=config['source'],
                            user_id=config['user_id'],
                            nickname=config['nickname'],
                            mode=config['mode']
                        )
                    else:
                        # self.ap.logger.info(f'命令{result}')
                        messages = self.convert_message(result, sender_id)  # 转换输出消息格式
                        # self.ap.logger.info(f'[verbot]messages---\n{messages}\n---')
                        # await ctx.send_message(ctx.event.launcher_type, str(ctx.event.launcher_id), MessageChain(messages))
                        # ctx.add_return("reply", messages)  # 返回处理后的消息
                        await ctx.reply(messages)

                except subprocess.CalledProcessError as e:  # 捕获脚本执行错误
                    # ctx.add_return("reply", [f"执行失败喵: {e.output}"])  # 返回错误消息
                    await ctx.reply(MessageChain([Plain(f"执行失败喵~ {e.output}~")]))
                except Exception as e:  # 捕获其他异常
                    # ctx.add_return("reply", [f"发生错误了喵: {str(e)}"])  # 返回通用错误消息
                    await ctx.reply(MessageChain([Plain(f"发生错误了喵~ {str(e)}")]))
                    await ctx.reply(MessageChain([Plain(f"发生错误了喵~")]))
                ctx.prevent_default()  # 防止后续处理

    # def convert_to_forward(self, raw_message: str) -> list[dict]:
    #     """升级版消息解析，按块分组，保留图文顺序"""
    #     messages = []

    #     for block in raw_message.split('\n---\n'):
    #         block = block.strip()
    #         if not block:
    #             continue
    #         content = []
    #         elements = re.split(r'(!\[.*?\]\(.*?\))', block)
    #         for elem in elements:
    #             elem = elem.strip()
    #             if not elem:
    #                 continue
    #             if elem.startswith('!['):  # 图片
    #                 match = re.match(r'!\[.*?\]\((.*?)\)', elem)
    #                 if match:
    #                     content.append({
    #                         "type": "image",
    #                         "data": {"file": match.group(1)}
    #                     })
    #             else:  # 文本
    #                 content.append({
    #                     "type": "text",
    #                     "data": {"text": elem}
    #                 })
    #         if content:
    #             messages.append({"content": content})
    #     return messages

    def convert_message(self, message, sender_id):
        parts = []
        last_end = 0
        Inimage = False
        image_pattern = re.compile(r'!\[.*?\]\((https?://\S+)\)')  # 网络图片的正则表达式
        local_image_pattern = re.compile(r'(/home/\S+)')  # 本地图片的正则表达式

        # 检查消息中是否包含at指令
        if "atper_on" in message:
            parts.append(At(target=sender_id))  # 在消息开头加上At(sender_id)
            message = message.replace("atper_on", "")  # 从消息中移除"send_on"
            # self.ap.logger.info(f'message = {message}')
        # 处理网络图片
        for match in image_pattern.finditer(message):  # 查找所有匹配的图像链接
            Inimage = True
            start, end = match.span()  # 获取匹配的起止位置
            if start > last_end:  # 如果有文本在图像之前
                parts.append(Plain(message[last_end:start]))  # 添加纯文本部分
            image_url = match.group(1)  # 提取图像 URL
            parts.append(Image(url=image_url))  # 添加图像消息
            last_end = end  # 更新最后结束位置

        if last_end +1 < len(message) and Inimage:  # 如果还有剩余文本
            parts.append(Plain(message[last_end:]))  # 添加剩余的纯文本
        elif Inimage == False: # 纯文本部分
            parts.append(Plain(message))
        # 处理本地图片
        # self.ap.logger.info(f'{image_pattern.finditer(message)}')
        for match in local_image_pattern.finditer(message):  # 查找所有匹配的本地图像链接
            image_path = match.group(1)  # 提取本地图片路径
            
            try:
                with open(image_path, 'rb') as img_file:
                    img_bytes = img_file.read()
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                return [Image(base64=img_base64)]
            except Exception as e:
                return [Plain(f"[Error loading image: {e}]")]

        Inimage = False
        return parts if parts else [Plain(message)]  # 返回构建好的消息列表，如果没有部分则返回纯文本消息
    
    def __del__(self):
        pass
