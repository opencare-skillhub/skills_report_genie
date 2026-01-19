"""
邮件发送模块

功能：
- 生成邮件模板
- 发送密码和访问链接
- 支持HTML邮件和纯文本邮件
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
from datetime import datetime
import os


class EmailSender:
    """邮件发送"""
    
    # 邮件配置
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', '')
    SENDER_NAME = '病情报告助手'
    
    # 邮件内容模板
    PASSWORD_EMAIL_SUBJECT = '您的患者病情报告已准备就绪'
    
    def __init__(self, smtp_server: str = None, smtp_port: int = None,
                 sender_email: str = None, sender_password: str = None):
        """
        初始化邮件发送器
        
        Args:
            smtp_server: SMTP服务器地址
            smtp_port: SMTP服务器端口
            sender_email: 发送者邮箱
            sender_password: 发送者密码
        """
        self.smtp_server = smtp_server or self.SMTP_SERVER
        self.smtp_port = smtp_port or self.SMTP_PORT
        self.sender_email = sender_email or self.SENDER_EMAIL
        self.sender_password = sender_password or self.SENDER_PASSWORD
    
    def send_password_email(
        self,
        recipient_email: str,
        access_url: str,
        password: str,
        patient_name: str = '患者',
        validity_hours: int = 24
    ) -> bool:
        """
        发送密码邮件
        
        Args:
            recipient_email: 收件人邮箱
            access_url: 访问链接
            password: 访问密码
            patient_name: 患者名称（用于邮件内容）
            validity_hours: 有效期（小时）
            
        Returns:
            bool: 发送是否成功
        """
        subject = self.PASSWORD_EMAIL_SUBJECT
        
        # 生成邮件内容
        html_content = self._generate_password_email_html(
            access_url, password, patient_name, validity_hours
        )
        text_content = self._generate_password_email_text(
            access_url, password, patient_name, validity_hours
        )
        
        try:
            return self._send_email(recipient_email, subject, text_content, html_content)
        except Exception as e:
            print(f"邮件发送失败: {str(e)}")
            return False
    
    def send_custom_email(
        self,
        recipient_email: str,
        subject: str,
        text_content: str,
        html_content: str = None
    ) -> bool:
        """
        发送自定义邮件
        
        Args:
            recipient_email: 收件人邮箱
            subject: 邮件主题
            text_content: 纯文本内容
            html_content: HTML内容（可选）
            
        Returns:
            bool: 发送是否成功
        """
        try:
            return self._send_email(recipient_email, subject, text_content, html_content)
        except Exception as e:
            print(f"邮件发送失败: {str(e)}")
            return False
    
    def _send_email(
        self,
        recipient_email: str,
        subject: str,
        text_content: str,
        html_content: str = None
    ) -> bool:
        """
        实际发送邮件（内部方法）
        
        Args:
            recipient_email: 收件人
            subject: 主题
            text_content: 纯文本内容
            html_content: HTML内容
            
        Returns:
            bool: 是否成功
        """
        try:
            # 创建邮件
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.SENDER_NAME} <{self.sender_email}>"
            message['To'] = recipient_email
            
            # 添加纯文本部分
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            message.attach(part1)
            
            # 添加HTML部分（如果有）
            if html_content:
                part2 = MIMEText(html_content, 'html', 'utf-8')
                message.attach(part2)
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            return True
        
        except smtplib.SMTPAuthenticationError:
            print("邮件认证失败，请检查邮箱和密码")
            return False
        except smtplib.SMTPException as e:
            print(f"SMTP错误: {str(e)}")
            return False
        except Exception as e:
            print(f"未知错误: {str(e)}")
            return False
    
    def _generate_password_email_html(
        self,
        access_url: str,
        password: str,
        patient_name: str,
        validity_hours: int
    ) -> str:
        """生成HTML格式的密码邮件"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background-color: #f5f5f5;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .content {{
                    padding: 30px;
                }}
                .content p {{
                    margin: 0 0 15px 0;
                    line-height: 1.6;
                    color: #333;
                }}
                .info-box {{
                    background: #f9f9f9;
                    border-left: 4px solid #667eea;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .info-box strong {{
                    color: #667eea;
                }}
                .button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                    text-align: center;
                }}
                .button:hover {{
                    opacity: 0.9;
                }}
                .code-box {{
                    background: #f5f5f5;
                    padding: 15px;
                    border-radius: 4px;
                    font-family: 'Courier New', monospace;
                    font-size: 14px;
                    text-align: center;
                    margin: 15px 0;
                    word-break: break-all;
                }}
                .footer {{
                    border-top: 1px solid #eee;
                    padding: 20px 30px;
                    background: #f9f9f9;
                    font-size: 12px;
                    color: #999;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 患者病情报告</h1>
                </div>
                
                <div class="content">
                    <p>尊敬的{patient_name}：</p>
                    
                    <p>您的病情报告已准备就绪，请通过以下链接访问：</p>
                    
                    <div class="info-box">
                        <p><strong>📋 报告链接：</strong></p>
                        <p><a href="{access_url}" class="button">点击访问报告</a></p>
                        <p>或直接打开：<br>{access_url}</p>
                    </div>
                    
                    <div class="info-box">
                        <p><strong>🔐 访问密码：</strong></p>
                        <div class="code-box">{password}</div>
                        <p style="margin: 10px 0 0 0; font-size: 12px; color: #666;">
                            请妥善保管此密码，勿分享给他人
                        </p>
                    </div>
                    
                    <div class="info-box">
                        <p><strong>⏰ 重要提示：</strong></p>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li>此链接有效期为 {validity_hours} 小时</li>
                            <li>密码仅在您的浏览器本地验证，不会被记录</li>
                            <li>过期后需要申请新链接</li>
                        </ul>
                    </div>
                    
                    <p>如有任何问题或需要技术支持，请联系我们的客服团队。</p>
                    
                    <p>祝您安康！</p>
                </div>
                
                <div class="footer">
                    <p>此邮件由病情报告系统自动生成，请勿直接回复此邮件。</p>
                    <p>发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def _generate_password_email_text(
        self,
        access_url: str,
        password: str,
        patient_name: str,
        validity_hours: int
    ) -> str:
        """生成纯文本格式的密码邮件"""
        text = f"""
尊敬的{patient_name}：

您的病情报告已准备就绪，请通过以下链接访问：

报告链接：
{access_url}

访问密码：
{password}

重要提示：
• 此链接有效期为 {validity_hours} 小时
• 密码仅在您的浏览器本地验证，不会被记录
• 过期后需要申请新链接
• 请妥善保管此密码，勿分享给他人

如有任何问题或需要技术支持，请联系我们的客服团队。

祝您安康！

---
此邮件由病情报告系统自动生成
发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        return text


# 使用示例
if __name__ == '__main__':
    # 配置邮件服务
    sender = EmailSender()
    
    # 发送密码邮件
    success = sender.send_password_email(
        recipient_email='patient@example.com',
        access_url='https://patient-reports.edgeone.com/abc123',
        password='K7@mQx9pL2$j',
        patient_name='张三',
        validity_hours=24
    )
    
    print(f"邮件发送: {'成功' if success else '失败'}")
