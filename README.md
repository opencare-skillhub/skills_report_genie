# Skill Report Genie - 肿瘤患者病情整理Skill

## 项目简介

**Skill Report Genie** 是一个为肿瘤患者（特别是胰腺癌患者）设计的AI驱动Skill，用于：

✅ **自动整理混乱的病情资料** - 文件扫描、分类、去重  
✅ **提取结构化病情信息** - 诊断、分期、基因检测、肿瘤标志物  
✅ **生成标准化病情报告** - 包含时间线、风险评估、并发症预警  
✅ **生成问诊清单** - 帮助患者准备医生提问  
✅ **推荐临床试验** - 基于患者基因和分期查询相关试验  

---

## 核心特点

### 🎯 患者友好
- **JSON存储**：所有数据保存为JSON文件，无需技术维护
- **版本控制**：自动版本管理（v1、v2、v3...）和日期标记
- **完全本地**：隐私第一，所有数据本地存储，无云端依赖

### 🔒 隐私保护
- **脱敏存储**：患者使用hash ID，避免明文敏感信息
- **分层授权**：对外API调用需用户明确授权
- **外漏检测**：敏感字段回显立即停止，提醒用户

### 🧬 医学专业
- **四标志物同趋势分析**：CA19-9/CA50/CA125/CA72-4
- **并发症风险预警**：胆管梗阻、肠道梗阻、门脉高压等
- **临床试验推荐**：基于基因突变和分期推荐相关试验
- **文献补充**：最新临床研究和治疗指南

### ⚡ 高效增量处理
- **哈希检测**：通过文件hash和修改时间检测新增/变更文件
- **避免重复**：不重复处理已处理的文件
- **版本历史**：完整保存演变历史，支持复诊对比

---

## 文档体系

| 文档 | 大小 | 用途 | 
|------|------|------|
| **DEVELOPMENT_PLAN.md** | 66K | 🔴 **主文档** - 完整技术设计方案（包含所有细节） |
| **JSON_STORAGE_GUIDE.md** | 13K | 数据存储和版本控制指南（患者友好） |
| **MCP_CONFIGURATION.md** | 8.6K | MCP服务集成指南（7个MCP服务） |
| **CLINICALTRIALS_API_GUIDE.md** | 17K | ClinicalTrials.gov API集成指南（查询示例） |
| **SQLITE_DEPLOYMENT.md** | 11K | SQLite可选部署指南（高级功能） |
| **mcp.json** | 1.9K | MCP生产配置（已完整配置） |

**其他参考文档**：
- skill_design.md - 原始需求文档
- 病历模版.md - 标准病历模板

---

## 关键设计方案

### 📁 数据存储（主方案）

```
patient_case/
├── _metadata/
│   ├── patient_master_v1_2024-01-15.json
│   └── patient_master_v2_2024-06-20.json  ← 版本历史
├── genetics/
├── imaging/
├── labs/
├── pathology/
├── [其他11个顶级目录...]
└── _reports/
    ├── disease_report_2024-06-20.md
    └── [输出报告...]
```

**特点**：
- JSON + 版本号 + 日期（非技术用户友好）
- 自动版本控制（v1 → v2 → v3...）
- 增量识别（hash + mtime检测变化）
- 完全本地存储，无维护需求

### 🗄️ 可选SQLite（高级功能）

启用方式：`enable_sqlite=true`

**用途**：
- 快速查询和复杂条件搜索
- 批量统计和性能优化
- 完全可选，不影响基础功能

### 🔗 MCP集成（7个服务）

| MCP | 用途 | 状态 |
|-----|------|------|
| **Quickchart-MCP** | 肿瘤标志物趋势图生成 | ✅ 已配置 |
| **memos-api-mcp** | 患者长期记忆存储 | ✅ 已配置 |
| **clinical-trials** | 临床试验检索包装 | ✅ 已配置 |
| **pubmed-data-server** | PubMed文献检索（胰腺癌定制） | ✅ 已配置 |
| **metaso** | 知识补充搜索 | ✅ 已配置 |
| **searxng-simple-mcp** | 网页搜索 | ✅ 已配置 |
| **mcp-pubmed-llm-server** | 文献智能总结 | ✅ 已配置 |

### 🔬 ClinicalTrials API

直接调用官方API：

```bash
curl -X GET "https://clinicaltrials.gov/api/v2/studies?query.cond=KRAS+G12D&pageSize=20"
```

**查询参数**：
- `query.cond`：疾病/基因（如"KRAS G12D"）
- `filter.phase`：试验阶段（PHASE1-4）
- `filter.status`：招募状态（RECRUITING等）
- `filter.locn`：地点（如"China"）

---

## 工作流程

### 初诊流程

```
病例目录上传
  ↓
【1】文件扫描和自动分类（对话确认）
  ↓
【2】敏感信息脱敏 + 文件去重 + 信息提取
  ↓
【3】长期记忆存储（memos）
  ↓
【4】报告生成
  ├─ 结构化病情报告（markdown/pdf）
  ├─ 肿瘤标志物趋势图
  ├─ 并发症风险预警
  ├─ 问诊清单
  └─ 关键信息速览（2页纸）
  ↓
【5】临床知识增强（可选，需授权）
  ├─ 临床试验推荐
  ├─ 最新文献推荐
  └─ 临床指南参考
```

### 复诊流程

```
新增资料上传
  ↓
【增量识别】检查hash+mtime → 仅处理新增/变更文件
  ↓
【信息提取】更新JSON版本（v2 → v3）
  ↓
【报告更新】生成增量更新报告和对比分析
```

---

## 技术栈

### 核心技术
- **Python 3.8+**
- **JSON** 数据存储
- **SQLite3** 可选优化
- **hashlib** 文件去重

### 文件处理
- python-magic（文件识别）
- pypdf、python-docx、openpyxl（文档解析）
- paddleOCR、mineru（OCR，可选）
- pydicom（DICOM处理，可选）

### 报告生成
- quickchart-mcp（图表生成）
- reportlab、weasyprint（PDF导出）
- echart（交互式图表，可选）

### API集成
- Claude API（子智能体）
- ClinicalTrials.gov API v2（临床试验）
- PubMed API（文献检索）
- memos API（长期记忆）

---

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repo_url>
cd skill-report-genie

# 安装依赖
pip install -r requirements.txt

# 配置MCP（mcp.json已预配置）
# 根据需要修改API密钥
```

### 2. 初始化

```python
from src.core.file_scanner import FileScanner
from src.core.data_manager import DataManager

# 扫描病例目录
scanner = FileScanner("patient_case/")
files = scanner.scan_directory()

# 初始化数据管理器
data_manager = DataManager()
```

### 3. 启动Skill

```bash
# 作为Skill运行
python -m skill_report_genie
```

---

## 开发计划（6周）

| Phase | 内容 | 周期 |
|-------|------|------|
| 1 | Skill框架 + 文件扫描 + 隐私保护 | Week 1 |
| 2 | JSON数据管理 + 文件去重 + 子智能体提示词 | Week 2 |
| 3 | 报告生成 + 肿瘤标志物图表 + quickchart集成 | Week 3 |
| 4 | 临床知识增强 + MCP集成 + ClinicalTrials API | Week 4 |
| 5 | 可选功能（DICOM、OCR、SQLite） | Week 5 |
| 6 | 测试、验证、文档完善 | Week 6 |

---

## 关键特点总结

1. **患者友好** - JSON版本文件，无需技术维护
2. **完全本地** - 所有数据本地存储，隐私保护最高  
3. **版本控制** - 完整历史记录，支持复诊对比
4. **自动化** - 版本号和日期自动管理
5. **可扩展** - 可选SQLite、DICOM、OCR等
6. **多患者** - 每患者独立目录，完全隔离
7. **高效** - Hash增量识别，避免重复处理
8. **专业** - 四标志物分析、风险预警、临床试验推荐

---

## 使用场景

### 场景1：初诊患者
患者收集2-3年的医疗资料（散乱在多个文件夹），上传到Skill：
- Skill自动扫描、分类、去重
- 提取关键信息并生成标准化报告
- 患者可打印问诊清单供医生查阅
- 推荐相关临床试验供参考

### 场景2：复诊患者
6个月后患者有新的检查结果，上传新资料：
- Skill识别新增文件，仅处理变化
- 更新病情报告和肿瘤标志物趋势图
- 显示与上次的对比分析
- 推荐符合新阶段的临床试验

### 场景3：医生参考
医生收到患者的标准化病情概览：
- 2页纸关键信息速览
- 完整的时间线和治疗史
- 风险预警和并发症提示
- 问诊重点和推荐临床方向

---

## 常见问题

**Q: 所有数据都是本地的吗？**
A: 是的。默认所有数据保存为本地JSON文件。仅当用户明确授权"网络增强模式"时，才会将脱敏信息发送到外部API（如临床试验数据库）。

**Q: 如何处理患者隐私？**
A: 
- 患者使用hash ID，避免明文敏感信息
- 文件和网络请求都进行敏感字段检测
- 外漏风险立即停止，用户确认才继续
- 遵循隐私保护全流程

**Q: 需要使用SQLite吗？**
A: 不需要。JSON方案足以满足大多数患者需求。SQLite仅作为可选优化（enable_sqlite=true），用于性能要求高的场景。

**Q: 支持哪些文件格式？**
A: PDF、Word、Excel、图片（jpg、png等）、DICOM（可选）、文本文件等。

**Q: 可以支持多个患者吗？**
A: 可以。每个患者有独立的目录和JSON文件，完全隔离。

---

## 文档快速索引

- 🔴 **完整方案**：[DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) - 从这里开始
- 💾 **数据存储**：[JSON_STORAGE_GUIDE.md](JSON_STORAGE_GUIDE.md)
- 🔬 **临床试验**：[CLINICALTRIALS_API_GUIDE.md](CLINICALTRIALS_API_GUIDE.md)
- 🧬 **基因病理科普**：[GENETIC_PATHOLOGY_GUIDE.md](GENETIC_PATHOLOGY_GUIDE.md) ✨ **新增**
- 🔗 **MCP集成**：[MCP_CONFIGURATION.md](MCP_CONFIGURATION.md)
- 🗄️ **可选数据库**：[SQLITE_DEPLOYMENT.md](SQLITE_DEPLOYMENT.md)

---

## 联系方式

- **项目地址**：/Users/qinxiaoqiang/Downloads/skill-report-genie
- **文档版本**：v1.4（2026-01-19）
- **MCP配置**：mcp.json（已完整配置）

---

**准备开始开发了吗？** 从[DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)开始！ 🚀
