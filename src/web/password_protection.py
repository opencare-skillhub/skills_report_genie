"""
密码生成和验证模块

支持：
- 随机强密码生成（12位，包含大小写字母、数字、符号）
- Session token创建
- 暴力破解防护
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import Tuple, Dict


class PasswordProtection:
    """密码生成和验证"""
    
    SYMBOLS = "!@#$%"
    DEFAULT_LENGTH = 12
    DEFAULT_SESSION_HOURS = 24
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY_SECONDS = 300  # 5分钟
    
    def __init__(self):
        self.password_chars = string.ascii_letters + string.digits + self.SYMBOLS
    
    def generate_password(self, length: int = None) -> str:
        """
        生成随机强密码
        
        Args:
            length: 密码长度（默认12位）
            
        Returns:
            str: 随机密码，例如 K7@mQx9pL2$j
        """
        if length is None:
            length = self.DEFAULT_LENGTH
        
        return ''.join(secrets.choice(self.password_chars) for _ in range(length))
    
    def create_session_token(self, patient_id: str, validity_hours: int = None) -> Tuple[str, str]:
        """
        创建会话token
        
        Args:
            patient_id: 患者ID
            validity_hours: 有效期（小时，默认24小时）
            
        Returns:
            tuple: (token, expiry_datetime_str)
        """
        if validity_hours is None:
            validity_hours = self.DEFAULT_SESSION_HOURS
        
        token = secrets.token_urlsafe(32)
        expiry = datetime.now() + timedelta(hours=validity_hours)
        
        return token, expiry.isoformat()
    
    def verify_password(self, input_password: str, correct_password: str) -> bool:
        """
        验证密码（使用时间常量比较防止时序攻击）
        
        Args:
            input_password: 用户输入的密码
            correct_password: 正确的密码
            
        Returns:
            bool: 验证是否成功
        """
        # 使用secrets.compare_digest防止时序攻击
        return secrets.compare_digest(input_password, correct_password)
    
    def get_retry_policy(self) -> Dict:
        """
        获取暴力破解防护策略
        
        Returns:
            dict: 防护参数
        """
        return {
            'max_attempts': self.MAX_RETRY_ATTEMPTS,
            'delay_seconds': self.RETRY_DELAY_SECONDS,
            'description': f'{self.MAX_RETRY_ATTEMPTS}次错误后锁定{self.RETRY_DELAY_SECONDS}秒'
        }


# 使用示例
if __name__ == '__main__':
    pm = PasswordProtection()
    
    # 生成密码
    pwd = pm.generate_password()
    print(f"生成密码: {pwd}")
    
    # 创建session
    token, expiry = pm.create_session_token('patient_001')
    print(f"Session token: {token}")
    print(f"过期时间: {expiry}")
    
    # 获取防护策略
    policy = pm.get_retry_policy()
    print(f"防护策略: {policy}")
