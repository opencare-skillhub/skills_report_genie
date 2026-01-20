# 项目组织结构完整指南 (2026-01-20)

## 📊 项目整体架构

```
skill-report-genie/
│
├── 🔵 核心源代码
│   └── src/                          # Python源代码模块
│       ├── processing/               # 文件处理
│       ├── file_handler/             # 文件解析
│       ├── analysis/                 # 数据分析
│       ├── agents/                   # AI智能体
│       ├── reporting/                # 报告生成
│       ├── storage/                  # 数据存储
│       ├── web/                      # Web发布
│       └── database/                 # 数据库
│
├── 🟢 活跃脚本
│   ├── process_single.py             # ⭐ 主脚本 (v2.1 已修复)
│   ├── README.md                     # 脚本说明
│   │
│   ├── scripts/
│   │   ├── legacy/                   # 废弃脚本备存 (8个)
│   │   │   ├── test_*.py
│   │   │   ├── parse_single_image.py
│   │   │   ├── process_batch.py
│   │   │   └── ...
│   │   ├── tools/                    # 工具脚本 (规划中)
│   │   └── README.md
│   │
│   ├── tests/                        # 单元测试 (规划中)
│   └── cache/                        # 缓存数据
│
├── 🔴 文档体系
│   ├── README.md                     # 项目说明 (根目录)
│   ├── SKILL.md                      # Skill定义
│   ├── docs/
│   │   ├── design/                   # 🎯 设计文档 (6个)
│   │   │   ├── skill_design.md       # 核心设计
│   │   │   ├── DEVELOPMENT_PLAN.md   # 开发方案
│   │   │   ├── GENETIC_PATHOLOGY_GUIDE.md
│   │   │   ├── PATHOLOGY_ANALYSIS_BEST_PRACTICES.md
│   │   │   ├── JSON_STORAGE_GUIDE.md
│   │   │   └── SQLITE_DEPLOYMENT.md
│   │   │
│   │   ├── implementation/           # 📋 实现指南 (11个)
│   │   │   ├── DEVELOPMENT_PRINCIPLES.md
│   │   │   ├── IMPLEMENTATION_SPEC.md
│   │   │   ├── WORKFLOW_IMPLEMENTATION.md
│   │   │   ├── WORKFLOW_REDESIGN.md
│   │   │   ├── ENVIRONMENT_SETUP.md
│   │   │   ├── PRIVACY_AND_WEB_DEPLOYMENT.md
│   │   │   ├── SECURITY_BEST_PRACTICES.md
│   │   │   ├── SECURITY_AUDIT_REPORT.md
│   │   │   ├── MULTI_SOURCE_ARCHITECTURE.md
│   │   │   ├── SYSTEM_SUMMARY.md
│   │   │   ├── DESIGN_INTEGRATION_SUMMARY.md
│   │   │   └── ...
│   │   │
│   │   ├── guides/                   # 📖 用户指南 (4个)
│   │   │   ├── QUICK_REFERENCE.md
│   │   │   ├── SINGLE_IMAGE_PARSING_GUIDE.md
│   │   │   ├── SINGLE_IMAGE_PROCESSING.md
│   │   │   └── STEPFUN_QUICK_START.md
│   │   │
│   │   ├── api/                      # 🔌 API文档 (3个)
│   │   │   ├── MCP_CONFIGURATION.md
│   │   │   ├── RAG_INTEGRATION_GUIDE.md
│   │   │   └── CLINICALTRIALS_API_GUIDE.md
│   │   │
│   │   ├── archives/                 # 📦 历史文档 (15个)
│   │   │   ├── PHASE*.md
│   │   │   ├── TEST_RESULTS.md
│   │   │   ├── CHANGELOG_STEPFUN.md
│   │   │   └── ...
│   │   │
│   │   └── README.md                 # 文档索引
│   │
│   └── records/                      # 📝 开发记录
│       ├── development/              # 版本记录
│       │   └── VERSION_2_1_CHANGELOG.md
│       ├── fixes/                    # 修复记录
│       │   └── PROCESS_SINGLE_FIX.md
│       ├── meetings/                 # 会议记录 (规划中)
│       └── README.md
│
├── 🟡 配置文件
│   ├── mcp.json                      # MCP配置
│   ├── mcp.json.template             # MCP模板
│   ├── .env                          # 环境变量 ⚠️ 勿分享
│   ├── .gitignore                    # Git忽略
│   ├── .gitattributes                # Git属性
│   └── requirements.txt              # 依赖列表
│
├── 🟣 资源文件
│   ├── ca_marker.png                 # 肿瘤标志物示例
│   ├── folder_tree.png               # 目录结构图
│   ├── reference/                    # 参考资料
│   └── cache/                        # 缓存数据
│
└── 📚 其他文件
    ├── PROJECT_ORGANIZATION.md       # ⭐ 本文件
    ├── .claude/                      # Claude配置
    ├── .git/                         # Git历史
    ├── .pytest_cache/                # pytest缓存
    └── __pycache__/                  # Python缓存
```

## 📊 文件统计总结

### 源代码
```
src/
├── processing/      : 处理流程 (5个模块)
├── file_handler/    : 文件解析 (6个模块)
├── analysis/        : 数据分析 (5个模块)
├── agents/          : AI智能体 (2个模块)
├── reporting/       : 报告生成 (1个模块)
├── storage/         : 数据存储 (2个模块)
├── web/             : Web服务 (5个模块)
└── database/        : 数据库 (2个模块)
```

### 脚本
| 目录 | 数量 | 状态 |
|------|------|------|
| 根目录 | 1 | ✅ 活跃 |
| scripts/legacy/ | 8 | 📦 归档 |
| scripts/tools/ | 0 | 🔲 规划 |

### 文档
| 目录 | 数量 | 类型 |
|------|------|------|
| docs/design/ | 6 | 🎯 设计 |
| docs/implementation/ | 11 | 📋 实现 |
| docs/guides/ | 4 | 📖 指南 |
| docs/api/ | 3 | 🔌 API |
| docs/archives/ | 15 | 📦 历史 |
| records/ | 2 | 📝 记录 |

**总计**: 41 个文档 + 1 个索引

## 🎯 快速导航

### 💡 快速开始
1. 阅读: `README.md`
2. 参考: `docs/guides/QUICK_REFERENCE.md`
3. 运行: `python process_single.py image.jpg -w /work`

### 🔧 开发者
1. 设计: `docs/design/DEVELOPMENT_PLAN.md`
2. 规范: `docs/implementation/DEVELOPMENT_PRINCIPLES.md`
3. 源代码: `src/`

### 📖 学习者
1. 概要: `docs/guides/QUICK_REFERENCE.md`
2. 详解: `docs/design/skill_design.md`
3. 实现: `docs/implementation/IMPLEMENTATION_SPEC.md`

### 🔌 集成者
1. MCP: `docs/api/MCP_CONFIGURATION.md`
2. RAG: `docs/api/RAG_INTEGRATION_GUIDE.md`
3. 临床试验: `docs/api/CLINICALTRIALS_API_GUIDE.md`

### 🚀 部署者
1. 环境: `docs/implementation/ENVIRONMENT_SETUP.md`
2. 安全: `docs/implementation/SECURITY_BEST_PRACTICES.md`
3. Web: `docs/implementation/PRIVACY_AND_WEB_DEPLOYMENT.md`

## 📋 核心文件说明

### 必读文件
| 文件 | 用途 | 优先级 |
|------|------|--------|
| README.md | 项目总览 | ⭐⭐⭐ |
| skill_design.md | 设计规范 | ⭐⭐⭐ |
| DEVELOPMENT_PLAN.md | 开发方案 | ⭐⭐⭐ |
| QUICK_REFERENCE.md | 快速参考 | ⭐⭐ |
| process_single.py | 主脚本 | ⭐⭐⭐ |

### 关键脚本
| 脚本 | 功能 | 版本 | 状态 |
|------|------|------|------|
| process_single.py | 图片处理全流程 | v2.1 | ✅ 活跃 |
| scripts/legacy/ | 历史脚本 | v1-v2 | 📦 存档 |

## 🔄 2026-01-20 整理内容

### ✅ 已完成

1. **创建新目录结构**
   - docs/ (5个子目录)
   - scripts/ (2个子目录)
   - records/ (3个子目录)

2. **文档分类整理**
   - 设计文档 → docs/design/
   - 实现文档 → docs/implementation/
   - 用户指南 → docs/guides/
   - API文档 → docs/api/
   - 过期文档 → docs/archives/

3. **脚本清理**
   - 活跃脚本 → 根目录 (1个)
   - 废弃脚本 → scripts/legacy/ (8个)

4. **记录管理**
   - 修复记录 → records/fixes/
   - 版本记录 → records/development/
   - 会议记录 → records/meetings/ (规划中)

5. **编写指引**
   - docs/README.md (文档索引)
   - scripts/README.md (脚本说明)
   - records/README.md (记录规范)
   - PROJECT_ORGANIZATION.md (本文件)

### 📊 整理统计

```
移动的脚本:     8个
移动的文档:    41个
创建的目录:    10个
新增的指引:     4个
```

## 🎯 后续维护建议

### 短期 (1周)
- [ ] 补充单元测试 (tests/)
- [ ] 验证文档链接有效性
- [ ] 更新README中的链接

### 中期 (1月)
- [ ] 补充会议记录 (records/meetings/)
- [ ] 创建tools/ 中的工具脚本
- [ ] 完成单元测试覆盖

### 长期 (3月+)
- [ ] 评估是否保留legacy脚本
- [ ] 更新过期的API文档
- [ ] 组织更完整的测试套件

## 📝 编辑文件指南

### 添加新文档
1. 确定分类: design / implementation / guides / api
2. 创建文件: 使用清晰的英文或中文名
3. 添加头部: 标题、日期、用途说明
4. 交叉引用: 链接相关文档

### 添加新脚本
1. 活跃脚本: 放在根目录
2. 辅助工具: 放在 scripts/tools/
3. 测试脚本: 放在 tests/
4. 历史脚本: 放在 scripts/legacy/

### 发布新版本
1. 更新: process_single.py 或相关模块
2. 记录: 创建 records/development/VERSION_X_Y.md
3. 验证: 通过单元测试
4. 提交: 提交Git并发布

## 🔗 关键链接

- **项目主页**: README.md
- **核心设计**: docs/design/skill_design.md
- **快速开始**: docs/guides/QUICK_REFERENCE.md
- **修复记录**: records/fixes/PROCESS_SINGLE_FIX.md
- **版本更新**: records/development/VERSION_2_1_CHANGELOG.md

## 📞 常见问题

### Q: 如何了解项目?
A: 从 README.md 开始，然后读 skill_design.md

### Q: 如何运行主脚本?
A: `python process_single.py image.jpg -w /work/dir`

### Q: 如何查看历史记录?
A: 在 records/ 或 docs/archives/ 中查找

### Q: 如何贡献代码?
A: 遵循 DEVELOPMENT_PRINCIPLES.md 的规范

### Q: 如何报告问题?
A: 创建 records/fixes/ 中的记录

## 版本信息

- **组织方案版本**: v1.0
- **最后更新**: 2026-01-20
- **项目版本**: v2.1
- **维护团队**: Skill Report Genie

---

**目标**: 通过清晰的组织结构，使项目易于导航、维护和扩展。
