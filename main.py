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
          description="个小插件运行插件不必开关程序直接运行程序简单（可以用gpt直接写功能添加）", 
          version="1.12", 
          author="sheetung")
class MyPlugin(BasePlugin):

    def __init__(self, host: APIHost):
        self.forwarder = ForwardMessage("127.0.0.1", 3000)
        self.sagesys = SageSystem()
        self.forward_config = {
            '流量卡': { 'enable': True, 'dftcmd': '19元', 'prompt': '流量卡查询结果', 'summary': '最新套餐信息', 'source': '流量卡小助手', 'user_id': '1048643088', 'nickname': '流量卡小助手', 'mode': 'multi' },
            '看妹妹': { 'enable': True, 'dftcmd': '1', 'prompt': '看妹妹', 'summary': '看妹妹', 'source': '沙耶香不看', 'user_id': '1048643088', 'nickname': 'bot妹妹', 'mode': 'multi' },
            '天气': { 'enable': False, 'dftcmd': '贵阳', 'prompt': '天气查询结果', 'summary': '天气信息', 'source': '天气查询', 'user_id': '1048643088', 'nickname': '天气小助手', 'mode': 'multi' },
            '贤者模式': { 'enable': False, 'dftcmd': 'off', 'prompt': '', 'summary': '', 'source': '', 'user_id': '', 'nickname': '', 'mode': '' },
            '热搜': { 'enable': True, 'dftcmd': 'off', 'prompt': '微博热搜榜', 'summary': '微博热搜榜', 'source': '微博热搜榜', 'user_id': '1048643088', 'nickname': '追热点的沙耶香', 'mode': '' },
            '猫眼': { 'enable': True, 'dftcmd': 'off', 'prompt': '猫眼票房排行榜', 'summary': '猫眼票房排行榜', 'source': '猫眼票房排行榜', 'user_id': '1048643088', 'nickname': '猫眼沙耶香', 'mode': '' }
        }
        
        # 扫描func目录获取所有可用命令（脚本名）
        self.available_cmds = self._scan_available_commands()

    def _scan_available_commands(self) -> List[str]:
        """扫描func目录下的所有Python脚本，返回可用命令列表（去.py后缀）"""
        func_dir = os.path.join(os.path.dirname(__file__), 'func')
        cmds = []
        
        if not os.path.exists(func_dir) or not os.path.isdir(func_dir):
            return cmds
            
        for filename in os.listdir(func_dir):
            # 只处理.py文件，排除以_开头的辅助脚本
            if filename.endswith('.py') and not filename.startswith('_'):
                cmd = filename[:-3]  # 去除.py后缀
                cmds.append(cmd)
                
        # 按命令长度倒序排序，确保匹配最长的命令
        return sorted(cmds, key=lambda x: len(x), reverse=True)

    # 异步初始化
    async def initialize(self):
        pass
        
    lock = asyncio.Lock()  # 创建一个锁以确保线程安全
    command_queue = asyncio.Queue()  # 创建一个队列以存储待处理的命令

    @handler(PersonMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        await self.command_queue.put(ctx)
        await self.process_commands()

    @handler(GroupMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        await self.command_queue.put(ctx)
        await self.process_commands()

    async def process_commands(self):
        while not self.command_queue.empty():
            ctx = await self.command_queue.get()
            await self.execute_command(ctx)
            await asyncio.sleep(2)

    async def execute_command(self, ctx: EventContext):
        async with self.lock:
            msg = str(ctx.event.message_chain).strip()
            # 清理文本，保留@后的QQ号
            cleaned_text = re.sub(r'@(\d+)', r' \1', msg).strip()
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

            sender_id = ctx.event.sender_id
            launcher_id = str(ctx.event.launcher_id)
            launcher_type = str(ctx.event.launcher_type)
            
            # 权限检查逻辑
            pipeline_data = getattr(self.ap.pipeline_cfg, 'data', None)
            if not pipeline_data:
                try:
                    mode = ctx.event.query.pipeline_config['trigger']['access-control']['mode']
                    sess_list = ctx.event.query.pipeline_config['trigger']['access-control'][mode]
                except Exception as e:
                    logger.error(f"无法获取 access-control 设置: {e}")
                    return
            else:
                mode = pipeline_data['access-control']['mode']
                sess_list = pipeline_data['access-control'][mode]

            found = False
            if (launcher_type == 'group' and 'group_*' in sess_list) or (launcher_type == 'person' and 'person_*' in sess_list):
                found = True
            else:
                for sess in sess_list:
                    if sess == f"{launcher_type}_{launcher_id}":
                        found = True
                        break 
                        
            ctn = found if mode == 'whitelist' else not found
            if not ctn:
                return

            # 解析命令和参数（兼容两种模式）
            cmd, param = self._parse_command(cleaned_text)
            
            # 如果没有匹配到命令，不处理
            if not cmd:
                return
                
            # 处理默认参数
            cmd1 = param if param else str(ctx.event.sender_id)
            # 检查是否有配置默认参数
            if cmd in self.forward_config and self.forward_config[cmd]['dftcmd'] != 'off' and not param:
                cmd1 = self.forward_config[cmd]['dftcmd']

            # 检查脚本是否存在
            script_path = os.path.join(os.path.dirname(__file__), 'func', f"{cmd}.py")
            if not os.path.exists(script_path):
                return

            # 贤者模式判断
            if self.sagesys.check_user(sender_id, cmd):
                remain = self.sagesys.get_remaining(sender_id, cmd)
                message_c = MessageChain([Plain(f'贤者模式 | {cmd}请 {remain:.1f} 小时后再尝试')])
                await ctx.reply(message_c)
                return

            try:
                # 执行脚本
                result = subprocess.check_output(['python', script_path, cmd1], text=True, timeout=60)
                
                # 处理转发
                if cmd in self.forward_config and self.forward_config[cmd]['enable']:
                    if cmd1 == '1' and cmd == '看妹妹':
                        messages = self.convert_message(result, sender_id)
                        await ctx.reply(messages)
                        return
                        
                    forward_messages = self.forwarder.convert_to_forward(result)
                    config = self.forward_config[cmd]
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
                    # 直接回复
                    messages = self.convert_message(result, sender_id)
                    await ctx.reply(messages)

            except subprocess.CalledProcessError as e:
                await ctx.reply(MessageChain([Plain(f"执行失败喵~ {e.output}~")]))
            except Exception as e:
                await ctx.reply(MessageChain([Plain(f"发生错误了喵~ {str(e)}")]))
                
            ctx.prevent_default()

    def _parse_command(self, cleaned_text: str) -> tuple[str, str]:
        """
        解析命令和参数，优先空格分割，再前缀匹配
        返回值：(命令, 参数)
        """
        # 1. 优先尝试空格分割模式（兼容旧方式）
        if ' ' in cleaned_text:
            parts = cleaned_text.split(' ', 1)  # 只分割第一个空格
            cmd_candidate = parts[0]
            param_candidate = parts[1].strip() if len(parts) > 1 else ""
            
            # 检查分割后的命令是否存在
            if cmd_candidate in self.available_cmds:
                return (cmd_candidate, param_candidate)
        
        # 2. 空格分割未匹配到有效命令，使用前缀匹配模式
        for cmd in self.available_cmds:
            if cleaned_text.startswith(cmd):
                # 提取命令后的剩余部分作为参数
                param = cleaned_text[len(cmd):].strip()
                return (cmd, param)
                
        # 3. 未匹配到任何命令
        return (None, None)

    def convert_message(self, message, sender_id):
        parts = []
        last_end = 0
        Inimage = False
        image_pattern = re.compile(r'!\[.*?\]\((https?://\S+)\)')
        local_image_pattern = re.compile(r'(/home/\S+)')

        if "atper_on" in message:
            parts.append(At(target=sender_id))
            message = message.replace("atper_on", "")
        
        # 处理网络图片
        for match in image_pattern.finditer(message):
            Inimage = True
            start, end = match.span()
            if start > last_end:
                parts.append(Plain(message[last_end:start]))
            image_url = match.group(1)
            parts.append(Image(url=image_url))
            last_end = end

        if last_end +1 < len(message) and Inimage:
            parts.append(Plain(message[last_end:]))
        elif Inimage == False:
            parts.append(Plain(message))
            
        # 处理本地图片
        for match in local_image_pattern.finditer(message):
            image_path = match.group(1)
            try:
                with open(image_path, 'rb') as img_file:
                    img_bytes = img_file.read()
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                return [Image(base64=img_base64)]
            except Exception as e:
                return [Plain(f"[Error loading image: {e}]")]

        Inimage = False
        return parts if parts else [Plain(message)]
    
    def __del__(self):
        pass