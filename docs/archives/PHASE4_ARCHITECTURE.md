# Phase 4 架构设计文档：科普教育与医学可视化

**版本**: 1.0  
**日期**: 2026-01-19  
**状态**: 设计确认

---

## 核心原则：LLM + 智能体 + 结构化数据

### 设计理念

Phase 4遵循以下**核心架构原则**：

```
结构化病情数据 (来自Phase 1-3)
    ↓
[智能体 Agent]
    ├─ 系统提示词 (System Prompt)
    ├─ 用户提示词 (User Prompt - 包含数据)
    └─ Claude API调用
    ↓
患者友好的文本内容 (Markdown格式)
    ↓
[可选] 图表生成 (quickchart-mcp/echart)
    ↓
最终报告包
```

**关键点**：
- ❌ **不是**：硬编码词汇表 + 模板替换
- ✅ **是**：LLM智能生成 + 结构化提示词 + 灵活输出

---

## 一、两个专用智能体

### 1.1 PopularScienceAgent（科普教育智能体）

**职责**：将医学术语转换为患者友好的科普内容

**系统角色定义**：
```
医学科普专家
- 将复杂医学概念转化为患者易懂的语言
- 使用类比和比喻帮助理解
- 平衡现实和希望
```

**主要方法**：

| 方法 | 输入 | 输出 | 用途 |
|------|------|------|------|
| `generate_genetic_education()` | `genetic_features` (Dict) | Markdown文本 | 基因科普 |
| `generate_pathology_education()` | `pathology_features` (Dict) | Markdown文本 | 病理科普 |
| `generate_treatment_education()` | `treatment_history` (List) | Markdown文本 | 治疗科普 |
| `generate_prognosis_education()` | 风险+基因+病理 | Markdown文本 | 预后科普 |
| `generate_clinical_trial_education()` | `matched_trials` (List) | Markdown文本 | 试验科普 |
| `generate_patient_self_care()` | 风险+并发症 | Markdown文本 | 自我管理建议 |
| `generate_comprehensive_education_report()` | 所有病情数据 | 完整Markdown | 完整报告 |

**输出格式（Markdown）**：
```markdown
## 主标题
### 副标题
- 要点1
- 要点2

**强调内容**

> 引用或关键信息
```

**调用示例**：
```python
agent = PopularScienceAgent(api_key="...")

genetic_features = {
    'driver_genes': [{'gene': 'KRAS', 'mutation': 'G12C'}],
    'tumor_suppressor_genes': [{'gene': 'TP53'}],
    'actionable_mutations': ['KRAS-G12C'],
    'risk_profile': '高危'
}

# LLM调用 (内部)
# 系统提示词: "你是医学科普专家..."
# 用户提示词: f"请根据以下基因检测结果生成科普文本:\n{genetic_features}"
# 返回: 患者友好的科普内容

content = agent.generate_genetic_education(genetic_features)
```

---

### 1.2 VisualizationAgent（医学可视化智能体）

**职责**：设计患者友好的可视化内容

**系统角色定义**：
```
医学信息设计师
- 将复杂数据转化为清晰的可视化
- 使用emoji和符号帮助理解
- 强调关键信息，简化复杂内容
```

**主要方法**：

| 方法 | 输入 | 输出 | 用途 |
|------|------|------|------|
| `design_risk_profile_visualization()` | 风险等级 | Markdown可视化 | 风险展示 |
| `design_genetic_features_table()` | 基因特征 | Markdown表格 | 基因概览 |
| `design_treatment_timeline()` | 治疗历史 | ASCII/Markdown时间线 | 治疗时间表 |
| `design_marker_trend_narrative()` | 标志物数据 | Markdown叙述 | 趋势解释 |
| `design_patient_summary_card()` | 患者信息 | Markdown卡片 | 1页速览 |
| `design_consultation_checklist()` | 病情特征 | Markdown清单 | 问诊清单 |
| `design_complication_risk_table()` | 并发症列表 | Markdown表格 | 风险提示 |
| `generate_comprehensive_visualization_report()` | 所有病情数据 | 完整Markdown | 完整可视化报告 |

**输出格式（Markdown可视化）**：
```markdown
🔴 **高危** (风险等级)
│
├─ 🧬 驱动基因：2个
├─ 🎯 可靶向突变：1个
└─ ⚠️ 风险指示条：█████░░░░

| 基因 | 突变 | 优先级 |
|------|------|--------|
| KRAS | G12C | 高     |

[ ] 高优先级问题
[ ] 中优先级问题
```

---

## 二、输出格式规范

### 2.1 统一的Markdown格式

所有输出都使用**Markdown格式**，包含以下元素：

**标题层级**：
```
# 一级标题（不用，保留给最终报告总题）
## 二级标题（模块标题）
### 三级标题（小节标题）
```

**内容结构**：
```
## 模块名称

### 关键点总结
- 要点1
- 要点2

### 详细解释
段落文本说明...

**强调内容**

> 引用或关键信息

### 后续建议
- 建议1
- 建议2
```

**Emoji规范**：
```
📚 知识类
🔬 科学/医学
🏥 医疗
💊 药物/治疗
🧬 基因
📊 数据/统计
📈 上升趋势
📉 下降趋势
➡️ 稳定
🔴 高风险/重要
🟡 中风险/注意
🟢 低风险/良好
⭐ 重点推荐
✅ 完成/正常
❌ 问题/异常
⚠️ 警告
💡 建议
```

### 2.2 报告包结构

Phase 4输出完整的**报告包**（与Phase 2一致，加入科普层）：

```
_reports/
├── 病情报告_完整版_2024-06-20.md        # 医学专业版（已有）
├── 病情报告_患者科普版_2024-06-20.md    # 患者友好版（NEW - Phase 4）
├── 医学可视化报告_2024-06-20.md         # 可视化设计（NEW - Phase 4）
├── 问诊清单_2024-06-20.md               # 问诊要点（可视化增强）
├── 患者速览卡_2024-06-20.md             # 1页总结
├── 肿瘤标志物趋势_2024-06-20.html       # quickchart图表
└── index.md                             # 导航索引
```

---

## 三、完整工作流程

### 3.1 科普教育报告生成流程

```
【输入】结构化病情数据
├── genetic_features (GeneticFeatureExtractor输出)
├── pathology_features (PathologyFeatureExtractor输出)
├── marker_data (MarkerAnalyzer输出)
├── treatment_history (JSON)
├── matched_trials (ClinicalTrialMatcher输出)
└── risk_profile (RiskStratifier输出)
  ↓
【Step 1】基因科普
  Population ScienceAgent.generate_genetic_education(genetic_features)
  → LLM生成基因科普文本
  → 输出: ## 基因检测结果科普版
  
【Step 2】病理科普
  PopularScienceAgent.generate_pathology_education(pathology_features)
  → LLM生成病理科普文本
  → 输出: ## 病理检查结果科普版
  
【Step 3】治疗科普
  PopularScienceAgent.generate_treatment_education(treatment_history)
  → LLM生成治疗科普文本
  → 输出: ## 治疗方案科普版
  
【Step 4】预后科普
  PopularScienceAgent.generate_prognosis_education(...)
  → LLM生成预后科普文本
  → 输出: ## 预后评估科普版
  
【Step 5】临床试验科普
  PopularScienceAgent.generate_clinical_trial_education(matched_trials)
  → LLM生成试验科普文本
  → 输出: ## 临床试验机会科普版
  
【Step 6】自我管理建议
  PopularScienceAgent.generate_patient_self_care(...)
  → LLM生成自我管理建议
  → 输出: ## 患者自我管理建议
  ↓
【输出】病情报告_患者科普版_YYYY-MM-DD.md
```

### 3.2 医学可视化报告生成流程

```
【输入】结构化病情数据（同上）
  ↓
【Step 1】患者速览卡
  VisualizationAgent.design_patient_summary_card(patient_data)
  → 生成1页患者信息卡
  → 输出: 患者病情速览卡
  
【Step 2】风险等级可视化
  VisualizationAgent.design_risk_profile_visualization(risk_profile)
  → 生成风险指示条和emoji视觉
  → 输出: 风险等级评估
  
【Step 3】基因特征表格
  VisualizationAgent.design_genetic_features_table(genetic_features)
  → 生成基因突变表格
  → 输出: 基因特征矩阵
  
【Step 4】治疗时间线
  VisualizationAgent.design_treatment_timeline(treatment_history)
  → 生成治疗时间线ASCII图
  → 输出: 治疗时间线
  
【Step 5】标志物趋势叙述
  VisualizationAgent.design_marker_trend_narrative(marker_data)
  → 生成趋势文字解释
  → 输出: 肿瘤标志物趋势分析
  
【Step 6】问诊清单
  VisualizationAgent.design_consultation_checklist(...)
  → 生成结构化问诊清单
  → 输出: 医生问诊清单
  
【Step 7】并发症风险表
  VisualizationAgent.design_complication_risk_table(complications)
  → 生成并发症风险表格
  → 输出: 并发症风险评估
  ↓
【输出】医学可视化报告_YYYY-MM-DD.md
```

---

## 四、关键设计决策

### 4.1 为什么是LLM驱动而不是硬编码？

| 方案 | 优点 | 缺点 | 选择 |
|------|------|------|------|
| **硬编码词汇表** | 快速、可控 | 不灵活、内容单调、难以维护 | ❌ |
| **LLM驱动** | 灵活、个性化、易维护 | 需要API、成本考量 | ✅ |

### 4.2 智能体与LLM的角色分工

```
智能体 (Agent)
├─ 角色定义 (System Prompt)
│  └─ "你是医学科普专家..."
├─ 任务设计 (User Prompt)
│  └─ "根据以下数据生成科普..."
├─ 数据传输
│  └─ 结构化的JSON数据
└─ 结果处理
   └─ Markdown格式的文本

LLM (Claude)
├─ 理解任务
├─ 根据系统提示词采用合适的语气和风格
├─ 根据数据生成内容
└─ 返回结构化的Markdown文本
```

### 4.3 为什么分为两个智能体？

- **PopularScienceAgent**：专注于**内容生成**
  - 系统提示词强调"医学科普专家"
  - 输出：纯文本科普内容
  - 调用6次（6个部分）

- **VisualizationAgent**：专注于**视觉设计**
  - 系统提示词强调"医学信息设计师"
  - 输出：包含emoji、表格、图示的可视化
  - 调用7次（7个可视化部分）

---

## 五、输出质量标准

### 5.1 科普教育报告质量检查

✅ 患者可以理解（避免过度医学术语）  
✅ 结构清晰（标题、要点、详细）  
✅ 平衡现实和希望（既不隐瞒也不过度悲观）  
✅ 可操作（提供具体建议）  
✅ 包含emoji增强视觉  

### 5.2 可视化报告质量检查

✅ 清晰易读（一目了然）  
✅ 信息准确（数据与source一致）  
✅ 视觉层级清晰（emoji、颜色、排版）  
✅ 包含必要的上下文（为什么这很重要）  
✅ 支持快速浏览  

---

## 六、与其他Phase的集成

### 6.1 数据流

```
Phase 1: 文件扫描 + JSON存储
    ↓
Phase 2: 病理+标志物+风险分层
    ↓
Phase 3: 基因提取 + 试验匹配
    ↓
Phase 4: 科普教育 + 医学可视化 ← 智能体处理
    ↓
Phase 5: 最终报告展示 + Web UI
```

### 6.2 兼容性

- ✅ PopularScienceAgent输出与Phase 2病情报告兼容
- ✅ VisualizationAgent输出与quickchart-mcp集成
- ✅ 所有输出都是Markdown格式，可用于Phase 5 Web UI

---

## 七、注意事项

### 7.1 成本考虑

- 每次生成完整报告调用**13次API**（6+7）
- 估计token使用：~3000-5000 tokens/报告
- 建议：实现缓存机制，相同数据不重复调用

### 7.2 错误处理

- LLM可能生成不准确的信息
- 需要在报告中明确标注"请咨询医生验证"
- 建议：增加人工审核步骤

### 7.3 隐私保护

- 智能体接收的是脱敏数据（patient_id而非真实姓名）
- 输出也应该脱敏处理
- 遵循Phase 2的隐私流程

---

**下一步**：Phase 5 将用Web UI展示这些报告
