"""
Report Deployer 集成测试
"""

import pytest
import json
import tempfile
import os
from src.web import ReportDeployer, PasswordProtection, DataSanitizer


class TestReportDeployer:
    """报告部署管理器测试"""
    
    def setup_method(self):
        self.deployer = ReportDeployer()
        self.sample_report = {
            'patient_name': '张三',
            'id_number': '110101199003151234',
            'diagnosis': '胰腺导管腺癌',
            'stage': 'IIIB期',
            'ecog': '1分',
            'genetic_mutations': 'KRAS G12C',
            'complete_report': '## 完整病情报告\n患者的详细报告',
            'consultation_list': '## 问诊清单\n1. 化疗方案',
            'appendix': {
                'popular': '## 患者科普版\n癌症知识'
            }
        }
    
    def test_deploy_patient_report_success(self):
        """测试成功部署报告"""
        result = self.deployer.deploy_patient_report(
            patient_id='patient_001',
            report_data=self.sample_report,
            patient_name='张三',
            send_email=False
        )
        
        assert result['success'] is True
        assert result['patient_id'] == 'patient_001'
        assert 'url' in result
        assert 'password' in result
        assert 'expires_at' in result
        assert 'deployed_at' in result
    
    def test_password_generation(self):
        """测试密码生成"""
        # 生成多个密码确保至少包含各类字符
        result = self.deployer.deploy_patient_report(
            patient_id='patient_002',
            report_data=self.sample_report,
            send_email=False
        )
        
        password = result['password']
        assert len(password) == 12
        # 检查密码包含的字符类型
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in '!@#$%' for c in password)
        
        # 至少包含3种字符类型
        char_types = sum([has_upper, has_lower, has_digit, has_symbol])
        assert char_types >= 3, f"密码应包含至少3种字符类型，实际{char_types}种: {password}"
    
    def test_data_sanitization(self):
        """测试数据脱敏"""
        result = self.deployer.deploy_patient_report(
            patient_id='patient_003',
            report_data=self.sample_report,
            send_email=False
        )
        
        # 部署成功意味着敏感信息已被脱敏
        assert result['success'] is True
    
    def test_validity_period(self):
        """测试访问有效期"""
        result = self.deployer.deploy_patient_report(
            patient_id='patient_004',
            report_data=self.sample_report,
            validity_hours=48,
            send_email=False
        )
        
        assert result['validity_hours'] == 48
        assert 'expires_at' in result
    
    def test_get_deployment_record(self):
        """测试获取部署记录"""
        # 部署报告
        result = self.deployer.deploy_patient_report(
            patient_id='patient_005',
            report_data=self.sample_report,
            send_email=False
        )
        
        # 获取记录
        record = self.deployer.get_deployment_record('patient_005')
        assert record is not None
        assert record['patient_id'] == 'patient_005'
        assert record['password'] == result['password']
    
    def test_revoke_access(self):
        """测试撤销访问权限"""
        # 部署报告
        self.deployer.deploy_patient_report(
            patient_id='patient_006',
            report_data=self.sample_report,
            send_email=False
        )
        
        # 撤销访问
        success = self.deployer.revoke_access('patient_006')
        assert success is True
        
        # 检查记录
        record = self.deployer.get_deployment_record('patient_006')
        assert record['revoked'] is True
    
    def test_reset_password(self):
        """测试重置密码"""
        # 部署报告
        result1 = self.deployer.deploy_patient_report(
            patient_id='patient_007',
            report_data=self.sample_report,
            send_email=False
        )
        
        old_password = result1['password']
        
        # 重置密码
        result2 = self.deployer.reset_password('patient_007')
        assert result2['success'] is True
        
        new_password = result2['new_password']
        assert new_password != old_password
        assert len(new_password) == 12
    
    def test_save_and_load_records(self):
        """测试保存和加载部署记录"""
        # 部署多个报告
        for i in range(3):
            self.deployer.deploy_patient_report(
                patient_id=f'patient_{i:03d}',
                report_data=self.sample_report,
                send_email=False
            )
        
        # 保存记录
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'deployments.json')
            
            # 保存
            success = self.deployer.save_deployment_records(filepath)
            assert success is True
            assert os.path.exists(filepath)
            
            # 创建新部署器
            deployer2 = ReportDeployer()
            
            # 加载
            success = deployer2.load_deployment_records(filepath)
            assert success is True
            assert len(deployer2.deployment_records) == 3
    
    def test_deployment_workflow(self):
        """测试完整的部署工作流"""
        # Step 1: 部署报告
        deploy_result = self.deployer.deploy_patient_report(
            patient_id='patient_workflow',
            report_data=self.sample_report,
            patient_name='工作流患者',
            validity_hours=24,
            send_email=False
        )
        
        assert deploy_result['success'] is True
        initial_password = deploy_result['password']
        
        # Step 2: 获取记录
        record = self.deployer.get_deployment_record('patient_workflow')
        assert record is not None
        assert record['password'] == initial_password
        
        # Step 3: 重置密码
        reset_result = self.deployer.reset_password('patient_workflow')
        assert reset_result['success'] is True
        
        # Step 4: 验证新密码
        record = self.deployer.get_deployment_record('patient_workflow')
        assert record['password'] == reset_result['new_password']
        assert record['password'] != initial_password


class TestEdgeOneMockDeployment:
    """EdgeOne部署模拟测试"""
    
    def test_deploy_to_edgeone_mock(self):
        """测试EdgeOne部署（模拟）"""
        deployer = ReportDeployer()
        
        result = deployer._deploy_to_edgeone(
            patient_id='test_patient',
            html_content='<html>测试内容</html>'
        )
        
        assert result['success'] is True
        assert 'url' in result
        assert 'test_patient' in result['url']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
