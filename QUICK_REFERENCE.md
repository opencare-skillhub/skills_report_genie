# Skill Report Genie - 快速参考指南

**版本**：v1.5
**更新日期**：2026-01-19
**文档总量**：6586行，10个核心文档

---

## 🚀 30秒快速开始

### 我是...谁？

- **患者/家属** → 看 [README.md](./README.md)
- **临床医生** → 看 [PATHOLOGY_ANALYSIS_BEST_PRACTICES.md](./PATHOLOGY_ANALYSIS_BEST_PRACTICES.md)
- **开发者** → 看 [DESIGN_INTEGRATION_SUMMARY.md](./DESIGN_INTEGRATION_SUMMARY.md) + [skill_design.md](./skill_design.md)
- **项目经理** → 看 [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md)

---

## 📚 文档导航地图

### 按用途分类

**我想了解...**

#### 系统功能与流程
- 📖 **项目概览** → [README.md](./README.md)
- 🔄 **完整工作流程** → [DEVELOPMENT_PLAN.md § 二](./DEVELOPMENT_PLAN.md) 
- 🎯 **系统设计总览** → [DESIGN_INTEGRATION_SUMMARY.md](./DESIGN_INTEGRATION_SUMMARY.md)

#### 病理分析与诊断
- 🧬 **多标志物同趋势分析** → [PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 一](./PATHOLOGY_ANALYSIS_BEST_PRACTICES.md)
- 📊 **病理分类决策树** → [PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 二](./PATHOLOGY_ANALYSIS_BEST_PRACTICES.md)
- ⚠️ **风险分层算法** → [PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 三](./PATHOLOGY_ANALYSIS_BEST_PRACTICES.md)
- 🔍 **49个病理指标详解** → [GENETIC_PATHOLOGY_GUIDE.md § 1.2](./GENETIC_PATHOLOGY_GUIDE.md) + [reference/病例报告指标说明.md](./reference/病例报告指标说明.md)
- 🧪 **胰腺肿瘤免疫表达谱** → [reference/胰腺癌典型病理.md](./reference/胰腺癌典型病理.md)

#### 基因分析
- 🔬 **基因特征提取** → [GENETIC_PATHOLOGY_GUIDE.md § 1.1](./GENETIC_PATHOLOGY_GUIDE.md)
- 📚 **基因科普教育** → [GENETIC_PATHOLOGY_GUIDE.md § 2.1](./GENETIC_PATHOLOGY_GUIDE.md)

#### 临床试验匹配
- 🏥 **API配置与使用** → [CLINICALTRIALS_API_GUIDE.md](./CLINICALTRIALS_API_GUIDE.md)
- 🎯 **智能匹配算法** → [GENETIC_PATHOLOGY_GUIDE.md § 第三部分](./GENETIC_PATHOLOGY_GUIDE.md)
- 📋 **三层匹配机制** → [PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 六.1](./PATHOLOGY_ANALYSIS_BEST_PRACTICES.md)

#### 数据存储与管理
- 📄 **JSON格式与版本控制** → [JSON_STORAGE_GUIDE.md](./JSON_STORAGE_GUIDE.md)
- 🗄️ **SQLite数据库设计** → [SQLITE_DEPLOYMENT.md](./SQLITE_DEPLOYMENT.md)
- 🔐 **患者ID管理与脱敏** → [DEVELOPMENT_PLAN.md § 1.1](./DEVELOPMENT_PLAN.md)

#### 系统集成
- 🔌 **MCP配置与接口** → [MCP_CONFIGURATION.md](./MCP_CONFIGURATION.md) + [mcp.json](./mcp.json)
- 🧠 **子智能体调用** → [DEVELOPMENT_PLAN.md § 2.2](./DEVELOPMENT_PLAN.md)
- 🎨 **小胰宝工具集成** → [GENETIC_PATHOLOGY_GUIDE.md § 第四部分](./GENETIC_PATHOLOGY_GUIDE.md)
  - 小红卡 (应急卡片): http://xhk.xiaoyibao.com.cn
  - 小绿卡 (基因解读): https://xlk.xiaoyibao.com.cn

#### 技术与架构
- 🏗️ **系统架构设计** → [skill_design.md](./skill_design.md)
- 📱 **CA19-9趋势图设计** → [DEVELOPMENT_PLAN.md § 1.3.1](./DEVELOPMENT_PLAN.md)
- 📋 **问诊清单格式** → [DEVELOPMENT_PLAN.md § 1.4](./DEVELOPMENT_PLAN.md)

---

## 🎯 常见场景快速查找

### 场景1：患者上传胰腺癌病历

**需要的文档**：
1. 初诊流程 → [DEVELOPMENT_PLAN.md § 2.1-2.4](./DEVELOPMENT_PLAN.md)
2. 文件分类规范 → [DEVELOPMENT_PLAN.md § 2.1](./DEVELOPMENT_PLAN.md)
3. JSON存储格式 → [JSON_STORAGE_GUIDE.md](./JSON_STORAGE_GUIDE.md)
4. 数据库初始化 → [SQLITE_DEPLOYMENT.md § 4.3](./SQLITE_DEPLOYMENT.md)

**预期输出**：
- ✅ 结构化病历JSON
- ✅ 患者基本信息与分期
- ✅ 病理分类与靶点
- ✅ 关键指标与趋势

---

### 场景2：分析CA19-9升高的临床意义

**关键文档**：
1. 多标志物同趋势分析 → [PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 一.2](./PATHOLOGY_ANALYSIS_BEST_PRACTICES.md)
2. 指标定义 → [reference/病例报告指标说明.md](./reference/病例报告指标说明.md)
3. 趋势图设计 → [DEVELOPMENT_PLAN.md § 1.3.1](./DEVELOPMENT_PLAN.md)

**决策树**：
```
CA19-9升高？
├─ CA50也升高 → 肿瘤进展可能性↑↑(⭐⭐⭐)
│  └─ 建议：立即调整治疗方案
├─ CA125也升高 → 腹膜转移风险↑↑↑(⭐⭐⭐)
│  └─ 建议：评估腹膜播散
├─ CA72-4也升高 → 分化程度下降↑(⭐⭐)
│  └─ 建议：考虑强化化疗
└─ 都正常 → 可能为炎症(⭐)
   └─ 建议：排除胰炎、胆囊炎
```

---

### 场景3：为患者生成综合临床报告

**工作流**：
1. [GENETIC_PATHOLOGY_GUIDE.md § 完整工作流](./GENETIC_PATHOLOGY_GUIDE.md) (第603行)
2. 包含8个步骤：基因提取 → 病理提取 → 试验匹配 → 科普教育 → 报告组合

**输出格式**：
- ✅ 基因科普部分
- ✅ 病理科普部分
- ✅ 临床试验推荐
- ✅ 后续建议
- ✅ 小胰宝资源链接

---

### 场景4：识别高危患者并推荐强化治疗

**核心算法**：
- 位置：[PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 三.1-3.2](./PATHOLOGY_ANALYSIS_BEST_PRACTICES.md)
- 输入：病理类型 + 分化程度 + 标志物
- 输出：风险等级(极高危/高危/中危/低危) + 治疗强度建议

**评分标准**：
```
病理基础分 (50-100)
+ 分化程度调整 (0-30)
+ 高危标志物累加 (每项20-25)
= 总分

极高危(≥130) → FOLFIRINOX + 靶向 + 免疫
高危(100-129) → 标准化疗 + 靶向治疗
中危(70-99) → 吉西他滨+顺铂
低危(<70) → 手术优先
```

---

### 场景5：为患者匹配最适合的临床试验

**三层匹配机制**：
- 位置：[PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 六.1](./PATHOLOGY_ANALYSIS_BEST_PRACTICES.md)

**步骤**：
1. **基础层**：病理类型 → "pancreatic cancer"
2. **靶点层**：标志物+基因 → "claudin18", "HER2", "KRAS"
3. **强化层**：组合 → "KRAS G12C AND claudin18"

**API调用**：
- 位置：[CLINICALTRIALS_API_GUIDE.md](./CLINICALTRIALS_API_GUIDE.md)
- 工具：ClinicalTrials.gov API 2.0

---

## 🔑 关键概念快速表

### 病理分类(10+种)

| 类别 | 代表类型 | 频率 | 预后 | 文档位置 |
|-----|--------|------|------|--------|
| 外分泌 | 导管腺癌 | 85% | 差 | GENETIC_PATHOLOGY_GUIDE.md |
| 外分泌 | 囊性肿瘤 | 5% | 中 | GENETIC_PATHOLOGY_GUIDE.md |
| 内分泌 | NET/G1 | 1-2% | 好 | GENETIC_PATHOLOGY_GUIDE.md |
| 罕见 | 鳞癌 | <1% | 极差 | GENETIC_PATHOLOGY_GUIDE.md |

### 多标志物组合(关键)

| 组合 | 含义 | 置信度 | 行动 |
|-----|------|--------|------|
| CA19-9↑CA50↑ | 肿瘤进展 | ⭐⭐⭐ | 调整方案 |
| CA19-9↑CA125↑ | 腹膜转移 | ⭐⭐⭐ | 评估播散 |
| CA19-9↑仅此 | 炎症可能 | ⭐ | 排除 |

### 靶点标志物

| 标志物 | 意义 | 治疗选择 | 试验关键词 |
|------|------|--------|----------|
| claudin18+ | 靶向机会 | anetumab ravtansine | claudin18 |
| HER2+ | 靶向机会 | trastuzumab | HER2 |
| MSI-H | 免疫敏感 | PD-L1抑制剂 | MSI-H |

---

## 📊 数据流向图

```
原始病历文件
    ↓
[文件扫描与分类] → DEVELOPMENT_PLAN.md § 2.1
    ↓
[信息提取与脱敏] → JSON_STORAGE_GUIDE.md
    ↓
patient_master.json
    ├─ genetic_report.json
    │   ↓
    │   [GeneticFeatureExtractor] → GENETIC_PATHOLOGY_GUIDE.md § 1.1
    │   ↓
    │   {driver_genes, risk_profile}
    │
    ├─ pathology_report.json
    │   ↓
    │   [PathologyFeatureExtractor] → GENETIC_PATHOLOGY_GUIDE.md § 1.2
    │   ↓
    │   {cancer_type, risk_level, treatment_targets}
    │       ↓
    │       [多标志物分析] → PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 一
    │       ↓
    │       [风险分层] → PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 三
    │
    └─ tumor_markers.json
        ↓
        [趋势分析] → DEVELOPMENT_PLAN.md § 1.3.1
        ↓
        {CA19-9趋势, 多标志物同趋势}

综合报告生成
    ├─ [基因科普] → GENETIC_PATHOLOGY_GUIDE.md § 2.1
    ├─ [病理科普] → GENETIC_PATHOLOGY_GUIDE.md § 2.2
    ├─ [试验匹配] → GENETIC_PATHOLOGY_GUIDE.md § 三 + CLINICALTRIALS_API_GUIDE.md
    └─ [小胰宝集成] → GENETIC_PATHOLOGY_GUIDE.md § 四

患者可用报告
```

---

## 🎨 各文档的"一句话"总结

| 文档 | 一句话总结 |
|-----|----------|
| README.md | 用户友好的功能介绍与快速开始 |
| DEVELOPMENT_PLAN.md | 项目全景蓝图与各模块详细设计 |
| GENETIC_PATHOLOGY_GUIDE.md | 病理+基因自动提取与科普教育+小胰宝工具集成 |
| PATHOLOGY_ANALYSIS_BEST_PRACTICES.md | 多标志物分析与临床决策框架 |
| CLINICALTRIALS_API_GUIDE.md | 临床试验API集成与匹配算法 |
| JSON_STORAGE_GUIDE.md | 患者数据的JSON模式与版本控制 |
| SQLITE_DEPLOYMENT.md | 数据持久化的SQLite设计与优化 |
| MCP_CONFIGURATION.md | 子智能体与Claude API的集成方案 |
| skill_design.md | 系统架构、模块划分与接口定义 |
| DESIGN_INTEGRATION_SUMMARY.md | 整个文档体系的导航与整合 |
| QUICK_REFERENCE.md | 快速导航与查询速查表（本文件）|

---

## 💡 查询技巧

### 快速搜索

**搜索关键词**：
- `多标志物` → PATHOLOGY_ANALYSIS_BEST_PRACTICES.md
- `CA19-9` → DEVELOPMENT_PLAN.md § 1.3.1 或 PATHOLOGY_ANALYSIS_BEST_PRACTICES.md
- `临床试验` → CLINICALTRIALS_API_GUIDE.md + GENETIC_PATHOLOGY_GUIDE.md § 三
- `JSON格式` → JSON_STORAGE_GUIDE.md
- `SQLite` → SQLITE_DEPLOYMENT.md
- `风险分层` → PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 三
- `病理分类` → GENETIC_PATHOLOGY_GUIDE.md § 1.2 pathology_db
- `决策树` → PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 二

### 按照开发阶段查找

**Phase 1 (数据管理)**：
- [SQLITE_DEPLOYMENT.md](./SQLITE_DEPLOYMENT.md)
- [JSON_STORAGE_GUIDE.md](./JSON_STORAGE_GUIDE.md)
- [DEVELOPMENT_PLAN.md § 2.1](./DEVELOPMENT_PLAN.md)

**Phase 2 (病理分析)**：
- [GENETIC_PATHOLOGY_GUIDE.md § 1.2](./GENETIC_PATHOLOGY_GUIDE.md)
- [PATHOLOGY_ANALYSIS_BEST_PRACTICES.md](./PATHOLOGY_ANALYSIS_BEST_PRACTICES.md)

**Phase 3 (基因分析)**：
- [GENETIC_PATHOLOGY_GUIDE.md § 1.1 + 2.1](./GENETIC_PATHOLOGY_GUIDE.md)

**Phase 4 (临床试验)**：
- [CLINICALTRIALS_API_GUIDE.md](./CLINICALTRIALS_API_GUIDE.md)
- [GENETIC_PATHOLOGY_GUIDE.md § 第三部分](./GENETIC_PATHOLOGY_GUIDE.md)

---

## 📞 常见问题速查

| Q | A | 文档 |
|---|---|------|
| CA19-9升高一定是肿瘤进展吗? | 不一定，需CA50联合判断 | PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 一 |
| 哪些标志物可以做靶向治疗? | claudin18, HER2, MSI-H | GENETIC_PATHOLOGY_GUIDE.md § 1.2 marker_db |
| 如何评估风险等级? | 病理类型+分化程度+标志物计分 | PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 三 |
| 临床试验如何匹配? | 三层机制：基础→靶点→组合 | PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 六 |
| 患者ID如何保护隐私? | hash(姓名+出生年份+医院+病例号) | DEVELOPMENT_PLAN.md § 1.1 |
| 数据如何版本控制? | JSON中含version_v1/v2/v3 | JSON_STORAGE_GUIDE.md |

---

## 🔗 文档版本追踪

```
v1.5 (2026-01-19) ✅ 当前版本
├─ GENETIC_PATHOLOGY_GUIDE.md v1.5 (49指标 + 多标志物分析 + 风险分层)
├─ PATHOLOGY_ANALYSIS_BEST_PRACTICES.md v1.0 (新增)
├─ DESIGN_INTEGRATION_SUMMARY.md v1.0 (新增)
├─ DEVELOPMENT_PLAN.md v1.5 (完整)
└─ 其他文档 v1.2-1.4 (稳定)

v1.4 → v1.5 主要变化
┣ 集成胰腺癌免疫表达谱(reference文档)
┣ 完整的49个病理指标定义
┣ 多标志物同趋势分析引擎
┣ 综合风险分层算法
┣ 临床决策树与最佳实践
┗ 完整的文档体系整合说明
```

---

**使用建议**：
1. 首次使用 → 先看 README.md + DESIGN_INTEGRATION_SUMMARY.md
2. 深入学习 → 按照 Phase 阶段顺序阅读相关文档
3. 日常查询 → 使用本快速参考 + Ctrl+F搜索关键词
4. 代码实现 → 参考 skill_design.md + 各模块详细设计文档

**最后更新**：2026-01-19
**维护者**：Skill Report Genie 开发团队
