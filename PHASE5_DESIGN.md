# Phase 5 设计文档：Web展示与隐私保护

**版本**: 1.0 (初步设计)  
**日期**: 2026-01-19  
**状态**: 设计阶段（等待开发）

---

## 一、核心目标

1. **Web展示** 📱
   - 通过edgeone-pages-mcp一键部署患者报告
   - 响应式设计（手机/平板/桌面）
   - 清晰的内容导航（选项卡）

2. **隐私保护** 🔒
   - 密码保护访问（强随机密码）
   - 患者数据脱敏（去除真实姓名、电话等）
   - 会话管理与自动过期（24小时）
   - 安全的密码传递（邮件）

3. **用户体验** ✨
   - 简洁的密码输入界面
   - 多选项卡导航：完整报告 + 问诊清单 + 附件
   - 支持打印和PDF导出
   - 患者友好的信息组织

---

## 二、工作流程

### 2.1 报告部署流程

```
【Phase 1-4输出】
├─ 病情报告_完整版.md (医学专业版)
├─ 问诊清单.md (结构化清单)
├─ 患者科普版.md (科普教育版 - 附件)
├─ 医学可视化报告.md (可视化 - 附件)
└─ 肿瘤标志物趋势.html (交互式图表)
    ↓
【Phase 5: Web发布模块】
├─ 脱敏检查 (去除真实姓名、电话等)
├─ 生成随机密码 (12位强密码)
├─ 生成患者专属URL
├─ 创建HTML + 密码验证脚本
├─ 部署到edgeone-pages (通过MCP)
└─ 发送邮件（包含URL和密码）
    ↓
【患者访问】
├─ 打开URL
├─ 输入密码
├─ 验证成功 → 显示报告
└─ 24小时后自动过期
```

### 2.2 患者访问流程

```
患者收到邮件
  ├─ 链接：https://patient-reports.edgeone.com/xxxx
  └─ 密码：K7@mQx9pL2$j
    ↓
打开链接 → 密码输入页面
  ├─ 输入密码
  ├─ 验证 (客户端)
  └─ 错误？→ 重试 (最多3次，然后延迟)
    ↓
报告主页面 (已认证)
  ├─ 📋 【速览】患者病情速览卡
  ├─ 📄 【完整报告】8部分医学专业版
  ├─ ❓ 【问诊清单】结构化问题清单
  ├─ 📎 【附件】
  │  ├─ 🎓 患者科普版
  │  ├─ 📊 医学可视化
  │  └─ 📈 标志物趋势图
  └─ 【操作】
     ├─ 🖨️ 打印
     ├─ 📥 下载PDF
     └─ 🚪 登出
    ↓
操作选择
  ├─ 切换选项卡 → 查看不同内容
  ├─ 打印 → 浏览器打印
  ├─ PDF导出 → 下载带密码保护的PDF
  └─ 登出 → 清除session
```

---

## 三、关键模块设计

### 3.1 密码保护模块

**文件**: `src/web/password_protection.py`

```python
import secrets
import string
from datetime import datetime, timedelta

class PasswordProtection:
    """
    密码生成和验证模块
    """
    
    def generate_password(self, length: int = 12) -> str:
        """
        生成随机强密码
        
        示例: K7@mQx9pL2$j
        特性: 包含大小写字母、数字、符号
        """
        chars = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    def create_session_token(self, patient_id: str) -> tuple:
        """
        创建会话token
        
        返回: (token, expiry_time)
        """
        token = secrets.token_urlsafe(32)
        expiry = datetime.now() + timedelta(hours=24)
        return token, expiry
```

### 3.2 脱敏模块

**文件**: `src/web/data_sanitizer.py`

```python
from typing import Dict

class DataSanitizer:
    """
    患者数据脱敏
    """
    
    SENSITIVE_FIELDS = [
        'patient_name', 'id_number', 'phone', 'address',
        'hospital_detailed', 'doctor_name'
    ]
    
    def sanitize_report(self, report: Dict) -> Dict:
        """
        脱敏报告数据
        
        规则:
        - 删除真实姓名 → [患者]
        - 删除身份证号 → [已脱敏]
        - 删除电话 → [已脱敏]
        - 删除详细地址 → [已脱敏]
        - 保留医学信息（基因、病理、治疗等）
        """
        sanitized = report.copy()
        
        for field in self.SENSITIVE_FIELDS:
            if field in sanitized:
                sanitized[field] = '[已脱敏]'
        
        # 特殊处理
        if 'real_name' in sanitized:
            del sanitized['real_name']  # 完全删除
        
        if 'diagnosis_date' in sanitized:
            # 只保留年月
            sanitized['diagnosis_date'] = sanitized['diagnosis_date'][:7]
        
        return sanitized
```

### 3.3 Web部署模块

**文件**: `src/web/report_deployer.py`

```python
import json
from datetime import datetime, timedelta
from .password_protection import PasswordProtection
from .data_sanitizer import DataSanitizer

class ReportDeployer:
    """
    报告Web部署管理
    """
    
    def __init__(self, edgeone_api_key: str):
        self.api_key = edgeone_api_key
        self.password_mgr = PasswordProtection()
        self.sanitizer = DataSanitizer()
    
    def deploy(
        self,
        patient_id: str,
        report_data: Dict,
        patient_email: str = None
    ) -> Dict:
        """
        部署报告到Web
        
        步骤:
        1. 脱敏报告数据
        2. 生成随机密码
        3. 生成HTML（含密码验证）
        4. 部署到edgeone-pages
        5. 发送邮件给患者
        """
        
        # Step 1: 脱敏
        sanitized = self.sanitizer.sanitize_report(report_data)
        
        # Step 2: 生成密码
        password = self.password_mgr.generate_password()
        
        # Step 3: 生成HTML
        html = self._generate_html(patient_id, sanitized, password)
        
        # Step 4: 部署到edgeone
        result = self._deploy_to_edgeone(patient_id, html)
        
        # Step 5: 发送邮件
        if patient_email:
            self._send_email(patient_email, result['url'], password)
        
        return {
            'patient_id': patient_id,
            'url': result['url'],
            'password': password,
            'deployed_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
        }
    
    def _generate_html(self, patient_id: str, report: Dict, password: str) -> str:
        """
        生成带密码保护的HTML
        """
        # HTML模板
        html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>患者病情报告</title>
            <style>
                /* 响应式设计 */
                body {{
                    font-family: 'Microsoft YaHei', -apple-system, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                
                .password-protect {{
                    max-width: 400px;
                    margin: 100px auto;
                    padding: 2rem;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    text-align: center;
                }}
                
                .password-protect h2 {{
                    margin-bottom: 2rem;
                    color: #0066cc;
                }}
                
                .password-protect input {{
                    width: 100%;
                    padding: 0.75rem;
                    margin-bottom: 1rem;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    font-size: 1rem;
                }}
                
                .password-protect button {{
                    width: 100%;
                    padding: 0.75rem;
                    background: #0066cc;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 1rem;
                }}
                
                .password-protect button:hover {{
                    background: #0052a3;
                }}
                
                .tabs {{
                    display: flex;
                    gap: 1rem;
                    margin: 2rem 0;
                    border-bottom: 2px solid #eee;
                }}
                
                .tab-button {{
                    padding: 0.75rem 1.5rem;
                    background: none;
                    border: none;
                    cursor: pointer;
                    font-size: 1rem;
                    border-bottom: 3px solid transparent;
                }}
                
                .tab-button.active {{
                    border-bottom-color: #0066cc;
                    color: #0066cc;
                }}
                
                .tab-content {{
                    display: none;
                }}
                
                .tab-content.active {{
                    display: block;
                }}
                
                .report-content {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                }}
                
                @media print {{
                    .password-protect, .tabs, .actions {{
                        display: none;
                    }}
                }}
            </style>
        </head>
        <body>
            <!-- 密码验证界面 -->
            <div class="password-protect" id="passwordPanel">
                <h2>🔒 患者病情报告</h2>
                <p>请输入访问密码</p>
                <input type="password" id="password" placeholder="输入密码">
                <button onclick="verifyPassword()">访问报告</button>
                <div id="error" style="color: red; margin-top: 1rem;"></div>
            </div>
            
            <!-- 报告内容（初始隐藏） -->
            <div id="reportContent" style="display: none;">
                <!-- 选项卡导航 -->
                <div class="tabs">
                    <button class="tab-button active" onclick="switchTab('overview')">
                        📋 速览
                    </button>
                    <button class="tab-button" onclick="switchTab('complete')">
                        📄 完整报告
                    </button>
                    <button class="tab-button" onclick="switchTab('consultation')">
                        ❓ 问诊清单
                    </button>
                    <button class="tab-button" onclick="switchTab('appendix')">
                        📎 附件
                    </button>
                </div>
                
                <!-- Tab 1: 速览 -->
                <div id="overview" class="tab-content active">
                    <div class="report-content">
                        <!-- 患者速览卡 -->
                        <h2>患者病情速览卡</h2>
                        <p>诊断：{{report.get('diagnosis', 'N/A')}}</p>
                        <p>分期：{{report.get('stage', 'N/A')}}</p>
                    </div>
                </div>
                
                <!-- Tab 2: 完整报告 -->
                <div id="complete" class="tab-content">
                    <div class="report-content">
                        {{report_html}}
                    </div>
                </div>
                
                <!-- Tab 3: 问诊清单 -->
                <div id="consultation" class="tab-content">
                    <div class="report-content">
                        {{consultation_html}}
                    </div>
                </div>
                
                <!-- Tab 4: 附件 -->
                <div id="appendix" class="tab-content">
                    <div class="report-content">
                        <h2>📚 附件内容</h2>
                        <ul>
                            <li><a href="#" onclick="showAppendix('popular')">🎓 患者科普版</a></li>
                            <li><a href="#" onclick="showAppendix('viz')">📊 医学可视化</a></li>
                            <li><a href="#" onclick="showAppendix('markers')">📈 标志物趋势</a></li>
                        </ul>
                    </div>
                </div>
                
                <!-- 操作按钮 -->
                <div class="actions">
                    <button onclick="window.print()">🖨️ 打印</button>
                    <button onclick="downloadPDF()">📥 下载PDF</button>
                    <button onclick="logout()">🚪 登出</button>
                </div>
            </div>
            
            <script>
                const PASSWORD = "{password}";
                let errorCount = 0;
                
                function verifyPassword() {{
                    const input = document.getElementById('password').value;
                    
                    if (input === PASSWORD) {{
                        // 密码正确
                        document.getElementById('passwordPanel').style.display = 'none';
                        document.getElementById('reportContent').style.display = 'block';
                        sessionStorage.setItem('authenticated', 'true');
                        sessionStorage.setItem('expiry', Date.now() + 24*60*60*1000);
                        errorCount = 0;
                    }} else {{
                        // 密码错误
                        errorCount++;
                        document.getElementById('error').textContent = 
                            '密码错误，请重试 (' + (3 - Math.min(errorCount, 3)) + '次机会)';
                        
                        if (errorCount >= 3) {{
                            document.getElementById('password').disabled = true;
                            document.querySelector('button').disabled = true;
                            setTimeout(() => {{
                                errorCount = 0;
                                document.getElementById('password').disabled = false;
                                document.querySelector('button').disabled = false;
                            }}, 5000);
                        }}
                    }}
                }}
                
                function switchTab(tabName) {{
                    // 隐藏所有tab内容
                    document.querySelectorAll('.tab-content').forEach(el => {{
                        el.classList.remove('active');
                    }});
                    document.querySelectorAll('.tab-button').forEach(el => {{
                        el.classList.remove('active');
                    }});
                    
                    // 显示选中的tab
                    document.getElementById(tabName).classList.add('active');
                    event.target.classList.add('active');
                }}
                
                function downloadPDF() {{
                    alert('PDF导出功能（带密码保护）');
                }}
                
                function logout() {{
                    sessionStorage.removeItem('authenticated');
                    location.reload();
                }}
                
                // 页面加载时检查session
                window.addEventListener('load', function() {{
                    const auth = sessionStorage.getItem('authenticated');
                    const expiry = sessionStorage.getItem('expiry');
                    
                    if (auth && Date.now() < expiry) {{
                        document.getElementById('passwordPanel').style.display = 'none';
                        document.getElementById('reportContent').style.display = 'block';
                    }}
                }});
            </script>
        </body>
        </html>
        """
        return html
    
    def _deploy_to_edgeone(self, patient_id: str, html: str) -> Dict:
        """通过edgeone-pages-mcp部署"""
        # 调用edgeone API
        # 返回 {'url': '...', 'status': 'success'}
        pass
    
    def _send_email(self, email: str, url: str, password: str):
        """发送密码邮件"""
        pass
```

### 3.4 Web UI渲染模块

**文件**: `src/web/html_renderer.py`

```python
import markdown
from typing import Dict

class ReportHTMLRenderer:
    """
    将Markdown报告转换为HTML
    """
    
    def render_markdown_to_html(self, markdown_content: str) -> str:
        """
        Markdown → HTML
        """
        html = markdown.markdown(
            markdown_content,
            extensions=['tables', 'toc', 'sane_lists']
        )
        return html
    
    def render_report_page(
        self,
        complete_report: str,
        consultation_list: str,
        popular_science: str = None,
        visualization: str = None
    ) -> str:
        """
        渲染完整的报告页面
        """
        # HTML框架 + 选项卡
        # 详见 src/web/templates/report.html
        pass
```

---

## 四、文件结构

```
src/web/
├── __init__.py
├── password_protection.py      # 密码生成和验证
├── data_sanitizer.py           # 数据脱敏
├── report_deployer.py          # Web部署管理
├── html_renderer.py            # HTML渲染
├── email_sender.py             # 邮件发送
└── templates/
    ├── report.html             # 报告主模板
    ├── password.html           # 密码输入页面
    └── styles.css              # 响应式样式

tests/
└── test_web_deployment.py      # Web部署测试
```

---

## 五、部署检查清单

- [ ] 所有敏感信息已脱敏
- [ ] 密码使用强随机生成
- [ ] HTML不包含XSS漏洞
- [ ] Session过期时间已设置（24小时）
- [ ] 邮件传输使用加密
- [ ] 支持多浏览器和设备
- [ ] 打印样式正确
- [ ] PDF导出功能可用

---

## 六、下一步（实现Phase 5）

1. **第1周**：
   - [ ] 实现密码生成和验证
   - [ ] 实现数据脱敏
   - [ ] 创建HTML模板

2. **第2周**：
   - [ ] 集成edgeone-pages-mcp
   - [ ] 实现部署流程
   - [ ] 实现邮件发送

3. **第3周**：
   - [ ] 响应式设计调整
   - [ ] 跨浏览器测试
   - [ ] 隐私安全审计

4. **第4周**：
   - [ ] 文档完善
   - [ ] 用户指南
   - [ ] 故障转移方案

---

**相关文档**：
- [PRIVACY_AND_WEB_DEPLOYMENT.md](PRIVACY_AND_WEB_DEPLOYMENT.md) - 详细的隐私和部署设计
- [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) - Phase 5详细需求
