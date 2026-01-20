# Phase 5 患者和医生使用指南

**版本**: 1.0  
**日期**: 2026-01-19  
**语言**: 中文

---

## 📖 目录

1. [患者使用指南](#患者使用指南)
2. [医生操作手册](#医生操作手册)
3. [系统管理员指南](#系统管理员指南)
4. [常见问题](#常见问题)
5. [故障排查](#故障排查)

---

## 患者使用指南

### 概述

病情报告Web系统帮助患者安全、便捷地查看和管理个人的医学报告。所有数据都采用密码保护，确保您的隐私和安全。

### 1. 访问报告

#### 第一步：获取访问链接和密码

您将收到来自医疗机构的邮件，邮件中包含：
- **访问链接**: https://patient-reports.edgeone.com/xxxxx
- **访问密码**: 例如 K7@mQx9pL2$j

⚠️ **重要提示**：
- 密码是私密的，请勿分享给他人
- 链接有效期为24小时
- 过期后需要申请新的链接

#### 第二步：打开链接

1. 复制邮件中的访问链接
2. 在浏览器中打开该链接
3. 您将看到密码输入页面

#### 第三步：输入密码

1. 在密码框中输入您收到的密码
2. 点击"访问报告"按钮
3. 密码正确后，您的报告将显示

⚠️ **安全提示**：
- 连续输入3次错误密码后，系统将暂停5秒
- 密码仅在您的浏览器中验证，不会被记录
- 刷新页面不会丢失内容（如果在24小时内）

### 2. 浏览报告

#### 报告包含的内容

报告分为4个选项卡：

##### 📋 速览

患者病情的快速总结，包括：
- 诊断信息
- 分期等级
- ECOG评分
- 主要基因突变

**用途**：快速了解病情要点

##### 📄 完整报告

详细的医学专业版报告，包括：
- 病情分析
- 治疗方案
- 检查结果
- 风险评估
- 并发症预警

**用途**：用于医生咨询和医学讨论

##### ❓ 问诊清单

结构化的问题清单，帮助您准备医生提问：

```
【高优先级】
- 化疗方案是否需要调整？
  关注点：当前CA19-9升高88%

【中优先级】
- 是否需要营养干预？
  关注点：体重下降5kg
```

**用途**：确保不遗漏重要问题

##### 📎 附件

包含的附件内容：
- 🎓 患者科普版 - 易懂的健康教育内容
- 📊 医学可视化 - 图表和数据展示
- 📈 标志物趋势 - 肿瘤标志物时间线

**用途**：深入了解医学信息和历史数据

#### 在选项卡间切换

1. 点击顶部的选项卡按钮（📋 📄 ❓ 📎）
2. 对应的内容将显示

### 3. 操作指南

#### 打印报告

1. 点击页面底部的 **🖨️ 打印** 按钮
2. 或使用键盘快捷键：Ctrl+P (Windows) 或 Cmd+P (Mac)
3. 选择打印机，确认打印设置
4. 点击打印

**提示**：
- 打印版本会隐藏按钮和导航
- 建议使用黑白模式打印以节省墨水
- 可以保存为PDF文件供后期查看

#### 下载PDF

1. 点击页面底部的 **📥 下载PDF** 按钮
2. 报告将下载为PDF文件
3. PDF文件已密码保护，只有您可以打开

**文件名示例**：`病情报告_2026-01-19.pdf`

#### 登出

1. 点击页面底部的 **🚪 登出** 按钮
2. 或关闭浏览器标签页
3. 24小时后自动登出

**注意**：登出后需要重新输入密码才能继续访问

### 4. 隐私和安全

#### 数据脱敏说明

为了保护您的隐私，报告中已脱敏以下信息：
- ❌ 真实姓名 → 显示为 [患者]
- ❌ 身份证号 → 显示为 [已脱敏]
- ❌ 电话号码 → 显示为 [已脱敏]
- ❌ 详细地址 → 显示为 [已脱敏]

#### 保留的信息

以下医学信息完整保留以便医学讨论：
- ✅ 诊断信息
- ✅ 基因检测结果
- ✅ 治疗方案
- ✅ 检查数据
- ✅ 肿瘤标志物

#### 会话过期

- 24小时自动过期
- 过期后需要申请新的链接
- 浏览器关闭后仍可恢复（在24小时内）

#### 密码安全

- 密码不存储在服务器
- 仅在您的浏览器中验证
- 无法被第三方获取
- 支持密码重置

---

## 医生操作手册

### 概述

医疗工作者可以使用此系统为患者生成和部署标准化病情报告，便于患者诊疗准备和后续复诊对比。

### 1. 生成患者报告

#### 步骤1：上传患者资料

使用Skill Report Genie上传患者的所有文件：
- 病历记录
- 影像报告
- 检查结果
- 用药记录
- 其他医学文档

#### 步骤2：信息提取和验证

系统将自动：
1. 扫描和分类文件
2. 提取关键医学信息
3. 生成结构化数据
4. 进行质量检查

#### 步骤3：审查和编辑

在部署前，您可以：
- 审查提取的信息
- 添加临床注解
- 调整优先级
- 验证敏感信息脱敏

#### 步骤4：生成报告

系统自动生成：
- 🔴 **完整病情报告** - 医学专业版
- 🟠 **问诊清单** - 结构化问题
- 🟡 **患者科普版** - 易懂的版本（附件）
- 🟢 **医学可视化** - 图表和数据（附件）

### 2. 部署报告

#### 部署前检查清单

- [ ] 所有医学信息正确
- [ ] 敏感个人信息已脱敏
- [ ] 患者邮箱正确
- [ ] 访问有效期设置（建议24小时）

#### 部署流程

```python
from src.web import ReportDeployer

deployer = ReportDeployer()

result = deployer.deploy_patient_report(
    patient_id='patient_001',
    report_data=patient_data,
    patient_email='patient@example.com',
    patient_name='患者名字',
    validity_hours=24,
    send_email=True
)

# 返回结果
# {
#   'success': True,
#   'url': 'https://patient-reports.edgeone.com/xxxx',
#   'password': 'K7@mQx9pL2$j',
#   'expires_at': '2026-01-20T14:22:40'
# }
```

#### 部署后

1. **验证部署**
   - 访问生成的URL测试
   - 确认密码正确
   - 检查所有内容显示正常

2. **患者通知**
   - 患者自动收到邮件
   - 邮件包含链接和密码
   - 如未收到，请检查垃圾邮件

3. **患者指导**
   - 解释报告内容
   - 说明访问方式
   - 建议在医生指导下阅读

### 3. 管理部署

#### 查看部署历史

```python
# 获取患者的部署记录
record = deployer.get_deployment_record('patient_001')
print(f"URL: {record['url']}")
print(f"密码: {record['password']}")
print(f"部署时间: {record['deployed_at']}")
print(f"过期时间: {record['expires_at']}")
```

#### 重置密码

```python
# 患者忘记密码时
result = deployer.reset_password(
    patient_id='patient_001',
    patient_email='patient@example.com'
)

# 新密码已发送到患者邮箱
print(f"新密码: {result['new_password']}")
```

#### 撤销访问

```python
# 如果需要撤销患者访问权限
deployer.revoke_access('patient_001')

# 患者将无法访问该报告
```

### 4. 数据管理

#### 部署记录保存

```python
# 保存部署记录（用于审计和备份）
deployer.save_deployment_records('deployments_2026.json')

# 从备份加载
deployer.load_deployment_records('deployments_2026.json')
```

#### 数据备份

定期备份患者报告：
- 每周备份一次部署记录
- 保存到安全的存储位置
- 包括URL、密码、时间戳

---

## 系统管理员指南

### 1. 环境配置

#### 必需的环境变量

```bash
# API配置
export EDGEONE_API_KEY="your-api-key"
export EDGEONE_API_URL="https://api.edgeone.ai/pages"

# 邮件配置
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SENDER_EMAIL="reports@hospital.com"
export SENDER_PASSWORD="your-app-password"

# 可选
export LOG_LEVEL="INFO"
export CACHE_DIR="/tmp/reports_cache"
```

#### 部署脚本

```bash
#!/bin/bash
# deploy.sh - 部署脚本

# 1. 检查环境
if [ -z "$EDGEONE_API_KEY" ]; then
  echo "ERROR: EDGEONE_API_KEY not set"
  exit 1
fi

# 2. 启动服务
python -m src.web.report_deployer &

# 3. 监控日志
tail -f logs/deployment.log

echo "系统已部署"
```

### 2. 监控和维护

#### 系统健康检查

```python
from src.web import ReportDeployer

deployer = ReportDeployer()

# 检查最近24小时的部署
recent = [r for r in deployer.deployment_records 
          if is_recent(r['deployed_at'])]

print(f"今日部署数: {len(recent)}")
print(f"成功率: {success_rate}%")
```

#### 日志审查

```
logs/
├── deployment.log      # 部署日志
├── security.log        # 安全日志
├── error.log          # 错误日志
└── access.log         # 访问日志（匿名）
```

### 3. 故障排查

#### 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 部署失败 | EdgeOne不可用 | 使用邮件转移 |
| 邮件未发送 | SMTP配置错误 | 检查邮箱配置 |
| 密码重置失败 | 邮件服务不可用 | 手动重新发送 |
| 链接过期 | 超过24小时 | 申请新链接 |

---

## 常见问题

### 患者常见问题

**Q: 我收不到邮件？**
A: 
1. 检查垃圾邮件文件夹
2. 确认邮箱地址正确
3. 联系医疗机构重新发送
4. 检查邮件是否来自 reports@hospital.com

**Q: 密码忘记了？**
A:
1. 联系医疗机构的客服
2. 我们将发送新密码到您的邮箱
3. 新密码仍然有效

**Q: 报告可以保存吗？**
A:
1. 可以打印成纸质版本
2. 可以下载为PDF文件
3. 不建议截屏（可能包含密码）

**Q: 24小时后链接过期了？**
A:
1. 这是正常的安全设置
2. 联系医疗机构申请新链接
3. 新链接将在几分钟内生成

### 医生常见问题

**Q: 如何更新患者报告？**
A:
1. 使用相同的patient_id
2. 生成新报告
3. 自动覆盖旧报告
4. 发送新链接给患者

**Q: 如何导出部署记录？**
A:
```python
deployer.save_deployment_records('export.json')
# 将JSON文件导出用于审计或备份
```

**Q: 能否修改访问有效期？**
A:
```python
# 部署时设置
deployer.deploy_patient_report(
    ...,
    validity_hours=48  # 改为48小时
)
```

---

## 故障排查

### 部署问题

#### 症状：部署失败，错误信息 "EdgeOne不可用"

**解决步骤**：
1. 检查网络连接
2. 验证API密钥
3. 检查EdgeOne服务状态
4. 切换到邮件转移方案

**代码示例**：
```python
result = manager.deploy_with_fallback(
    patient_id='test',
    html_content=html,
    fallback_strategy='email'  # 启用故障转移
)
```

### 邮件问题

#### 症状：患者未收到邮件

**解决步骤**：
1. 检查SMTP服务器配置
2. 验证发件人邮箱
3. 检查收件人邮箱是否正确
4. 查看邮件日志

**测试邮件**：
```python
from src.web import EmailSender

sender = EmailSender()
result = sender.send_custom_email(
    recipient_email='test@example.com',
    subject='测试邮件',
    text_content='这是一封测试邮件'
)
```

### 安全问题

#### 症状：密码验证失败

**检查清单**：
- [ ] 密码是否复制完整
- [ ] 是否有多余的空格
- [ ] 大小写是否正确
- [ ] 是否超过3次失败（已锁定）

#### 症状：数据泄露风险警告

**应对措施**：
1. 立即撤销相关患者访问
2. 生成新报告和密码
3. 联系所有受影响患者
4. 进行安全审计

### 获取技术支持

如遇到其他问题：

1. **查看日志**
   ```bash
   tail -f logs/error.log
   ```

2. **运行诊断**
   ```bash
   python -m tests.test_security_audit
   ```

3. **联系技术支持**
   - Email: support@hospital.com
   - Phone: +86-10-xxxx-xxxx
   - 在线文档: https://docs.hospital.com

---

## 更新和维护

### 系统更新

定期更新以获得最新功能和安全补丁：

```bash
# 检查更新
pip list --outdated

# 更新依赖
pip install --upgrade -r requirements.txt

# 重启系统
systemctl restart patient-reports
```

### 数据备份

```bash
# 定期备份
0 2 * * * /path/to/backup.sh

# 备份脚本
#!/bin/bash
BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR
cp deployments/*.json $BACKUP_DIR/
```

---

**最后更新**: 2026-01-19  
**版本**: 1.0  
**联系方式**: support@hospital.com
