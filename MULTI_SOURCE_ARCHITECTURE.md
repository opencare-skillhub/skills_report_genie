# 多信息源架构设计文档

**文档版本**: 1.0  
**最后更新**: 2026-01-19  
**适用范围**: Skill Report Genie 信息聚合与检索系统

---

## 一、整体架构

### 1.1 三层信息源体系

Skill支持从**三个层级**的信息源进行智能查询和聚合分析：

```
┌────────────────────────────────────────────────────────────────┐
│                        用户查询                                  │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────┐
    │  智能路由 & 多源聚合分析器   │
    │  (MultiSourceAnalyzer)      │
    │                             │
    │  • 问题分类                 │
    │  • 来源选择                 │
    │  • 并行查询                 │
    │  • 结果融合                 │
    │  • 冲突检测                 │
    └──┬──────────────┬──────────┬─┘
       │              │          │
       ▼              ▼          ▼
    ┌─────────────┐ ┌────────────────┐ ┌──────────────┐
    │  第1层      │ │    第2层       │ │    第3层     │
    │ 专业API     │ │ 小胰宝RAG      │ │  LLM+MCP     │
    │ 和爬虫      │ │ (社区知识库)   │ │ (动态检索)   │
    └──┬──────────┘ └────────┬───────┘ └──────┬───────┘
       │                     │                │
       ├─ 临床试验API       ├─ 基因知识      ├─ PubMed LLM
       │  clinicaltrials     │ 病理知识      │ (pubmed_llm_mcp)
       │                     │ 治疗方案      │
       ├─ 中国临床注册中心   │ 预后信息      ├─ Metaso搜索
       │  (chiCTR)          │               │ (metaso_web_search)
       │                     │               │
       └─ 其他医学API        │ • 实时性强    ├─ MCP集成
          (可扩展)           │ • 患者导向    │ (医学文献)
                             │ • 多维度     │
                             │              └─ 可扩展
                             │
                             └─ 高可靠性
                               结构化数据
```

### 1.2 三层特点对比

| 特性 | 第1层 API | 第2层 RAG | 第3层 LLM+MCP |
|------|---------|----------|-------------|
| **数据源** | 官方标准 | 社区知识 | 海量文献 |
| **实时性** | 中等 | 实时 | 非常实时 |
| **结构化** | 高 | 中等 | 低 |
| **权威性** | 很高 | 中等 | 中等 |
| **覆盖度** | 针对性强 | 中等 | 非常广泛 |
| **人力需求** | 低 | 中 | 高 |
| **响应时间** | 较快 | 较快 | 较慢 |
| **成本** | 可能付费 | 免费 | 取决于MCP |

---

## 二、第1层：专业API与爬虫

### 2.1 临床试验API (Clinical Trials)

**服务**: ClinicalTrials.gov API  
**功能**: 美国FDA批准的临床试验数据  
**覆盖**: 全球临床试验 (优先国际多中心)  
**特点**: 数据最权威、更新最快

```python
# 使用示例
from src.integration.clinical_trials_api import ClinicalTrialsAPIClient

client = ClinicalTrialsAPIClient()

# 查询KRAS-G12C试验
trials = client.search(
    condition="pancreatic cancer",
    keyword="KRAS G12C",
    status="RECRUITING",
    phase=["Phase 2", "Phase 3"]
)
```

**优先级**: ⭐⭐⭐⭐⭐ (最高)  
**推荐用途**: 国际临床试验、标准治疗方案

### 2.2 中国临床试验注册中心 (ChiCTR)

**服务**: 中国国内临床试验注册平台  
**网站**: https://www.chictr.org.cn/  
**功能**: 中国国内临床试验检索  
**覆盖**: 中国境内临床试验

```python
# 使用示例
from src.integration.chictr_client import ChiCTRClient

client = ChiCTRClient()

# 查询KRAS相关胰腺癌试验
trials = client.search_genetic_mutation(
    gene_name="KRAS",
    mutation="G12C"
)

# 搜索胰腺癌化疗试验
trials = client.search_cancer_trials(
    cancer_type="胰腺癌",
    treatment="化疗",
    phase="II期"
)
```

**优先级**: ⭐⭐⭐⭐ (高)  
**推荐用途**: 中国国内患者、本土临床方案

### 2.3 其他医学API (预留)

- PubMed API (医学文献摘要)
- DrugBank API (药物信息)
- 其他医学数据库

---

## 三、第2层：小胰宝RAG

### 3.1 核心能力

**服务**: 小胰宝社区助手RAG  
**基础**: 集成pubmed_llm_mcp和metaso  
**数据源**:
- 社区患者数据
- 临床医生经验
- 医学文献(通过pubmed_llm_mcp)
- 互联网信息(通过metaso)

### 3.2 优势

```
✅ 实时性强        - 接入最新社区信息
✅ 患者导向        - 基于真实患者经历
✅ 多维度知识      - 整合医学、患者、社区视角
✅ 灵活性高        - 支持复杂自然语言查询
✅ 上下文感知      - 理解患者具体情况
✅ 完全免费        - 无额外成本
```

### 3.3 查询示例

```python
from src.integration.rag_client import XiaoyibaoRAGClient

rag = XiaoyibaoRAGClient(api_key="xxx")

# 查询基因相关信息
response = rag.query_genetic_info(
    gene_name="KRAS",
    mutation="G12C"
)

# 查询治疗方案
response = rag.query_treatment_options(
    cancer_type="导管腺癌",
    genetic_features=["KRAS-G12C"],
    pathology_features=["claudin18+"]
)

# 查询预后
response = rag.query_prognosis(
    cancer_type="导管腺癌",
    risk_factors=["Ki-67高", "E-cadherin丧失"]
)
```

**优先级**: ⭐⭐⭐⭐ (高)  
**推荐用途**: 患者教育、治疗咨询、预后评估

---

## 四、第3层：LLM + MCP

### 4.1 PubMed LLM检索

**能力**: 通过LLM进行PubMed医学文献检索  
**来源**: pubmed_llm_mcp集成  
**用途**: 最新医学研究、循证医学数据

```python
# 概念示例（实现由MCP提供）
pubmed_results = mcp_pubmed_search(
    query="KRAS G12C pancreatic cancer treatment",
    max_results=10,
    date_filter="2024"
)

# 使用LLM总结文献
summary = llm_summarize_literature(pubmed_results)
```

### 4.2 Metaso网络搜索

**能力**: 通过LLM进行智能网络搜索  
**来源**: metaso_web_search集成  
**用途**: 最新信息、实时数据、新闻报道

```python
# 概念示例
web_results = metaso_search(
    query="KRAS G12C新药临床结果2025",
    domain="health|medical"
)

# 提取关键信息
key_findings = llm_extract_key_info(web_results)
```

### 4.3 MCP集成

**能力**: 通过MCP协议接入多个信息源  
**优势**:
- 标准化接口
- 可扩展性强
- 安全和可控

**优先级**: ⭐⭐⭐ (中)  
**推荐用途**: 前沿研究、实时资讯、补充信息

---

## 五、多源聚合分析

### 5.1 查询流程

```
用户查询
  ↓
[问题分类]
  ├─ 基因特异性 → API + RAG + LLM
  ├─ 病理特异性 → RAG + LLM
  ├─ 治疗方案   → API + RAG + LLM
  └─ 预后评估   → RAG + LLM
  ↓
[并行查询多源]
  ├─ API查询 (毫秒)
  ├─ RAG查询 (秒)
  └─ LLM查询 (秒)
  ↓
[结果融合]
  ├─ 一致性分析
  ├─ 冲突检测
  └─ 置信度评估
  ↓
[推荐答案生成]
  ├─ 优先级排序
  ├─ 来源标注
  └─ 替代观点保留
```

### 5.2 智能路由规则

```python
# 基因查询优先顺序
GENETIC_QUERY_PRIORITY = [
    ("clinical_trials_api", 0.9),  # 官方API最权威
    ("chictr", 0.85),              # 中国试验中心
    ("xiaoyibao_rag", 0.8),        # 社区知识
    ("pubmed_llm", 0.7),           # 医学文献
    ("metaso", 0.6)                # 网络搜索
]

# 病理查询优先顺序
PATHOLOGY_QUERY_PRIORITY = [
    ("xiaoyibao_rag", 0.9),        # RAG有专业知识
    ("pubmed_llm", 0.8),           # 文献支持
    ("metaso", 0.7)                # 网络资源
]

# 治疗方案优先顺序
TREATMENT_QUERY_PRIORITY = [
    ("clinical_trials_api", 0.95), # 试验数据最权威
    ("chictr", 0.90),              # 国内方案
    ("xiaoyibao_rag", 0.85),       # 实践经验
    ("pubmed_llm", 0.80),          # 指南和文献
    ("metaso", 0.70)               # 补充信息
]
```

### 5.3 一致性和冲突处理

```
情况                        处理方式                    来源标注
════════════════════════════════════════════════════════════════════
多源一致                    合并呈现 + 强调共识          显示所有参与源

API高置信 + RAG低置信       优先API                    注明RAG有不同观点
  (罕见情况)

RAG高置信 + LLM不确定       保留RAG + 注明LLM补充       清晰标注置信度

三源全部不同               保留所有观点 + 分析原因      每个观点标注来源

信息过时                   优先新来源 + 时间戳         标注信息时间
  (API数据旧 vs 网络新)
```

---

## 六、实现细节

### 6.1 MultiSourceAnalyzer增强

```python
from src.integration.multi_source_analyzer import MultiSourceAnalyzer

class EnhancedMultiSourceAnalyzer(MultiSourceAnalyzer):
    """
    增强版多源分析器
    支持三层信息源
    """
    
    def analyze_query(
        self,
        query_text: str,
        query_type: str,  # "genetic", "pathology", "treatment", "prognosis"
        sources: Optional[List[str]] = None,
        include_all_sources: bool = False
    ) -> MultiSourceResult:
        """
        多源分析查询
        
        Args:
            query_text: 查询文本
            query_type: 查询类型
            sources: 指定来源 (自动选择或完全指定)
            include_all_sources: 是否包含所有可用来源
        
        Returns:
            聚合分析结果
        """
        
        # 自动选择来源
        if sources is None:
            sources = self._select_sources_for_query_type(query_type)
        
        # 并行查询多源
        results = self._query_all_sources(query_text, sources)
        
        # 聚合和分析
        aggregated = self._aggregate_results(results, query_type)
        
        return aggregated
```

### 6.2 配置示例

```python
# config.py

# API配置
CLINICAL_TRIALS_API_CONFIG = {
    "base_url": "https://clinicaltrials.gov/api/v2",
    "enabled": True,
    "timeout": 30
}

CHICTR_CONFIG = {
    "base_url": "https://www.chictr.org.cn",
    "enabled": True,
    "timeout": 30
}

# RAG配置
XIAOYIBAO_RAG_CONFIG = {
    "api_key": os.getenv("XIAOYIBAO_API_KEY"),
    "base_url": "https://admin.xiaoyibao.com.cn/v1",
    "enabled": True,
    "timeout": 30
}

# LLM+MCP配置
LLM_MCP_CONFIG = {
    "pubmed_llm": {
        "enabled": True,
        "timeout": 60
    },
    "metaso_search": {
        "enabled": True,
        "timeout": 30
    }
}

# 查询优先级
QUERY_PRIORITY = {
    "genetic": [
        "clinical_trials_api",
        "chictr",
        "xiaoyibao_rag",
        "pubmed_llm",
        "metaso"
    ],
    "pathology": [
        "xiaoyibao_rag",
        "pubmed_llm",
        "metaso"
    ],
    "treatment": [
        "clinical_trials_api",
        "chictr",
        "xiaoyibao_rag",
        "pubmed_llm",
        "metaso"
    ],
    "prognosis": [
        "xiaoyibao_rag",
        "pubmed_llm",
        "metaso"
    ]
}
```

---

## 七、信息来源使用场景

### 场景1: 基因靶向治疗咨询

```
Q: "KRAS G12C突变胰腺癌的最新靶向治疗方案是什么？"

推荐来源顺序:
1️⃣ Clinical Trials API
   └─ 获取最新G12C试验(sotorasib, adagrasib等)

2️⃣ chiCTR
   └─ 中国国内相关G12C试验

3️⃣ 小胰宝RAG
   └─ 患者/医生对这些药物的真实体验

4️⃣ PubMed LLM
   └─ 最新研究数据和对比分析

5️⃣ Metaso
   └─ 2024-2025年最新新闻和指南更新

融合结论:
✅ 一线推荐: sotorasib/adagrasib
✅ 联合: 标准化疗或FOLFIRINOX
⚠️ 中国患者注意: 可查chiCTR了解国内临床试验可用性
💡 患者体验: 根据RAG社区信息提供真实预期
```

### 场景2: 病理诊断咨询

```
Q: "claudin18+ HER2+ 导管腺癌如何分类和治疗？"

推荐来源顺序:
1️⃣ 小胰宝RAG
   └─ 多维度临床知识(诊断、分类、治疗)

2️⃣ PubMed LLM
   └─ 文献支持的诊断标准

3️⃣ Metaso
   └─ 补充新指南和建议

Clinical Trials API用途少（因为试验通常选一个靶点）

融合结论:
✅ 诊断: 导管腺癌，两个高价值靶点
✅ 靶点优先级: claudin18>HER2（胰腺癌中claudin18特异性更高）
✅ 治疗: 考虑双靶点或顺序靶向
💡 患者教育: 用RAG提供的患者友好语言
```

### 场景3: 预后评估

```
Q: "极高危胰腺导管腺癌(多个驱动基因+高Ki-67)的预后是？"

推荐来源:
1️⃣ 小胰宝RAG
   └─ 真实患者预后数据和生存期

2️⃣ PubMed LLM
   └─ 文献中的生存数据

3️⃣ Metaso
   └─ 最新预后研究

API不太相关(试验数据不代表预后)

融合结论:
📊 中位生存期: 6-12月(化疗)
💊 新方案可能延长至12-18月
⚠️ 个体化: 基于具体分子特征预测
```

---

## 八、最佳实践

### 8.1 查询优化

```python
# ❌ 不推荐：过于宽泛
analyzer.analyze_query("胰腺癌治疗", "treatment")

# ✅ 推荐：具体详细
analyzer.analyze_query(
    "导管腺癌伴KRAS-G12C和claudin18+的精准治疗方案",
    "treatment"
)
```

### 8.2 来源优先级动态调整

```python
# 根据用户背景调整优先级

# 国际患者
user_location = "USA"
sources = ["clinical_trials_api", "pubmed_llm", "xiaoyibao_rag", "metaso"]

# 中国患者
user_location = "China"
sources = ["chictr", "clinical_trials_api", "xiaoyibao_rag", "pubmed_llm", "metaso"]

# 医疗专业人士
user_role = "doctor"
sources = ["clinical_trials_api", "pubmed_llm", "chictr", "xiaoyibao_rag"]

# 患者教育
user_role = "patient"
sources = ["xiaoyibao_rag", "metaso", "pubmed_llm"]
```

### 8.3 缓存策略

```python
# 不同来源缓存时间不同

CACHE_TTL = {
    "clinical_trials_api": 3600,      # 1小时(数据变化快)
    "chictr": 3600,                   # 1小时
    "xiaoyibao_rag": 86400,           # 24小时(稳定)
    "pubmed_llm": 86400 * 7,          # 7天(论文更新慢)
    "metaso": 3600                    # 1小时(网络信息更新快)
}
```

---

## 九、故障转移

当某个来源不可用时：

```
如果 Clinical Trials API 不可用
  → 自动降级到 chiCTR + xiaoyibao_rag
  → 提示用户可能信息不完整

如果 chiCTR 不可用
  → 继续使用 Clinical Trials API
  → 提示中国患者可能缺少国内试验信息

如果 xiaoyibao_rag 不可用
  → 使用 pubmed_llm + metaso 替代
  → 但缺少社区实际体验

如果 PubMed LLM 不可用
  → 使用 metaso 进行网络搜索
  → 提示可能缺少学术支持

如果所有来源不可用
  → 使用本地数据库信息
  → 提示用户稍后重试
```

---

## 十、扩展计划

### v1.1 (近期)
- [ ] Clinical Trials API正式集成
- [ ] chiCTR爬虫完善
- [ ] 缓存系统实现
- [ ] 故障转移自动化

### v1.2 (中期)
- [ ] PubMed LLM集成
- [ ] Metaso搜索集成
- [ ] 更精细的聚合算法
- [ ] 用户偏好学习

### v2.0 (长期)
- [ ] 多语言支持
- [ ] 知识图谱应用
- [ ] 实时更新订阅
- [ ] AI医生推理引擎

---

**维护责任**: 信息架构团队  
**更新频率**: 每月或功能更新时  
**反馈渠道**: GitHub Issues / 项目讨论
