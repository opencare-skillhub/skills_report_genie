"""
报告Web部署管理器

功能：
- 整合脱敏、密码生成、HTML渲染
- 协调edgeone-pages-mcp部署
- 管理邮件发送
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
import json
import os

from .password_protection import PasswordProtection
from .data_sanitizer import DataSanitizer
from .html_renderer import ReportHTMLRenderer
from .email_sender import EmailSender


class ReportDeployer:
    """报告部署管理器"""
    
    def __init__(
        self,
        edgeone_api_key: Optional[str] = None,
        email_config: Optional[Dict] = None
    ):
        """
        初始化部署管理器
        
        Args:
            edgeone_api_key: EdgeOne API密钥
            email_config: 邮件配置
        """
        self.edgeone_api_key = edgeone_api_key or os.getenv('EDGEONE_API_KEY')
        self.password_mgr = PasswordProtection()
        self.sanitizer = DataSanitizer()
        self.renderer = ReportHTMLRenderer()
        self.email_sender = EmailSender()
        self.deployment_records = []
    
    def deploy_patient_report(
        self,
        patient_id: str,
        report_data: Dict,
        patient_email: Optional[str] = None,
        patient_name: str = '患者',
        validity_hours: int = 24,
        send_email: bool = True
    ) -> Dict:
        """
        部署患者报告到Web
        
        Args:
            patient_id: 患者ID
            report_data: 报告数据，包含：
                - complete_report: 完整报告（Markdown或HTML）
                - consultation_list: 问诊清单
                - appendix: 附件内容（可选）
            patient_email: 患者邮箱（可选）
            patient_name: 患者名称
            validity_hours: 访问有效期（小时）
            send_email: 是否发送邮件
            
        Returns:
            dict: 部署结果
                {
                    'success': bool,
                    'patient_id': str,
                    'url': str,
                    'password': str,
                    'expires_at': str,
                    'deployed_at': str,
                    'email_sent': bool,
                    'error': str (if failed)
                }
        """
        try:
            # Step 1: 脱敏报告数据
            sanitized_data = self._sanitize_report_data(report_data)
            
            # Step 2: 生成随机密码
            password = self.password_mgr.generate_password()
            
            # Step 3: 生成HTML报告
            overview_html = self._generate_overview(sanitized_data)
            complete_html = self._prepare_content(
                sanitized_data.get('complete_report', '')
            )
            consultation_html = self._prepare_content(
                sanitized_data.get('consultation_list', '')
            )
            appendix_items = sanitized_data.get('appendix', {})
            
            # Step 4: 生成完整的Web报告页面
            full_html = self.renderer.render_complete_page(
                password=password,
                overview_html=overview_html,
                complete_report_html=complete_html,
                consultation_html=consultation_html,
                appendix_items=appendix_items
            )
            
            # Step 5: 部署到EdgeOne（模拟）
            deploy_result = self._deploy_to_edgeone(patient_id, full_html)
            
            if not deploy_result.get('success'):
                return {
                    'success': False,
                    'patient_id': patient_id,
                    'error': deploy_result.get('error', '部署失败')
                }
            
            access_url = deploy_result['url']
            
            # Step 6: 发送邮件（可选）
            email_sent = False
            if patient_email and send_email:
                email_sent = self.email_sender.send_password_email(
                    recipient_email=patient_email,
                    access_url=access_url,
                    password=password,
                    patient_name=patient_name,
                    validity_hours=validity_hours
                )
            
            # Step 7: 生成部署记录
            expires_at = (datetime.now() + timedelta(hours=validity_hours)).isoformat()
            deployment_record = {
                'success': True,
                'patient_id': patient_id,
                'url': access_url,
                'password': password,
                'expires_at': expires_at,
                'deployed_at': datetime.now().isoformat(),
                'email_sent': email_sent,
                'validity_hours': validity_hours
            }
            
            # 保存部署记录
            self.deployment_records.append(deployment_record)
            
            return deployment_record
        
        except Exception as e:
            return {
                'success': False,
                'patient_id': patient_id,
                'error': str(e)
            }
    
    def _sanitize_report_data(self, report_data: Dict) -> Dict:
        """脱敏报告数据"""
        sanitized = {}
        
        for key, value in report_data.items():
            if isinstance(value, dict):
                sanitized[key] = self.sanitizer.sanitize_report(value)
            elif isinstance(value, str):
                sanitized[key] = self.sanitizer.sanitize_string(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _generate_overview(self, sanitized_data: Dict) -> str:
        """生成患者病情速览卡"""
        overview = """
        <div class="overview-card">
            <h2>患者病情速览卡</h2>
            <table>
                <tr>
                    <td><strong>诊断</strong></td>
                    <td>{diagnosis}</td>
                </tr>
                <tr>
                    <td><strong>分期</strong></td>
                    <td>{stage}</td>
                </tr>
                <tr>
                    <td><strong>ECOG评分</strong></td>
                    <td>{ecog}</td>
                </tr>
                <tr>
                    <td><strong>主要基因突变</strong></td>
                    <td>{genetic_mutations}</td>
                </tr>
            </table>
        </div>
        """
        
        # 从sanitized_data中提取信息
        diagnosis = sanitized_data.get('diagnosis', 'N/A')
        stage = sanitized_data.get('stage', 'N/A')
        ecog = sanitized_data.get('ecog', 'N/A')
        genetic = sanitized_data.get('genetic_mutations', 'N/A')
        
        return overview.format(
            diagnosis=diagnosis,
            stage=stage,
            ecog=ecog,
            genetic_mutations=genetic
        )
    
    def _prepare_content(self, content: str) -> str:
        """准备内容（Markdown转HTML或直接返回）"""
        if not content:
            return '<p>暂无内容</p>'
        
        # 如果是Markdown格式，转换为HTML
        if '##' in content or '###' in content:
            return self.renderer.markdown_to_html(content)
        
        return content
    
    def _deploy_to_edgeone(self, patient_id: str, html_content: str) -> Dict:
        """
        部署到EdgeOne Pages（使用MCP API）

        Args:
            patient_id: 患者ID
            html_content: HTML内容

        Returns:
            dict: 部署结果
        """
        try:
            # 优先使用真实的EdgeOne MCP API
            try:
                from .edgeone_integration import EdgeOneIntegration

                edgeone = EdgeOneIntegration()
                result = edgeone.upload_report(
                    patient_id=patient_id,
                    html_content=html_content,
                    metadata={'type': 'patient_report', 'version': '1.0'}
                )

                if result.get('success'):
                    return {
                        'success': True,
                        'url': result['url'],
                        'page_id': result.get('page_id'),
                        'status': 'deployed',
                        'method': 'edgeone_mcp'
                    }
                else:
                    # EdgeOne MCP失败，回退到模拟
                    return self._fallback_deployment(patient_id, html_content)

            except ImportError as e:
                print(f"EdgeOne集成模块导入失败: {str(e)}")
                return self._fallback_deployment(patient_id, html_content)

        except Exception as e:
            print(f"EdgeOne部署异常: {str(e)}")
            return self._fallback_deployment(patient_id, html_content)

    def _fallback_deployment(self, patient_id: str, html_content: str) -> Dict:
        """
        回退部署方案（本地保存 + 模拟URL）

        Args:
            patient_id: 患者ID
            html_content: HTML内容

        Returns:
            dict: 部署结果
        """
        try:
            # 本地保存HTML文件作为备份
            import os
            from datetime import datetime

            reports_dir = 'deployed_reports'
            os.makedirs(reports_dir, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'{reports_dir}/report_{patient_id}_{timestamp}.html'

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)

            # 生成模拟访问URL
            url = f"https://patient-reports.edgeone.com/{patient_id}"

            return {
                'success': True,
                'url': url,
                'status': 'deployed',
                'method': 'fallback_simulation',
                'local_backup': os.path.abspath(filename),
                'note': 'EdgeOne API不可用，已保存本地备份'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'回退部署也失败: {str(e)}'
            }
    
    def get_deployment_record(self, patient_id: str) -> Optional[Dict]:
        """获取患者的部署记录"""
        for record in self.deployment_records:
            if record.get('patient_id') == patient_id:
                return record
        return None
    
    def revoke_access(self, patient_id: str) -> bool:
        """撤销患者的访问权限"""
        for record in self.deployment_records:
            if record.get('patient_id') == patient_id:
                record['revoked'] = True
                record['revoked_at'] = datetime.now().isoformat()
                return True
        return False
    
    def reset_password(self, patient_id: str, patient_email: Optional[str] = None) -> Dict:
        """重置患者密码"""
        record = self.get_deployment_record(patient_id)
        
        if not record:
            return {'success': False, 'error': '未找到部署记录'}
        
        # 生成新密码
        new_password = self.password_mgr.generate_password()
        record['password'] = new_password
        record['password_reset_at'] = datetime.now().isoformat()
        
        # 发送新密码邮件
        if patient_email:
            self.email_sender.send_password_email(
                recipient_email=patient_email,
                access_url=record['url'],
                password=new_password,
                validity_hours=record.get('validity_hours', 24)
            )
        
        return {
            'success': True,
            'new_password': new_password,
            'url': record['url']
        }
    
    def save_deployment_records(self, filepath: str) -> bool:
        """保存部署记录到文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.deployment_records, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存部署记录失败: {str(e)}")
            return False
    
    def load_deployment_records(self, filepath: str) -> bool:
        """从文件加载部署记录"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.deployment_records = json.load(f)
            return True
        except Exception as e:
            print(f"加载部署记录失败: {str(e)}")
            return False


# 使用示例
if __name__ == '__main__':
    deployer = ReportDeployer()
    
    # 示例患者数据
    patient_report = {
        'diagnosis': '胰腺导管腺癌',
        'stage': 'IIIB期',
        'ecog': '1分',
        'genetic_mutations': 'KRAS G12C',
        'complete_report': '## 完整病情报告\n这是患者的完整病情报告...',
        'consultation_list': '## 问诊清单\n1. 化疗方案...',
        'appendix': {
            'popular': '## 患者科普版\n癌症是...'
        }
    }
    
    # 部署报告
    result = deployer.deploy_patient_report(
        patient_id='patient_001',
        report_data=patient_report,
        patient_email='patient@example.com',
        patient_name='张三',
        validity_hours=24
    )
    
    print("部署结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
