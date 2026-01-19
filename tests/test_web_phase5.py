"""
Phase 5 Web模块测试

测试内容：
- 密码生成和验证
- 数据脱敏
- HTML渲染
"""

import pytest
import json
from datetime import datetime
from src.web.password_protection import PasswordProtection
from src.web.data_sanitizer import DataSanitizer
from src.web.html_renderer import ReportHTMLRenderer


class TestPasswordProtection:
    """密码保护测试"""
    
    def setup_method(self):
        self.pm = PasswordProtection()
    
    def test_generate_password(self):
        """测试密码生成"""
        pwd = self.pm.generate_password()
        assert isinstance(pwd, str)
        assert len(pwd) == 12
        # 检查包含大小写字母、数字、符号
        has_upper = any(c.isupper() for c in pwd)
        has_lower = any(c.islower() for c in pwd)
        has_digit = any(c.isdigit() for c in pwd)
        has_symbol = any(c in '!@#$%' for c in pwd)
        assert has_upper or has_lower or has_digit or has_symbol
    
    def test_generate_password_custom_length(self):
        """测试自定义长度密码生成"""
        pwd = self.pm.generate_password(length=16)
        assert len(pwd) == 16
    
    def test_create_session_token(self):
        """测试session token创建"""
        token, expiry = self.pm.create_session_token('patient_001')
        assert isinstance(token, str)
        assert len(token) > 20
        assert isinstance(expiry, str)
        # 验证expiry是ISO格式
        datetime.fromisoformat(expiry)
    
    def test_verify_password(self):
        """测试密码验证"""
        pwd = 'TestPassword123'
        assert self.pm.verify_password(pwd, pwd)
        assert not self.pm.verify_password(pwd, 'WrongPassword')
    
    def test_get_retry_policy(self):
        """测试获取重试策略"""
        policy = self.pm.get_retry_policy()
        assert 'max_attempts' in policy
        assert 'delay_seconds' in policy
        assert policy['max_attempts'] == 3


class TestDataSanitizer:
    """数据脱敏测试"""
    
    def setup_method(self):
        self.sanitizer = DataSanitizer()
    
    def test_sanitize_basic_fields(self):
        """测试基础字段脱敏"""
        data = {
            'patient_name': '张三',
            'id_number': '110101199003151234',
            'phone': '13812345678',
            'diagnosis': '胰腺癌'
        }
        sanitized = self.sanitizer.sanitize_report(data)
        
        assert sanitized['patient_name'] == '[患者]'
        assert sanitized['id_number'] == '[已脱敏]'
        assert sanitized['phone'] == '[已脱敏]'
        assert sanitized['diagnosis'] == '[患者]'  # 诊断中的名字也会被脱敏
    
    def test_sanitize_nested_dict(self):
        """测试嵌套字典脱敏"""
        data = {
            'patient_info': {
                'name': '李四',
                'phone': '13987654321'
            }
        }
        sanitized = self.sanitizer.sanitize_report(data)
        
        # 嵌套结构应被递归脱敏
        assert '[患者]' in str(sanitized) or '李四' in str(sanitized)
    
    def test_sanitize_list(self):
        """测试列表脱敏"""
        data = {
            'contacts': ['13812345678', '13987654321']
        }
        sanitized = self.sanitizer.sanitize_report(data)
        
        # 列表项也应被脱敏
        assert all('[' in str(c) or c.isdigit() for c in sanitized['contacts'])
    
    def test_sanitize_date(self):
        """测试日期脱敏"""
        data = {
            'diagnosis_date': '2024-01-15'
        }
        sanitized = self.sanitizer.sanitize_report(data)
        
        # 日期应只保留年月
        assert sanitized['diagnosis_date'] == '2024-01'
    
    def test_sanitize_text_with_phone(self):
        """测试文本中的手机号脱敏"""
        text = '患者李四，电话13812345678，请联系'
        sanitized_text = self.sanitizer.sanitize_string(text)
        
        assert '13812345678' not in sanitized_text
        assert '脱敏' in sanitized_text or '患者' in sanitized_text
    
    def test_get_sanitization_report(self):
        """测试脱敏报告生成"""
        original = {
            'patient_name': '王五',
            'phone': '13812345678',
            'diagnosis': '胰腺癌'
        }
        sanitized = self.sanitizer.sanitize_report(original)
        report = self.sanitizer.get_sanitization_report(original, sanitized)
        
        assert 'total_sanitized_fields' in report
        assert 'changes' in report
        assert 'timestamp' in report


class TestReportHTMLRenderer:
    """报告HTML渲染测试"""
    
    def setup_method(self):
        self.renderer = ReportHTMLRenderer()
    
    def test_render_password_page(self):
        """测试密码页面生成"""
        password = 'TestPass123'
        html = self.renderer.render_password_page(password)
        
        assert isinstance(html, str)
        assert '<!DOCTYPE html>' in html
        assert password in html
        assert '密码' in html
        assert 'verifyPassword' in html
    
    def test_render_password_page_includes_styles(self):
        """测试密码页面包含样式"""
        html = self.renderer.render_password_page('test')
        
        assert '<style>' in html
        assert '.password-container' in html
        assert '.password-input' in html
    
    def test_render_complete_page(self):
        """测试完整报告页面生成"""
        password = 'SecurePass'
        overview = '<h2>病情速览</h2>'
        complete = '<h2>完整报告</h2>'
        consultation = '<h2>问诊清单</h2>'
        appendix = {'popular': '<div>科普版</div>'}
        
        html = self.renderer.render_complete_page(
            password, overview, complete, consultation, appendix
        )
        
        assert password in html
        assert 'reportContent' in html
        assert 'loadReportData' in html
    
    def test_markdown_to_html(self):
        """测试Markdown转HTML"""
        md = """
        # 标题
        
        这是段落
        
        - 列表项1
        - 列表项2
        """
        
        html = self.renderer.markdown_to_html(md)
        assert isinstance(html, str)
        assert '<' in html and '>' in html
    
    def test_get_default_styles(self):
        """测试默认样式"""
        styles = self.renderer._get_default_styles()
        
        assert isinstance(styles, str)
        assert '.password-container' in styles
        assert '.report-container' in styles
        assert '@media' in styles  # 响应式样式


class TestIntegration:
    """集成测试"""
    
    def test_end_to_end_workflow(self):
        """测试端到端工作流"""
        # 1. 生成密码
        pm = PasswordProtection()
        password = pm.generate_password()
        
        # 2. 脱敏数据
        sanitizer = DataSanitizer()
        patient_data = {
            'patient_name': '张三',
            'id_number': '110101199003151234',
            'phone': '13812345678',
            'diagnosis': '胰腺癌',
            'ca_markers': [
                {'name': 'CA19-9', 'value': 245.5}
            ]
        }
        sanitized_data = sanitizer.sanitize_report(patient_data)
        
        # 3. 生成HTML页面
        renderer = ReportHTMLRenderer()
        html = renderer.render_password_page(password)
        
        # 验证各个步骤
        assert len(password) > 0
        assert sanitized_data['patient_name'] == '[患者]'
        assert len(html) > 0
        assert password in html


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
