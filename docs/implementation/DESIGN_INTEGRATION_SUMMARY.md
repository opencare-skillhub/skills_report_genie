# Skill Report Genie 设计文档系统整合总结

**项目版本**：v1.5 (完整的基因病理科普+智能临床试验匹配+MCP集成)
**最后更新**：2026-01-19
**文档状态**：✅ 核心设计完成，可进入实现阶段

---

## 📋 文档体系概览

### 核心规划文档

| 文档 | 版本 | 覆盖范围 | 关键内容 |
|-----|------|--------|---------|
| **DEVELOPMENT_PLAN.md** | v1.5 | 全局架构 | 工作流、数据库设计、患者ID管理、版本控制 |
| **GENETIC_PATHOLOGY_GUIDE.md** | v1.5 | 病理+基因 | 自动提取、多标志物分析、科普教育、临床试验匹配 |
| **PATHOLOGY_ANALYSIS_BEST_PRACTICES.md** | v1.0 | 病理临床决策 | 多标志物同趋势分析、风险分层算法、临床决策树 |
| **MCP_CONFIGURATION.md** | v1.3 | MCP架构 | Claude API集成、子智能体调用、数据接口 |
| **CLINICALTRIALS_API_GUIDE.md** | v1.2 | 临床试验 | ClinicalTrials.gov API、搜索策略、匹配算法 |
| **JSON_STORAGE_GUIDE.md** | v1.4 | 数据存储 | 病历JSON模式、版本控制、增量更新 |
| **SQLITE_DEPLOYMENT.md** | v1.2 | 数据库 | SQLite表结构、索引优化、备份策略 |
| **README.md** | v1.5 | 用户指南 | 功能概览、使用流程、常见问题 |
| **mcp.json** | v1.3 | MCP配置 | 工具定义、参数规范、返回格式 |
| **skill_design.md** | v1.0 | 技术设计 | 架构设计、模块划分、接口定义 |

### 参考文档

| 文档 | 内容 | 用途 |
|-----|------|------|
| **reference/胰腺癌典型病理.md** | 免疫表达谱表格 | 病理诊断标准库 |
| **reference/病例报告指标说明.md** | 49个指标定义 | 病理术语解释库 |
| **病历模版.md** | 中文病历结构 | 数据录入参考 |
| **病例模板.doc** | 打印用病历模板 | 患者自填表单 |

---

## 🔄 完整工作流程映射

### 初诊流程（用户上传病历）

```
1. 文件扫描与分类
   文档：DEVELOPMENT_PLAN.md § 2.1
   工具：file_index表(SQLite) + 分类规则
   
2. 信息提取与脱敏
   文档：DEVELOPMENT_PLAN.md § 2.2 + JSON_STORAGE_GUIDE.md
   工具：OCR + 3个子智能体 + patient_id hash生成
   输出：患者基本信息JSON
   
3. 长期记忆存储
   文档：JSON_STORAGE_GUIDE.md + SQLITE_DEPLOYMENT.md
   工具：SQLite + memos (版本控制)
   
4. 病理分析与风险评估
   文档：GENETIC_PATHOLOGY_GUIDE.md + PATHOLOGY_ANALYSIS_BEST_PRACTICES.md
   工具：PathologyFeatureExtractor + 多标志物分析引擎
   输出：病理分类、风险等级、靶点识别
   
5. 基因分析与科普
   文档：GENETIC_PATHOLOGY_GUIDE.md § 第一部分
   工具：GeneticFeatureExtractor + GeneticEducationModule
   输出：基因科普报告
   
6. 临床试验匹配
   文档：CLINICALTRIALS_API_GUIDE.md + GENETIC_PATHOLOGY_GUIDE.md § 第三部分
   工具：ClinicalTrials API + 智能匹配引擎
   输出：排序化试验推荐清单
   
7. 问诊清单生成
   文档：DEVELOPMENT_PLAN.md § 1.4
   工具：quickchart-mcp或echarts
   输出：结构化问诊清单（优先级+关键数据）
   
8. 综合报告生成
   文档：GENETIC_PATHOLOGY_GUIDE.md § 第四部分
   工具：小胰宝工具集成
   输出：患者可用的综合科普报告
```

### 持续监测流程（定期回访）

```
1. 新增数据导入
   触发：新病历/检查报告上传
   处理：增量识别(hash/mtime) → 版本记录
   存储：memos中追加新版本记录
   
2. 指标趋势分析
   文档：DEVELOPMENT_PLAN.md § 1.3.1 (CA19-9趋势图)
   触发：CA19-9等肿瘤标志物序列完整时
   生成：多标志物折线图 + 趋势解读
   
3. 多标志物同趋势分析
   文档：PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 一、二
   触发：同期内≥2个标志物异常时
   判断：肿瘤进展置信度评估
   行动：推荐治疗方案调整或检查
   
4. 月度摘要生成
   文档：DEVELOPMENT_PLAN.md § 1.6 (月度定义)
   输出：月度进展摘要 + 新增治疗/检查事件
   
5. 临床试验重新匹配
   触发：基因/病理数据更新或新试验纳入时
   处理：重新计算匹配分数，推荐新试验
```

---

## 🧬 关键模块详解

### 模块1：病理特征提取（PathologyFeatureExtractor）

**位置**：GENETIC_PATHOLOGY_GUIDE.md § 1.2
**核心类**：`PathologyFeatureExtractor`
**输入**：原始病理报告(JSON)
**输出**：
- cancer_type: 癌肿分类(WHO标准，10+种)
- differentiation_grade: 分化程度(I/II/III)
- marker_db: 49个免疫组化指标库
- multi_marker_analysis: 多标志物同趋势分析结果
- risk_stratification: 综合风险分层

**关键方法**：
1. `extract_pathology()` - 基础提取
2. `_analyze_multi_markers()` - 多标志物分析 (新增 v1.5)
3. `_stratify_risk()` - 风险分层算法 (新增 v1.5)

**支撑数据**：
- pathology_db: 胰腺肿瘤WHO分类(外分泌+内分泌+罕见)
- marker_db: 49个指标完整定义
- grade_db: 分化程度(I/II/III)

---

### 模块2：基因特征提取（GeneticFeatureExtractor）

**位置**：GENETIC_PATHOLOGY_GUIDE.md § 1.1
**核心类**：`GeneticFeatureExtractor`
**输入**：原始基因检测报告(NGS JSON)
**输出**：
- driver_genes: 驱动基因列表
- tumor_suppressor_genes: 抑癌基因列表
- treatment_targets: 治疗靶点集合
- risk_profile: 风险等级(高/中/低)

**支撑数据**：
- gene_db: KRAS、TP53等关键基因库

---

### 模块3：多标志物同趋势分析引擎

**位置**：PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 一
**核心方法**：`PathologyFeatureExtractor._analyze_multi_markers()`
**输入**：特殊标志物字典(CA19-9, CA50, CA125, CA72-4, CEA等)
**输出**：
```json
{
  "simultaneous_elevation": ["CA19-9", "CA50"],  // 同升高的指标
  "trend_interpretation": "CA19-9 + CA50同升高 → 肿瘤进展可能性↑↑",
  "clinical_recommendation": "与CA19-9单独升高相比，可靠性大幅提升..."
}
```

**关键规则**：
- CA19-9 + CA50 → 肿瘤进展 ⭐⭐⭐
- CA19-9 + CA125 → 腹膜转移 ⭐⭐⭐
- CA19-9 单独 + 其他正常 → 炎症反应 ⭐
- CA19-9 + CA50 + CA125 → 极高可信 ⭐⭐⭐⭐

---

### 模块4：综合风险分层算法

**位置**：PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 三
**核心方法**：`PathologyFeatureExtractor._stratify_risk()`
**计算维度**：
1. 病理类型基础分(50-100分)
2. 分化程度调整(0-30分)
3. 高危标志物累加(每项20-25分)

**输出**：
```json
{
  "level": "高危",              // 极高危/高危/中危/低危
  "score": 115,                 // 总分
  "factors": ["导管腺癌", "低分化程度", "S100P高表达"],
  "treatment_intensity": "积极治疗：标准化疗+靶向治疗"
}
```

**分级对应**：
- 极高危(≥130) → FOLFIRINOX + 靶向 + 免疫
- 高危(100-129) → 标准化疗 + 靶向治疗
- 中危(70-99) → 吉西他滨+顺铂或FOLFIRINOX
- 低危(<70) → 手术优先，必要时化疗

---

### 模块5：临床试验智能匹配

**位置**：GENETIC_PATHOLOGY_GUIDE.md § 第三部分 + CLINICALTRIALS_API_GUIDE.md
**核心函数**：`match_and_rank_trials(genetic_features, pathology_features)`
**三层匹配机制**：

1. **基础层**：病理类型
   ```
   pancreatic_ductal_adenocarcinoma 
   → 搜索 "pancreatic cancer" OR "adenocarcinoma"
   ```

2. **靶点层**：关键标志物
   ```
   claudin18+ → 加入 "claudin18" 
   HER2+ → 加入 "HER2"
   MSI-H → 加入 "MSI-H"
   KRAS G12C → 加入 "KRAS G12C"
   ```

3. **强化层**：基因+病理组合
   ```
   IF KRAS G12C AND claudin18+ 
   → 搜索 "KRAS G12C" AND "claudin18"
   ```

**排序优先级**：
1. 完全匹配(基因+病理+≥2个标志物)
2. 多标志物匹配(≥2个靶点)
3. 单靶点匹配
4. 肿瘤类型匹配

---

## 📊 数据模型映射

### JSON模式（JSON_STORAGE_GUIDE.md）

```
patient/
├── patient_master.json
│   ├── patient_id: hash(姓名+出生年份+医院+病例号)
│   ├── basic_info: {姓名,性别,年龄,诊断,TNM分期...}
│   ├── disease_timeline: [{date, event_type, description, source_file}]
│   └── version_history: [{version, timestamp, changes}]
│
├── genetic_report.json
│   ├── test_date, test_type(NGS/PCR)
│   ├── mutations: [{gene, mutation, classification, allele_frequency}]
│   ├── extracted_features: {driver_genes, tumor_suppressor_genes, treatment_targets}
│   └── version_v1, version_v2...
│
├── pathology_report.json
│   ├── test_date, specimen_id
│   ├── primary_pathology: "pancreatic_ductal_adenocarcinoma"
│   ├── differentiation_grade: "II"
│   ├── special_markers: {CA19-9: "positive", claudin18: "positive"...}
│   ├── extracted_features: {cancer_type, grade, risk_level, treatment_targets}
│   └── version_v1, version_v2...
│
└── tumor_markers.json
    ├── CA19-9: [{date, value, unit, imputed, confidence}]
    ├── CA50: [{date, value...}]
    ├── CA125: [{date, value...}]
    ├── CA72-4: [{date, value...}]
    └── trend_analysis: {simultaneous_elevation, interpretation, recommendation}
```

### SQLite表结构（SQLITE_DEPLOYMENT.md）

```sql
-- 文件索引表(去重+增量识别)
file_index(file_hash, file_path, file_size, mtime, status, error_msg)

-- 肿瘤标志物历史表(用于趋势图)
markers_history(patient_id, marker_type, date, value, source_file, imputed, confidence)

-- 处理日志表(审计追踪)
processing_log(patient_id, import_id, file_hash, step, status, error_msg)

-- 临床试验缓存表(避免重复查询)
clinical_trials_cache(patient_id, trial_id, match_score, match_reason, fetched_at)
```

---

## 🔌 系统集成点

### 集成1：Claude API子智能体调用

**位置**：DEVELOPMENT_PLAN.md § 2.2 + MCP_CONFIGURATION.md
**调用场景**：
1. 病情提取智能体 → 关键字段JSON
2. 病历整理智能体 → 病历结构化
3. 文件分类智能体 → 低置信度文件纠正

**MCP工具定义**：mcp.json中定义各智能体接口

---

### 集成2：ClinicalTrials.gov API

**位置**：CLINICALTRIALS_API_GUIDE.md
**查询示例**：
```
GET /api/v2/studies?
  query.cond=pancreatic cancer
  query.intr=claudin18
  query.status=RECRUITING
  pageSize=100
```

**缓存策略**：SQLite clinical_trials_cache表避免重复查询

---

### 集成3：小胰宝工具集成

**位置**：GENETIC_PATHOLOGY_GUIDE.md § 第四部分
**集成的资源**：
- 小胰宝公众号
- 小胰宝助手
- 小绿卡基因报告工具
- 小红卡应急卡片制作

---

## 📈 v1.5新增内容清单

### GENETIC_PATHOLOGY_GUIDE.md增强

✅ 胰腺肿瘤WHO完整分类(10+种类型)
- 外分泌：导管腺癌、浆液性囊腺癌、粘液性囊肿、IPMN、腺泡细胞癌
- 内分泌：NET G1/G2、小细胞癌
- 罕见：鳞癌、未分化癌、实性假乳头状

✅ 49个病理指标完整定义和分组
- 肿瘤标志物(CA19-9/CA50/CA125/CA72-4/CEA)
- 诊断指标(CK7/CK19/CK20/EMA等)
- 靶点标志物(claudin18/HER2/S100P)
- 预后相关(Ki-67/E-cadherin/IMP3/MUC1)
- 神经内分泌(SYN/Cg)

✅ 多标志物同趋势分析方法(CA19-9/CA50/CA125/CA72-4)
- 关键组合判断逻辑
- 假阳性排除规则
- 临床置信度分级

✅ 综合风险分层算法
- 病理类型基础分
- 分化程度调整
- 高危标志物累加
- 4级风险分层←→治疗强度对应

### PATHOLOGY_ANALYSIS_BEST_PRACTICES.md新增

✅ 完整的多标志物分析框架
✅ 病理分类决策树(SYN/Cg表达→进一步分类)
✅ 导管腺癌靶点识别决策树(claudin18→HER2→S100P→MSI)
✅ 特殊情景病理诊断(高危NET识别、囊肿恶变判断)
✅ 临床试验匹配三层机制
✅ 质量控制与异常处理规范

---

## 🎯 实现优先级建议

### Phase 1: 核心数据管理(已完成设计)
- [ ] SQLite数据库初始化脚本
- [ ] JSON模式验证器
- [ ] 文件扫描与分类模块

### Phase 2: 病理分析引擎(已完成设计)
- [ ] PathologyFeatureExtractor实现
- [ ] 多标志物分析引擎
- [ ] 风险分层算法
- [ ] 趋势图生成(quickchart-mcp)

### Phase 3: 基因分析与科普(已完成设计)
- [ ] GeneticFeatureExtractor实现
- [ ] 科普文本生成模块
- [ ] 教育模块集成

### Phase 4: 临床试验匹配(已完成设计)
- [ ] ClinicalTrials API集成
- [ ] 智能匹配与排序
- [ ] 试验缓存管理

### Phase 5: 综合报告与发布
- [ ] 综合报告生成
- [ ] 小胰宝工具集成
- [ ] 用户交互优化

---

## 📚 文档交叉引用

### 快速导航

| 查找内容 | 相关文档 |
|--------|---------|
| 病理分类 | GENETIC_PATHOLOGY_GUIDE.md § 1.2 pathology_db |
| 多标志物分析 | PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 一、四 |
| 风险评分 | PATHOLOGY_ANALYSIS_BEST_PRACTICES.md § 三.2 |
| 临床试验匹配 | CLINICALTRIALS_API_GUIDE.md + GENETIC_PATHOLOGY_GUIDE.md § 三 |
| 数据存储格式 | JSON_STORAGE_GUIDE.md + SQLITE_DEPLOYMENT.md |
| 肿瘤标志物趋势 | DEVELOPMENT_PLAN.md § 1.3.1 |
| 问诊清单 | DEVELOPMENT_PLAN.md § 1.4 |
| MCP配置 | mcp.json + MCP_CONFIGURATION.md |

---

## ✅ 验收清单

- [x] 完整的胰腺肿瘤病理分类(WHO标准, 10+种类型)
- [x] 49个病理指标详细定义
- [x] 多标志物同趋势分析框架
- [x] 综合风险分层算法(病理+分化+标志物)
- [x] 基因特征提取与科普教育
- [x] 临床试验三层智能匹配机制
- [x] 完整的工作流程文档
- [x] 数据模型设计(JSON + SQLite)
- [x] 质量控制与异常处理规范
- [x] 小胰宝工具集成方案

---

**文档管理**
- 主维护者：Skill开发团队
- 最后更新：2026-01-19
- 版本控制：基于memos系统(见JSON_STORAGE_GUIDE.md)
- 审核周期：月度

**后续工作**
1. 代码实现验证与测试
2. 临床医生评审与反馈
3. 试点患者数据验证
4. 性能优化与扩展
