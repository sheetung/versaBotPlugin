# forward.py
# auther: https://github.com/Hanschase
import json
import aiohttp
import os
from typing import List, Dict

class ForwardMessage:
    def __init__(self, host: str, port: int):
        self.base_url = f"http://{host}:{port}"
    
    async def send_forward(
        self,
        launcher_id: str,
        messages: List[Dict],
        prompt: str = "默认提示",
        summary: str = "默认摘要",
        source: str = "默认来源",
        user_id: str = "100000",
        nickname: str = "消息助手"
    ) -> dict:
        """发送合并转发消息"""
        message_data = {
            "group_id": launcher_id,
            "messages": self._build_single_node(messages, user_id, nickname),
            "prompt": prompt,
            "summary": summary,
            "source": source
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/send_forward_msg",
                json=message_data,
                headers={'Content-Type': 'application/json'}
            ) as resp:
                return await resp.json()

    def _build_single_node(self, messages: List[Dict], user_id: str, nickname: str) -> List[Dict]:
        """构建单节点消息"""
        return [{
            "type": "node",
            "data": {
                "user_id": user_id,
                "nickname": nickname,
                "content": self._parse_contents(messages)
            }
        }]
    
    def _build_nodes(self, messages: List[Dict]) -> List[Dict]:
        """构建消息节点"""
        nodes = []
        for idx, msg in enumerate(messages):
            node = {
                "type": "node",
                "data": {
                    "user_id": str(100000 + idx),  # 虚拟ID
                    "nickname": "消息助手",
                    "content": self._parse_contents(msg)
                }
            }
            nodes.append(node)
        return nodes

    def _parse_contents(self, messages: Dict) -> List[Dict]:
        """解析全部消息内容"""
        contents = []
        for msg in messages:
            if 'text' in msg:
                contents.append({
                    "type": "text",
                    "data": {"text": msg['text']}
                })
            if 'image' in msg:
                contents.append({
                    "type": "image",
                    "data": {"file": self._get_media_path(msg['image'])}
                })
        return contents

    def _get_media_path(self, path: str) -> str:
        """获取合法媒体路径"""
        if path.startswith(('http://', 'https://')):
            return path
        if os.path.isfile(path):
            return f"file:///{os.path.abspath(path)}"
        return ""
