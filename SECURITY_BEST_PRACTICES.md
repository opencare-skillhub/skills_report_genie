# 安全最佳实践指南

**版本**: 1.0  
**日期**: 2026-01-19  
**范围**: 代码安全、数据隐私、部署安全

---

## 🔒 核心原则

### 1. 永不硬编码密钥

❌ **不允许**:
```python
API_KEY = "sk_test_xxxxxxxxxxxx"  # 危险！
password = "admin123"              # 危险！
db_url = "postgres://user:pass@host/db"  # 危险！
```

✅ **必须**:
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('API_KEY')
password = os.getenv('DB_PASSWORD')
```

### 2. 环境变量隔离

**规则**:
- 开发环境: `.env.local`
- 生产环境: 密钥管理系统（AWS Secrets Manager, HashiCorp Vault等）
- CI/CD: 平台级密钥存储（GitHub Secrets, GitLab CI Variables等）

### 3. 最小权限原则

- API密钥只授予必需的权限
- 定期轮换密钥（每3个月）
- 删除不使用的密钥

### 4. 审计和监控

- 记录所有API调用（不记录密钥）
- 定期审查访问日志
- 监控异常行为

---

## 📋 代码安全检查清单

### 提交前检查

```bash
#!/bin/bash
# pre-commit-security-check.sh

# 1. 检查敏感内容
echo "检查敏感内容..."
if grep -r "api.key\|API_KEY.*=\|password.*=\|secret.*=" src/ --include="*.py"; then
    echo "❌ 发现可能的硬编码密钥！"
    exit 1
fi

# 2. 检查.env文件
echo "检查.env文件..."
if git ls-files | grep -E '\.env|mcp\.json|secrets'; then
    echo "❌ .env或敏感文件被追踪！"
    exit 1
fi

# 3. 检查credentials
echo "检查凭证文件..."
if [ -f ".env" ] || [ -f "mcp.json" ]; then
    if git diff --cached --name-only | grep -E '\.env|mcp\.json'; then
        echo "❌ 敏感文件即将被提交！"
        exit 1
    fi
fi

# 4. 检查依赖安全
echo "检查依赖..."
pip-audit

echo "✅ 安全检查通过"
exit 0
```

### 推送前检查

```bash
#!/bin/bash
# pre-push-security-check.sh

# 检查历史中是否有敏感信息
echo "扫描Git历史..."
git log --all --oneline | head -100 | while read commit; do
    if git show ${commit:0:7} | grep -q "API_KEY\|password\|secret"; then
        echo "⚠️ 提交 ${commit:0:7} 可能包含敏感信息"
    fi
done

echo "✅ 推送安全检查完成"
```

---

## 🔐 部署安全

### 1. 环境变量验证

```python
# config.py
import os
from typing import List

REQUIRED_VARS = [
    'EDGEONE_API_KEY',
    'SMTP_SERVER',
    'SENDER_EMAIL',
]

def validate_environment():
    """验证所有必需的环境变量"""
    missing = []
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        raise EnvironmentError(
            f"缺少必需的环境变量: {', '.join(missing)}"
        )
    
    return True

# 启动应用时调用
if __name__ == '__main__':
    validate_environment()
    # 启动应用
```

### 2. 秘密存储

**生产环境推荐方案**:

```python
# 使用AWS Secrets Manager
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except Exception as e:
        raise Exception(f"Failed to retrieve secret: {e}")

# 使用HashiCorp Vault
import hvac

def get_vault_secret(path, key):
    client = hvac.Client(url='https://vault.example.com')
    secret = client.secrets.kv.v2.read_secret_version(path=path)
    return secret['data']['data'][key]
```

### 3. 日志安全

❌ **不安全**:
```python
import logging
logging.info(f"API Key: {api_key}")
logging.error(f"Error calling {api_url} with password {password}")
```

✅ **安全**:
```python
import logging

# 配置日志处理器移除敏感信息
class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        sensitive_keys = ['password', 'api_key', 'token', 'secret']
        for key in sensitive_keys:
            if key in record.getMessage().lower():
                record.msg = "[REDACTED]"
        return True

logger = logging.getLogger(__name__)
logger.addFilter(SensitiveDataFilter())
logger.info("Configuration loaded successfully")
```

---

## 🔍 安全审计

### 定期审计计划

**每周**:
- [ ] 检查错误日志中的异常
- [ ] 审查API使用情况
- [ ] 检查部署日志

**每月**:
- [ ] 完整的安全扫描
- [ ] 依赖漏洞检查
- [ ] 访问控制审查
- [ ] 密钥轮换计划

**每季度**:
- [ ] 完整的安全审计
- [ ] 渗透测试
- [ ] 合规性检查

### 安全扫描工具

```bash
# 扫描Python依赖漏洞
pip-audit

# 扫描敏感信息泄露
git-secrets --scan

# 扫描依赖安全
safety check

# 代码质量和安全
pylint src/
bandit -r src/

# 容器镜像扫描（如使用Docker）
trivy image myapp:latest
```

---

## 📝 代码审查清单

审查他人代码时，特别注意：

- [ ] 是否有硬编码的密钥或密码
- [ ] 是否使用了不安全的加密方式
- [ ] 是否有SQL注入风险
- [ ] 是否有XSS漏洞
- [ ] 是否有CSRF防护
- [ ] 是否正确验证输入
- [ ] 是否正确处理错误
- [ ] 日志是否安全（不记录敏感信息）
- [ ] 是否有适当的访问控制
- [ ] 是否使用了已知漏洞的依赖

---

## 🚨 应急响应

### 如果发生密钥泄露

**立即行动（5分钟内）**:
1. 立即撤销泄露的密钥
2. 生成新密钥
3. 部署新密钥到生产环境
4. 检查日志中的异常使用

**30分钟内**:
1. 从Git历史中移除密钥（使用`git filter-branch`或`BFG Repo-Cleaner`）
2. 通知团队
3. 审查访问日志是否有异常

**1小时内**:
1. 完整的安全审计
2. 检查是否有额外的泄露
3. 生成事件报告

### Git历史清理

```bash
# 使用BFG（推荐）
bfg --delete-files ".env" --delete-files "mcp.json"

# 或使用git filter-branch
git filter-branch --tree-filter 'rm -f .env' -- --all

# 清理垃圾
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 强制推送
git push origin --force --all --tags
```

---

## 📚 安全资源

### 推荐阅读

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python安全最佳实践](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [Django安全文档](https://docs.djangoproject.com/en/stable/topics/security/)
- [NIST网络安全框架](https://www.nist.gov/cyberframework)

### 有用的工具

- **git-secrets**: 防止密钥提交
- **pre-commit**: 提交前钩子框架
- **bandit**: Python安全检查
- **safety**: Python依赖漏洞检查
- **pip-audit**: Python依赖审计
- **OWASP ZAP**: Web应用安全扫描

### 安全社区

- [安全研究邮件列表](https://www.ietf.org/mailman/listinfo/ietf-announce/)
- [GitHub安全公告](https://github.com/advisories)
- [Python安全公告](https://pypi.org/pypa/advisory-db/)

---

## ✅ 最终检查清单

部署到生产环境前：

- [ ] 所有API密钥已从源代码中移除
- [ ] 使用环境变量管理所有密钥
- [ ] .env和mcp.json在.gitignore中
- [ ] .env文件权限设置为600
- [ ] Git历史中没有敏感信息
- [ ] 所有依赖都是最新版本
- [ ] 依赖漏洞扫描通过（pip-audit）
- [ ] 代码安全扫描通过（bandit）
- [ ] 测试覆盖率 > 80%
- [ ] 日志不包含敏感信息
- [ ] 访问控制已实施
- [ ] 加密已使用（如需要）
- [ ] 定期密钥轮换计划已制定
- [ ] 监控和告警已配置
- [ ] 事件响应流程已准备

---

**最后更新**: 2026-01-19  
**版本**: 1.0  
**负责人**: Security Team
