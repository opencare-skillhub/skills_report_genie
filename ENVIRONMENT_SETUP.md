# 环境配置指南

**版本**: 1.0  
**日期**: 2026-01-19  
**重要**: 本指南说明如何安全配置环境变量

---

## 🔒 安全声明

**重要提示**: 
- ❌ **不要**将密钥提交到Git版本控制
- ❌ **不要**在代码中硬编码API密钥
- ✅ **应该**使用环境变量或密钥管理系统
- ✅ **应该**使用.env.template作为模板

---

## 📋 快速开始

### 1. 复制配置模板

```bash
# 复制环境变量模板
cp .env.template .env

# 复制MCP配置模板（如果使用MCP）
cp mcp.json.template mcp.json
```

### 2. 编辑配置文件

编辑 `.env` 文件，替换占位符为实际值：

```bash
# 使用你的编辑器
nano .env
# 或
vim .env
# 或
code .env
```

### 3. 验证配置

```bash
# 检查环境变量是否正确加载
python3 -c "import os; print('EDGEONE_API_KEY:', 'OK' if os.getenv('EDGEONE_API_KEY') else 'MISSING')"
```

---

## 🔐 环境变量详细配置

### 核心系统配置

#### EDGEONE_API_KEY
- **用途**: EdgeOne Pages服务的API密钥
- **来源**: EdgeOne控制台 → API管理
- **格式**: 字符串
- **示例**: `ey_xxx_xxxx`
- **必需**: 是（如果使用EdgeOne部署）

#### EDGEONE_API_URL
- **用途**: EdgeOne API端点
- **默认值**: `https://api.edgeone.ai/pages`
- **格式**: URL
- **必需**: 否（默认已设置）

### 邮件服务配置

#### SMTP_SERVER
- **用途**: SMTP服务器地址
- **常见值**:
  - Gmail: `smtp.gmail.com`
  - QQ邮箱: `smtp.qq.com`
  - 企业邮箱: `smtp.company.com`
- **格式**: 主机名或IP
- **必需**: 是

#### SMTP_PORT
- **用途**: SMTP端口
- **常见值**:
  - TLS: `587`
  - SSL: `465`
  - 明文: `25`
- **格式**: 数字
- **必需**: 是
- **推荐**: 使用TLS (587)

#### SENDER_EMAIL
- **用途**: 发件人邮箱地址
- **格式**: 有效的邮箱地址
- **示例**: `reports@hospital.com`
- **必需**: 是

#### SENDER_PASSWORD
- **用途**: SMTP认证密码
- **重要**: 
  - Gmail: 需要应用专用密码（不是账户密码）
  - QQ邮箱: 需要授权码
  - 企业邮箱: 使用实际密码或API令牌
- **格式**: 字符串
- **必需**: 是

### PubMed API配置

#### PUBMED_API_KEY
- **用途**: PubMed E-utilities API密钥
- **来源**: https://www.ncbi.nlm.nih.gov/account/
- **格式**: 字符串
- **必需**: 否（仅用于文献查询）

#### PUBMED_EMAIL
- **用途**: PubMed API邮箱（NCBI要求）
- **格式**: 邮箱地址
- **必需**: 否（与PUBMED_API_KEY配套）

### Memos API配置

#### MEMOS_API_KEY
- **用途**: Memos知识库API密钥
- **来源**: Memos服务 → 设置 → API
- **格式**: 字符串，通常以`pg-`开头
- **必需**: 否（仅用于长期记忆存储）

#### MEMOS_CHANNEL
- **用途**: Memos频道名称
- **默认值**: `MEMOS`
- **格式**: 字符串
- **必需**: 否

#### MEMOS_USER_ID
- **用途**: Memos用户标识
- **格式**: 用户邮箱或ID
- **必需**: 否

### Metaso API配置

#### METASO_API_KEY
- **用途**: Metaso知识搜索API密钥
- **来源**: Metaso平台 → API密钥
- **格式**: 字符串，通常以`mk-`开头
- **必需**: 否（仅用于知识补充）

---

## MCP配置

### mcp.json 安全配置

**原则**: 
- 使用环境变量替代硬编码值
- 参考 `mcp.json.template`

### 配置示例

```json
{
    "mcpServers": {
        "pubmed-data-server": {
            "env": {
                "PUBMED_API_KEY": "${PUBMED_API_KEY}",
                "PUBMED_EMAIL": "${PUBMED_EMAIL}"
            }
        },
        "memos-api-mcp": {
            "env": {
                "MEMOS_API_KEY": "${MEMOS_API_KEY}",
                "MEMOS_USER_ID": "${MEMOS_USER_ID}"
            }
        }
    }
}
```

### 替换环境变量

使用脚本替换环境变量：

```bash
#!/bin/bash
# setup-mcp.sh

# 从.env读取变量
set -a
source .env
set +a

# 替换mcp.json模板
envsubst < mcp.json.template > mcp.json

echo "MCP配置已生成"
```

---

## 🛡️ 安全最佳实践

### 1. 环境变量管理

✅ **推荐做法**:
```bash
# 在本地安全存储
export EDGEONE_API_KEY="your-key"

# 使用python-dotenv
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('EDGEONE_API_KEY')

# 使用密钥管理服务（生产环境）
# AWS Secrets Manager, HashiCorp Vault等
```

❌ **危险做法**:
```bash
# 不要这样做！
export API_KEY="hardcoded-secret-key"
password = "my-secret-password"  # 不要硬编码
```

### 2. 文件权限

```bash
# 限制.env文件权限（仅所有者可读）
chmod 600 .env

# 检查权限
ls -la .env
# 应该显示: -rw------- (600)
```

### 3. Git安全检查

```bash
# 检查是否有敏感文件被追踪
git log --all --oneline --source -- '.env' 'mcp.json' 'secrets*'

# 如果泄露，从历史中移除
git filter-branch --tree-filter 'rm -f .env' -- --all

# 强制推送（仅在确认后）
git push origin --force --all
```

### 4. CI/CD配置

在CI/CD系统中安全存储密钥：

**GitHub Actions**:
```yaml
env:
  EDGEONE_API_KEY: ${{ secrets.EDGEONE_API_KEY }}
  SENDER_PASSWORD: ${{ secrets.SENDER_PASSWORD }}
```

**GitLab CI**:
```yaml
variables:
  EDGEONE_API_KEY: $EDGEONE_API_KEY
  SENDER_PASSWORD: $SENDER_PASSWORD
```

---

## 📝 初始化流程

### 首次部署

1. **准备环境**
   ```bash
   git clone <repo>
   cd skill-report-genie
   
   # 创建虚拟环境
   python3 -m venv venv
   source venv/bin/activate  # 或 venv\Scripts\activate (Windows)
   
   # 安装依赖
   pip install -r requirements.txt
   ```

2. **配置密钥**
   ```bash
   cp .env.template .env
   # 编辑.env并填入真实值
   nano .env
   
   # 设置文件权限
   chmod 600 .env
   ```

3. **配置MCP**
   ```bash
   cp mcp.json.template mcp.json
   # 根据实际值编辑mcp.json或使用envsubst
   bash setup-mcp.sh
   ```

4. **初始化数据库**
   ```bash
   python -m src.database.init_database
   ```

5. **运行测试**
   ```bash
   pytest tests/
   ```

6. **启动服务**
   ```bash
   python -m src.web.report_deployer
   ```

### 后续使用

- **仅更新代码** - 无需重新配置
- **更换API密钥** - 编辑.env并重启服务
- **不需要调整初始文件结构** - 患者首次执行已完成

---

## 🐛 故障排查

### 常见问题

**问题**: `EDGEONE_API_KEY not found`

**解决**:
```bash
# 检查.env是否存在
ls -la .env

# 检查环境变量是否加载
source .env
echo $EDGEONE_API_KEY

# 如果为空，编辑.env添加实际值
```

**问题**: 邮件发送失败

**检查清单**:
```bash
# 1. 检查SMTP配置
python3 -c "
import os
print('SMTP_SERVER:', os.getenv('SMTP_SERVER'))
print('SMTP_PORT:', os.getenv('SMTP_PORT'))
print('SENDER_EMAIL:', os.getenv('SENDER_EMAIL'))
"

# 2. 测试SMTP连接
python3 -c "
import smtplib
import os
try:
    server = smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT')))
    server.starttls()
    print('SMTP连接成功')
except Exception as e:
    print(f'SMTP连接失败: {e}')
"

# 3. 检查邮箱密码是否正确
# （Gmail需要应用专用密码，QQ需要授权码）
```

**问题**: .env被意外提交

**恢复步骤**:
```bash
# 1. 检查是否已提交
git log --all --oneline -- .env

# 2. 如果已提交，从历史中移除
git filter-branch --tree-filter 'rm -f .env' -- --all

# 3. 强制推送
git push origin --force --all

# 4. 通知团队重新配置密钥
```

---

## 📋 检查清单

部署前确认：

- [ ] 已复制.env.template到.env
- [ ] 已编辑.env并填入真实值
- [ ] 已检查.env权限（chmod 600）
- [ ] 已验证SMTP配置可连接
- [ ] 已验证API密钥有效
- [ ] .env已在.gitignore中
- [ ] 未在代码中硬编码任何密钥
- [ ] 测试通过（pytest）
- [ ] MCP配置正确（如使用）

---

## 🔄 定期审查

### 每月检查

```bash
# 1. 检查密钥是否泄露
git log --all --oneline -- '.env' 'mcp.json' 'secrets*'

# 2. 检查敏感文件是否被追踪
git ls-files | grep -E '\.env|mcp\.json|secrets|password'

# 3. 审查环境变量使用
grep -r "os.getenv\|os.environ" src/ --include="*.py"
```

### 定期更新密钥

- API密钥每3个月轮换一次
- 生成新密钥时立即删除旧密钥
- 使用密钥管理服务跟踪密钥轮换

---

## 📞 获取帮助

### API密钥获取指南

- **EdgeOne**: https://cloud.tencent.com/document/product/1146/50159
- **Gmail SMTP**: https://support.google.com/accounts/answer/185833
- **QQ邮箱**: https://service.mail.qq.com/cgi-bin/help?subtype=1&id=28&no=1001256
- **PubMed API**: https://www.ncbi.nlm.nih.gov/account/
- **Memos**: https://memos.md/docs/
- **Metaso**: https://metaso.cn/docs/

---

**最后更新**: 2026-01-19  
**版本**: 1.0
