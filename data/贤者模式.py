"""
sage_system.py - 可独立运行或被调用的贤者模式系统
Usage:
    独立模式：python sage_system.py [check|set] <user_id> [command]
    模块模式：from sage_system import SageSystem
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone

china_tz = timezone(timedelta(hours=8))

class SageSystem:
    """核心功能类"""
    
    _DEFAULT_CONFIG = {
        "看妹妹": {"duration": 1},  # 命令配置
        "default_duration": 2      # 默认冷却
    }

    def __init__(self, data_file='sage_data.json', config=None):
        """
        Args:
            data_file: 数据存储文件
            config: 自定义配置字典
        """
        # 文件路径处理
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_path = os.path.join(self.script_dir, data_file)
        
        # 加载配置
        self.config = config if config else self._DEFAULT_CONFIG

    def _load_data(self) -> dict:
        """私有方法：安全加载数据文件"""
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r') as f:
                return json.load(f)
        return {}

    def check_user(self, user_id: str, command: str) -> bool:
        """
        检查用户状态
        Returns:
            True: 处于冷却中
            False: 可执行操作
        """
        data = self._load_data()
        record = data.get(str(user_id))  # 确保user_id转换为字符串
        
        if not record:
            return False
        
        # 计算冷却时间
        duration = self.config.get(command, {}).get(
            'duration', self.config['default_duration']
        )
        expire_time = datetime.now(china_tz).fromisoformat(record) + timedelta(hours=duration)
        
        return datetime.now(china_tz) < expire_time

    def set_user(self, user_id: str):
        """记录用户操作时间"""
        data = self._load_data()
        data[str(user_id)] = datetime.now(china_tz).isoformat()  # 确保存储为字符串
        
        with open(self.data_path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_remaining(self, user_id: str, command: str) -> float:
        """获取剩余冷却时间（小时）"""
        if not self.check_user(user_id, command):
            return 0.0
        
        data = self._load_data()
        record_time = datetime.fromisoformat(data[str(user_id)])
        elapsed = datetime.now(china_tz) - record_time
        duration = self.config.get(command, {}).get(
            'duration', self.config['default_duration']
        )
        return max(duration - elapsed.total_seconds() / 3600, 0)

# 独立运行模式处理
def cli_handler():
    """命令行接口"""
    user_id = sys.argv[1]
    
    sage = SageSystem()  # 使用默认配置

    sage.set_user(user_id)
    print(f"✅ 用户[{user_id}] 贤者模式已激活 ")
    print(f"⏰ 记录时间：{datetime.now(china_tz).strftime('%Y-%m-%d %H:%M:%S')}")
 

if __name__ == '__main__':
    cli_handler()
