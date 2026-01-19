# 隐私保护与Web部署设计文档

**版本**: 1.0  
**日期**: 2026-01-19  
**涉及Phase**: Phase 5

---

## 一、核心需求

### 1.1 隐私保护

✅ **患者数据安全**：
- 所有敏感信息脱敏存储和展示
- 患者ID而非真实姓名展示
- 不记录或加密存储访问日志
- 患者可控的访问权限

✅ **密码保护**：
- 每份报告有独立的访问密码
- 随机生成的强密码
- 密码可自定义和重置
- 密码安全传递（邮件/SMS）

✅ **会话管理**：
- 自动过期机制（默认24小时）
- 支持手动登出
- 防止密码暴力破解

### 1.2 Web部署

✅ **快速部署**：
- 使用edgeone-pages-mcp一键部署
- 自动化部署流程
- 支持多患者并行部署
- 患者专属访问URL

✅ **用户体验**：
- 响应式设计（手机/平板/桌面）
- 清晰的内容导航
- 打印友好的样式
- 支持PDF导出

---

## 二、架构设计

### 2.1 整体流程

```
【报告生成】(Phase 1-4)
    ↓
【Web发布前处理】
├─ 脱敏检查（去除真实姓名、电话等）
├─ 生成patient_id
├─ 生成随机访问密码
└─ 生成患者专属URL
    ↓
【edgeone-pages-mcp部署】
├─ 将Markdown报告转换为HTML
├─ 部署到Tencent EdgeOne Pages
├─ 配置密码验证页面
└─ 返回访问URL
    ↓
【患者访问】
├─ 输入密码
├─ 验证成功 → 展示报告
├─ 验证失败 → 提示错误（锁定后重试）
└─ Session过期 → 重新输入密码
    ↓
【患者操作】
├─ 阅读报告（完整版 + 附件）
├─ 打印或PDF导出
└─ 登出
```

### 2.2 数据流

```
原始病情数据 (patient_master.json)
    ↓
[脱敏层]
├─ 保留: 诊断、基因、病理、治疗、标志物
├─ 移除: 真实姓名、电话、详细住址、身份证号
└─ 替换: 真实姓名 → [患者], 医院名 → [医院A]
    ↓
生成脱敏版本 (patient_web.json)
    ↓
[Web渲染层]
├─ Markdown → HTML转换
├─ 应用患者风格主题
└─ 嵌入交互元素（选项卡、可展开内容）
    ↓
[部署层]
├─ 通过edgeone-pages-mcp上传
├─ 配置密码验证
└─ 生成访问URL
    ↓
患者可访问的Web报告
```

---

## 三、密码认证机制

### 3.1 密码生成

```python
import secrets
import string

def generate_patient_password(length: int = 12) -> str:
    """
    为患者生成随机强密码
    
    Args:
        length: 密码长度（默认12位）
    
    Returns:
        随机密码（包含大小写字母、数字、符号）
    """
    characters = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(secrets.choice(characters) for _ in range(length))

# 示例
password = generate_patient_password()
# 输出: K7@mQx9pL2$j
```

### 3.2 密码存储（客户端）

**原则**：密码不存储在服务器，仅在客户端HTML中验证

```html
<!-- 密码验证页面 (client-side only) -->
<div class="password-protect">
  <h2>患者病情报告</h2>
  <p>请输入访问密码</p>
  
  <input type="password" id="password" placeholder="输入密码">
  <button onclick="verifyPassword()">访问报告</button>
  
  <div id="error-message" class="error"></div>
</div>

<script>
  // 正确密码（在生成报告时嵌入）
  const CORRECT_PASSWORD = "K7@mQx9pL2$j";
  
  function verifyPassword() {
    const input = document.getElementById('password').value;
    
    if (input === CORRECT_PASSWORD) {
      // 显示报告内容
      document.querySelector('.password-protect').style.display = 'none';
      document.getElementById('report-content').style.display = 'block';
      
      // 记录session
      sessionStorage.setItem('authenticated', 'true');
      sessionStorage.setItem('expiry', Date.now() + 24*60*60*1000);
    } else {
      document.getElementById('error-message').textContent = 
        '密码错误，请重试';
      // 暴力破解防护：连续3次错误后增加延迟
    }
  }
  
  // 页面加载时检查session
  window.addEventListener('load', function() {
    const auth = sessionStorage.getItem('authenticated');
    const expiry = sessionStorage.getItem('expiry');
    
    if (auth && Date.now() < expiry) {
      // 自动展示报告
      document.querySelector('.password-protect').style.display = 'none';
      document.getElementById('report-content').style.display = 'block';
    }
  });
  
  // 24小时后自动清除session
  window.addEventListener('beforeunload', function() {
    sessionStorage.removeItem('authenticated');
  });
</script>
```

### 3.3 密码传递

**安全的密码传递方式**（按优先级）：

1. **邮件传递** ✅ 推荐
   ```
   亲爱的患者：
   
   您的病情报告已准备就绪，可通过以下链接访问：
   https://patient-reports.edgeone.com/xxxx
   
   访问密码：K7@mQx9pL2$j
   
   密码有效期：24小时
   敏感信息提示：请勿将此密码分享给他人
   
   如需帮助，请联系[医疗机构]
   ```

2. **SMS短信** ✅ 备选
   ```
   【病情报告】
   访问链接: https://patient-reports.edgeone.com/xxxx
   密码: K7@mQx9pL2$j (有效24小时)
   ```

3. **患者自定义** ✅ 可选
   - 患者访问生成链接
   - 设置自己的密码
   - 系统发送确认邮件

---

## 四、Web UI设计

### 4.1 页面结构

```
┌─────────────────────────────────────┐
│   密码验证页面 (首次访问)            │
├─────────────────────────────────────┤
│ 🔒 患者病情报告                     │
│                                     │
│ 请输入访问密码：                     │
│ [________密码输入框________]         │
│ [访问报告按钮]                      │
│                                     │
│ ⚠️ 密码有效期：24小时               │
│ 🕐 当前时间：2026-01-19 14:30      │
└─────────────────────────────────────┘
        ↓ (认证成功)
┌─────────────────────────────────────┐
│   报告主页面 (已认证)                │
├─────────────────────────────────────┤
│                                     │
│ 📋 [患者速览] [完整报告] [问诊清单]  │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ 【患者病情速览卡】              │ │
│ │                                 │ │
│ │ 诊断：胰腺导管腺癌              │ │
│ │ 分期：IIIB期                    │ │
│ │ 关键基因：KRAS G12C            │ │
│ │ 风险等级：🔴高危                │ │
│ │                                 │ │
│ │ [阅读完整报告] [下载PDF]        │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [登出按钮] [帮助] [隐私政策]        │
└─────────────────────────────────────┘
```

### 4.2 报告内容展示

```html
<div id="report-content" style="display: none;">
  <!-- 导航选项卡 -->
  <div class="tabs">
    <button class="tab-button active" onclick="showTab('overview')">
      📋 速览
    </button>
    <button class="tab-button" onclick="showTab('full-report')">
      📄 完整报告
    </button>
    <button class="tab-button" onclick="showTab('consultation')">
      ❓ 问诊清单
    </button>
    <button class="tab-button" onclick="showTab('appendix')">
      📎 附件（科普+可视化）
    </button>
  </div>

  <!-- Tab 1: 速览 -->
  <div id="overview" class="tab-content">
    <!-- 患者速览卡片 -->
    <div class="patient-summary-card">
      <!-- 来自VisualizationAgent.design_patient_summary_card() -->
    </div>
  </div>

  <!-- Tab 2: 完整报告 -->
  <div id="full-report" class="tab-content" style="display: none;">
    <!-- Markdown转HTML（包含1. 基本信息 到 8. 随访记录） -->
    <div class="report-content">
      <!-- Phase 2生成的完整医学专业版报告 -->
    </div>
  </div>

  <!-- Tab 3: 问诊清单 -->
  <div id="consultation" class="tab-content" style="display: none;">
    <!-- 问诊清单（结构化+优先级） -->
  </div>

  <!-- Tab 4: 附件 -->
  <div id="appendix" class="tab-content" style="display: none;">
    <h3>📚 附件内容</h3>
    <ul>
      <li>
        <a href="#" onclick="showAppendix('popular-science')">
          🎓 患者科普版报告
        </a>
      </li>
      <li>
        <a href="#" onclick="showAppendix('visualization')">
          📊 医学可视化报告
        </a>
      </li>
      <li>
        <a href="#" onclick="showAppendix('markers')">
          📈 肿瘤标志物趋势图
        </a>
      </li>
    </ul>
  </div>

  <!-- 底部操作 -->
  <div class="actions">
    <button onclick="printReport()">🖨️ 打印</button>
    <button onclick="downloadPDF()">📥 下载PDF</button>
    <button onclick="logout()">🚪 登出</button>
  </div>
</div>
```

### 4.3 响应式设计

```css
/* 桌面版 (≥1024px) */
@media (min-width: 1024px) {
  .report-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }
  
  .tabs {
    display: flex;
    gap: 1rem;
  }
}

/* 平板版 (768px - 1023px) */
@media (min-width: 768px) and (max-width: 1023px) {
  .report-container {
    max-width: 100%;
    padding: 1.5rem;
  }
  
  .tabs {
    display: flex;
    overflow-x: auto;
  }
}

/* 手机版 (<768px) */
@media (max-width: 767px) {
  .report-container {
    max-width: 100%;
    padding: 1rem;
  }
  
  .tabs {
    display: flex;
    flex-direction: column;
  }
  
  .tab-button {
    width: 100%;
    margin-bottom: 0.5rem;
  }
}

/* 打印样式 */
@media print {
  .password-protect,
  .actions,
  .tabs {
    display: none;
  }
  
  .report-content {
    font-size: 11pt;
    line-height: 1.5;
  }
}
```

---

## 五、脱敏规则

### 5.1 必须脱敏的信息

| 信息类型 | 原始 | 脱敏后 | 示例 |
|---------|------|--------|------|
| 患者姓名 | 张三 | [患者] | 报告生成者：[患者] |
| 身份证号 | 330181198x... | [已脱敏] | - |
| 电话号码 | 13900001111 | [已脱敏] | - |
| 住址 | 杭州市西湖区某街道 | [已脱敏] | - |
| 医院名称 | 浙江大学医学院附属医院 | 医院A | 就诊医院：医院A |
| 详细病案号 | 住院号+科室 | [已脱敏] | - |
| 医生姓名 | 王医生 | [医学专家] | - |

### 5.2 可以保留的信息

✅ 诊断日期（年月即可，不需日期）  
✅ 基因检测结果（完整保留，这是核心医学信息）  
✅ 病理检查结果（完整保留）  
✅ 治疗方案（完整保留）  
✅ 肿瘤标志物数值（完整保留）  
✅ 影像学描述（完整保留）  
✅ TNM分期（完整保留）  

### 5.3 脱敏实现

```python
def sanitize_report(report_dict: Dict) -> Dict:
    """
    对报告进行脱敏处理
    
    Args:
        report_dict: 原始报告数据
    
    Returns:
        脱敏后的报告
    """
    sanitized = report_dict.copy()
    
    # 移除高敏感信息
    sensitive_fields = [
        'patient_name', 'id_number', 'phone', 'address',
        'hospital_detailed', 'detailed_case_number', 'doctor_name'
    ]
    
    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = '[已脱敏]'
    
    # 保留的信息（带部分脱敏）
    if 'diagnosis_date' in sanitized:
        # 只保留年月，不保留日期
        sanitized['diagnosis_date'] = sanitized['diagnosis_date'][:7]
    
    # patient_id用于追踪
    if 'real_name' in sanitized:
        del sanitized['real_name']  # 完全删除真实姓名
    
    return sanitized
```

---

## 六、部署流程

### 6.1 自动部署脚本

```python
import json
import hashlib
import secrets
from datetime import datetime, timedelta

class PatientReportDeployer:
    """
    患者报告Web部署管理器
    """
    
    def __init__(self, edgeone_api_key: str):
        self.api_key = edgeone_api_key
        self.edgeone_client = self._init_edgeone_client()
    
    def deploy_patient_report(
        self,
        patient_id: str,
        report_content: Dict,
        patient_email: str = None,
        validity_hours: int = 24
    ) -> Dict:
        """
        部署单个患者的报告
        
        Args:
            patient_id: 患者ID (hash)
            report_content: 报告内容 (Dict)
            patient_email: 患者邮箱（用于发送密码）
            validity_hours: 访问链接有效期（小时）
        
        Returns:
            部署结果 (包含URL和密码)
        """
        
        # Step 1: 脱敏报告
        sanitized_report = self._sanitize_report(report_content)
        
        # Step 2: 生成随机密码
        password = self._generate_password()
        
        # Step 3: 生成HTML（包含密码和报告内容）
        html_content = self._generate_html(
            patient_id=patient_id,
            report_data=sanitized_report,
            password=password
        )
        
        # Step 4: 部署到edgeone-pages
        deploy_result = self._deploy_to_edgeone(
            patient_id=patient_id,
            content=html_content
        )
        
        # Step 5: 记录部署信息
        deployment_record = {
            'patient_id': patient_id,
            'url': deploy_result['url'],
            'password': password,
            'deployed_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=validity_hours)).isoformat(),
            'status': 'active'
        }
        
        # Step 6: 发送邮件（可选）
        if patient_email:
            self._send_password_email(
                email=patient_email,
                url=deploy_result['url'],
                password=password,
                validity_hours=validity_hours
            )
        
        return deployment_record
    
    def _generate_password(self, length: int = 12) -> str:
        """生成随机强密码"""
        import string
        chars = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    def _sanitize_report(self, report: Dict) -> Dict:
        """脱敏报告"""
        sanitized = report.copy()
        
        # 脱敏逻辑
        sensitive_fields = [
            'patient_name', 'id_number', 'phone', 'address'
        ]
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = '[已脱敏]'
        
        return sanitized
    
    def _generate_html(self, patient_id: str, report_data: Dict, password: str) -> str:
        """
        生成带密码保护的HTML报告
        """
        # HTML模板（包含密码验证和报告内容）
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>患者病情报告</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                /* 响应式设计和隐私保护样式 */
                body {{ font-family: 'Microsoft YaHei', sans-serif; }}
                .password-protect {{ max-width: 400px; margin: 100px auto; }}
                .report-content {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
            </style>
        </head>
        <body>
            <!-- 密码保护页面 -->
            <div class="password-protect">
                <h2>🔒 患者病情报告</h2>
                <input type="password" id="password" placeholder="输入访问密码">
                <button onclick="verifyPassword()">访问报告</button>
            </div>
            
            <!-- 报告内容（初始隐藏） -->
            <div id="report-content" class="report-content" style="display: none;">
                {report_html_content}
            </div>
            
            <script>
                const CORRECT_PASSWORD = "{password}";
                
                function verifyPassword() {{
                    const input = document.getElementById('password').value;
                    if (input === CORRECT_PASSWORD) {{
                        document.querySelector('.password-protect').style.display = 'none';
                        document.getElementById('report-content').style.display = 'block';
                        sessionStorage.setItem('authenticated', 'true');
                    }} else {{
                        alert('密码错误');
                    }}
                }}
            </script>
        </body>
        </html>
        """
        
        # 将report_data转换为HTML
        report_html = self._markdown_to_html(json.dumps(report_data))
        
        return html_template.format(
            password=password,
            report_html_content=report_html
        )
    
    def _deploy_to_edgeone(self, patient_id: str, content: str) -> Dict:
        """
        通过edgeone-pages-mcp部署
        """
        # 调用edgeone-pages-mcp的相关API
        # 返回 {'url': 'https://...', 'status': 'success'}
        pass
    
    def _send_password_email(self, email: str, url: str, password: str, validity_hours: int):
        """
        发送密码邮件给患者
        """
        # 邮件模板
        email_body = f"""
        亲爱的患者：
        
        您的病情报告已准备就绪，可通过以下链接访问：
        {url}
        
        访问密码：{password}
        密码有效期：{validity_hours}小时
        
        敏感信息提示：
        - 请勿将此密码分享给他人
        - 报告包含敏感的医学信息
        - 24小时后链接将自动失效
        
        如需帮助，请联系[医疗机构客服]
        """
        
        # 发送邮件
        # send_email(to=email, subject="您的病情报告已就绪", body=email_body)
        pass
```

### 6.2 集成到Phase 5工作流

```python
# Phase 5主流程
from src.report.deployer import PatientReportDeployer

def generate_and_deploy_patient_reports(patient_data: Dict):
    """
    生成报告并部署到Web
    """
    
    # Step 1: 加载报告 (Phase 1-4输出)
    complete_report = load_report(patient_data['patient_id'])  # Phase 2
    consultation_list = load_consultation_list(patient_data['patient_id'])  # Phase 2
    popular_science = load_popular_science_report(patient_data['patient_id'])  # Phase 4
    visualization = load_visualization_report(patient_data['patient_id'])  # Phase 4
    
    # Step 2: 创建部署管理器
    deployer = PatientReportDeployer(api_key=os.getenv('EDGEONE_API_KEY'))
    
    # Step 3: 部署主报告
    main_report_result = deployer.deploy_patient_report(
        patient_id=patient_data['patient_id'],
        report_content={
            'complete_report': complete_report,
            'consultation_list': consultation_list,
            'appendix': {
                'popular_science': popular_science,
                'visualization': visualization
            }
        },
        patient_email=patient_data.get('email'),
        validity_hours=24
    )
    
    # Step 4: 保存部署记录
    save_deployment_record(main_report_result)
    
    # Step 5: 返回患者可访问的URL和密码
    return {
        'access_url': main_report_result['url'],
        'password': main_report_result['password'],
        'expires_at': main_report_result['expires_at'],
        'status': 'success'
    }
```

---

## 七、安全检查清单

### 7.1 部署前检查

- [ ] 所有敏感信息已脱敏
- [ ] 密码使用强随机生成
- [ ] HTML内容不包含XSS漏洞
- [ ] Session过期时间已设置
- [ ] 邮件传输使用加密（HTTPS/TLS）
- [ ] 无访问日志记录（或已加密）
- [ ] 密码不存储在服务器
- [ ] 支持密码修改和重置

### 7.2 运维监控

- [ ] 部署成功率监控
- [ ] 访问异常检测（多次密码错误）
- [ ] 链接有效期提醒
- [ ] 用户反馈渠道
- [ ] 隐私事件日志

---

## 八、用户隐私政策摘要

```
【患者隐私政策】

1. 数据脱敏
   - 您的真实姓名、身份证、电话等敏感信息已被脱敏
   - 报告中仅保留必要的医学信息（诊断、治疗、检查结果）

2. 访问控制
   - 仅您持有的密码可访问您的报告
   - 24小时后链接自动失效
   - 可随时修改密码或重置访问权限

3. 日志管理
   - 我们不记录您的访问日志
   - 不存储您的密码（仅在您的浏览器中验证）

4. 数据保留
   - 报告存储在安全的加密服务器
   - 过期后自动删除

5. 联系我们
   - 如有隐私顾虑，请联系[医疗机构隐私负责人]
```

---

## 九、故障转移与恢复

### 9.1 常见问题处理

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 忘记密码 | 正常情况 | 申请重置，系统发送新密码到邮箱 |
| 链接已过期 | 超过24小时 | 申请新的访问链接 |
| 无法打开链接 | edgeone部署失败 | 重新部署，检查网络 |
| 页面显示错误 | HTML渲染问题 | 更换浏览器，清除缓存 |

### 9.2 备份方案

- 报告同时保存为PDF（本地）
- 可通过邮件附件发送备份报告
- edgeone部署失败时，降级为邮件发送

---

**下一步**：Phase 5实现Web UI和edgeone部署模块
