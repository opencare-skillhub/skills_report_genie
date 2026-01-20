# 开发原则和规范

**版本**: 1.0  
**日期**: 2026-01-19  
**范围**: 代码质量、项目规范、开发工作流

---

## 🎯 核心开发原则

### 1. 首次执行完成原则

> **患者首次执行时完成文件结构等初始化，后续使用仅更新，不需要对已有结构进行处理，避免浪费大量的时间和token资源。**

**含义**:
- 初始化（Phase 1）完成后，文件结构稳定
- 后续开发仅在现有结构中增删功能
- 不重构已稳定的目录和文件组织
- 不修改已定义的数据模式

**适用范围**:
- 数据库schema
- 目录结构
- 文件命名规范
- 数据存储格式

**例外情况**:
- 发现设计缺陷需要修复
- 遵守新的安全标准
- 响应用户要求的特殊需求

### 2. 安全优先原则

> **所有敏感信息通过环境变量管理，代码中禁止硬编码。**

**执行规范**:
- ✅ 使用`.env`管理所有API密钥
- ✅ 使用`os.getenv()`获取敏感信息
- ✅ 在`.gitignore`中排除`.env`和`mcp.json`
- ✅ 使用`.env.template`作为模板
- ❌ 不硬编码密钥、密码、Token
- ❌ 不在代码中记录敏感日志

**示例**:
```python
# ✅ 正确
api_key = os.getenv('EDGEONE_API_KEY')

# ❌ 错误
api_key = "sk_test_xxxxxxxxxxxx"
```

### 3. 增量开发原则

> **功能开发采用增量方式，新功能不影响已有功能。**

**版本管理**:
- 使用语义版本化 (Semantic Versioning)
- 主版本: 不兼容的API变化
- 次版本: 新功能（向后兼容）
- 补丁版本: Bug修复

**示例**:
```
v1.0.0 - 初始版本
v1.1.0 - 新增功能（向后兼容）
v1.1.1 - Bug修复
v2.0.0 - 不兼容变化
```

### 4. 测试驱动开发原则

> **新功能必须包含相应的测试，维持100%的测试通过率。**

**规范**:
- 新功能 = 代码 + 测试
- 测试覆盖率 > 80%
- 所有测试必须通过
- 代码审查时检查测试

**测试类型**:
```
单元测试 → 集成测试 → 端到端测试 → 安全测试
```

### 5. 文档同步原则

> **新功能必须更新相应的文档。**

**文档类型**:
- ✅ 代码注释 (Docstring)
- ✅ README.md
- ✅ API文档
- ✅ 使用指南
- ✅ 更新日志 (CHANGELOG)

**文档位置**:
```
新功能 → src/module/__init__.py   (Docstring)
       → README.md              (快速开始)
       → DEVELOPMENT_PLAN.md    (详细设计)
       → CHANGELOG.md           (更新记录)
```

---

## 📋 代码规范

### 代码风格

**Python规范** (PEP 8):
```python
# 命名约定
class MyClass:          # 类: CapWords
    def my_method():    # 方法: snake_case
        my_var = 123    # 变量: snake_case
        MY_CONST = 456  # 常量: UPPER_CASE

# 行长度: 最多79个字符（注释）或99个（代码）
# 缩进: 4个空格
# 导入顺序: 标准库 → 第三方 → 本地
```

**代码组织**:
```
src/
├── module/
│   ├── __init__.py      # 模块导出
│   ├── core.py          # 核心功能
│   ├── utils.py         # 辅助函数
│   └── config.py        # 配置管理
└── tests/
    └── test_module.py   # 测试文件
```

### 文件注释规范

```python
"""
Module/file description.

This module provides:
- Feature 1
- Feature 2

Example:
    >>> from src.module import MyClass
    >>> obj = MyClass()
    >>> result = obj.method()
"""

def my_function(param: str) -> bool:
    """
    One-line summary.
    
    Longer description if needed.
    
    Args:
        param: Parameter description.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: When condition is met.
    """
    pass
```

### 错误处理

```python
# ✅ 正确
try:
    result = api_call()
except ConnectionError as e:
    logger.error(f"API connection failed: {e}")
    raise

# ❌ 错误
try:
    result = api_call()
except Exception:
    pass  # 忽略所有错误
```

---

## 🔄 开发工作流

### 分支策略 (Git Flow)

```
main (生产)
├── release/v1.0.0      (发布准备)
└── develop (开发)
    ├── feature/auth     (新功能)
    ├── bugfix/crash     (Bug修复)
    └── hotfix/urgent    (紧急修复)
```

**分支命名**:
- `feature/short-description` - 新功能
- `bugfix/issue-number` - Bug修复
- `hotfix/urgent-issue` - 紧急修复
- `docs/update-readme` - 文档更新
- `refactor/module-name` - 代码重构

### 提交规范 (Conventional Commits)

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档
- `style`: 代码风格（不影响功能）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试
- `chore`: 构建、依赖等

**示例**:
```
feat(auth): add password reset functionality

Implement password reset via email.

Fixes #123
```

### 代码审查检查清单

- [ ] 代码符合PEP 8规范
- [ ] 包含适当的注释和文档字符串
- [ ] 新功能有相应的测试
- [ ] 所有测试通过
- [ ] 没有硬编码的敏感信息
- [ ] 错误处理完善
- [ ] 没有破坏性变化
- [ ] CHANGELOG已更新
- [ ] README已更新（如需要）

---

## 🛡️ 质量保证

### 代码质量检查

```bash
# 代码风格
pylint src/

# 类型检查
mypy src/

# 安全检查
bandit -r src/

# 依赖审计
pip-audit

# 覆盖率
pytest --cov=src tests/
```

### 持续集成 (CI)

```yaml
# 每次推送都运行
- 代码风格检查
- 单元测试
- 集成测试
- 安全扫描
- 覆盖率检查
```

### 部署流程

```
开发 → 测试 → Staging → 生产
```

**发布清单**:
- [ ] 所有测试通过
- [ ] 代码审查通过
- [ ] 文档已更新
- [ ] CHANGELOG已更新
- [ ] 版本号已更新
- [ ] 环境变量已验证

---

## 📊 性能标准

### 响应时间

| 操作 | 目标 | 测量 |
|------|------|------|
| API请求 | < 100ms | 平均响应 |
| 数据库查询 | < 50ms | 单次查询 |
| 文件处理 | < 1s | 单个文件 |
| 页面加载 | < 200ms | 首屏时间 |

### 资源使用

| 资源 | 限制 | 监控 |
|------|------|------|
| 内存 | < 256MB | 平均使用 |
| CPU | < 50% | 峰值使用 |
| 磁盘 | < 1GB | 数据库大小 |

### 测试性能

| 指标 | 目标 | 实际 |
|------|------|------|
| 单元测试 | < 1s | 0.15s ✅ |
| 集成测试 | < 5s | 0.5s ✅ |
| 全部测试 | < 10s | 2s ✅ |

---

## 🔐 安全规范

### 代码安全

- ✅ 不硬编码密钥
- ✅ 使用强密码生成
- ✅ 实施访问控制
- ✅ 验证所有输入
- ✅ 使用安全的加密
- ✅ 定期更新依赖

### 部署安全

- ✅ 环境隔离
- ✅ HTTPS加密
- ✅ 防火墙配置
- ✅ 日志审计
- ✅ 定期备份
- ✅ 应急响应计划

### 审计要求

- 每月代码审计
- 每周安全扫描
- 每季度渗透测试
- 持续依赖更新

---

## 📈 改进流程

### 问题识别

1. 报告问题（Issue）
2. 分析根本原因
3. 设计解决方案
4. 评估影响

### 改进执行

1. 创建分支
2. 实现改进
3. 编写测试
4. 更新文档
5. 提交审查
6. 合并到主分支

### 效果评估

1. 监控指标
2. 收集反馈
3. 对比基准
4. 调整策略

---

## ✅ 最终检查清单

每次提交前：

- [ ] 代码通过所有检查（pylint, mypy, bandit）
- [ ] 所有测试通过
- [ ] 覆盖率 > 80%
- [ ] 代码已审查
- [ ] 文档已更新
- [ ] 没有硬编码的密钥
- [ ] CHANGELOG已更新
- [ ] 版本号已更新（如需要）

---

**最后更新**: 2026-01-19  
**版本**: 1.0
