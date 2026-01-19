# 小胰宝RAG信息源集成指南

**文档版本**: 1.0  
**最后更新**: 2026-01-19  
**适用范围**: Skill Report Genie 多源信息聚合模块

---

## 一、概述

本指南说明如何在Skill中集成小胰宝社区助手的RAG（检索增强生成）能力，进行多维度临床知识查询。

### 核心目标
- 🔗 整合多个信息源 (LLM + RAG + MCP + 本地DB)
- 📊 智能聚合分析，处理信息冲突
- 📍 完整的信息来源标注
- 🎯 提供推荐答案和替代观点

---

## 二、架构设计

### 2.1 信息源架构

```
┌─────────────────────────────────────────────────────────────┐
│                    用户查询                                   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────┐
    │   MultiSourceAnalyzer          │ (多源聚合分析器)
    │                                │
    │  1. 路由查询到多个源            │
    │  2. 并行/序列查询              │
    │  3. 分析一致性                 │
    │  4. 生成推荐答案               │
    └────┬───────────────┬───────────┘
         │               │
    ┌────▼──┐    ┌──────▼──────┐
    │ 小胰宝 │    │  本地数据库  │
    │  RAG  │    │  (Phase 1-3) │
    │       │    │              │
    │ API   │    │ PathologyDB  │
    │调用   │    │ GeneticDB    │
    └───────┘    │ TrialDB      │
                 └──────────────┘

其他信息源 (预留):
├── LLM (Claude/GPT)
├── MCP (Model Context Protocol)
└── 医学文献库
```

### 2.2 查询流程

```
用户查询
  ↓
问题分类 (基因/病理/治疗/预后)
  ↓
信息源选择
  ├─ 基因相关 → xiaoyibao_rag + local genetic_db
  ├─ 病理相关 → xiaoyibao_rag + local pathology_db
  ├─ 治疗相关 → xiaoyibao_rag + local treatment_db
  └─ 预后相关 → xiaoyibao_rag
  ↓
并行查询多源
  ├─ RAG查询 (5-10秒)
  ├─ 本地DB查询 (毫秒)
  └─ 融合结果
  ↓
一致性分析
  ├─ 识别共识
  ├─ 检测冲突
  └─ 置信度评估
  ↓
生成推荐答案
  ├─ 多源一致 → 合并答案
  ├─ 部分冲突 → 标注差异
  └─ 重大分歧 → 保留所有观点
  ↓
信息来源标注
  ├─ 明确来源
  ├─ 置信度说明
  └─ 引用文献
```

---

## 三、使用指南

### 3.1 基本使用

#### 3.1.1 初始化

```python
from src.integration.rag_client import create_xiaoyibao_rag_client

# 创建RAG客户端
api_key = "openapi-b417lLW6VhNdTog5PTWiNuSdhuvplEdn3GKQShXRLV2ZbLdHRLdO"
rag_client = create_xiaoyibao_rag_client(api_key)
```

#### 3.1.2 单源查询

```python
# 查询基因相关信息
response = rag_client.query_genetic_info(
    gene_name="KRAS",
    mutation="G12C"
)
print(response.content)
print(f"相关性: {response.relevance_score:.0%}")
print(f"置信度: {'高' if response.is_confident else '低'}")
```

#### 3.1.3 多源查询

```python
from src.integration.rag_client import create_multi_source_analyzer

# 创建多源分析器
analyzer = create_multi_source_analyzer(api_key)

# 分析查询
result = analyzer.analyze_query(
    query_text="KRAS G12C突变胰腺癌的治疗方案",
    sources=["xiaoyibao_rag", "local_db"],
    include_local_knowledge=True
)

# 输出结果
print(analyzer.format_result(result))
```

---

### 3.2 具体应用场景

#### 场景1: 基因特征咨询

```python
# 病人: KRAS-G12C + TP53-R175H

# 多源查询
result = analyzer.analyze_query(
    "KRAS G12C和TP53 R175H同时存在时的治疗策略是什么？"
)

# 预期输出:
# 推荐答案: [综合多源最佳答案]
# 信息来源:
#   • 小胰宝RAG (置信度: 高)
#   • 本地知识库 (置信度: 高)
# ✅ 共识: 两个信息源对KRAS-G12C靶向治疗的推荐一致
# ⚠️ 不同观点: (如果有)
#   - 关于TP53处理的策略存在差异
```

#### 场景2: 病理标志物分析

```python
# 病人: claudin18+ + HER2+ + Ki-67 high

result = analyzer.analyze_query(
    "claudin18+ 和 HER2+ 同时阳性的胰腺导管腺癌如何治疗？"
)

# 预期输出:
# - 推荐答案: [多靶点联合治疗方案]
# - 来源: 小胰宝RAG + 本地病理数据库
# - 标注: 两个claudin18靶向药物的疗效对比
```

#### 场景3: 预后评估

```python
# 查询预后信息
result = analyzer.analyze_query(
    query_text="极高危胰腺导管腺癌的预后和生存期预测",
    sources=["xiaoyibao_rag"],
    include_local_knowledge=False
)

# 专注于RAG提供的最新临床数据
```

---

## 四、信息源说明

### 4.1 小胰宝RAG优势

| 特性 | 说明 |
|------|------|
| **实时性** | 接入社区最新病例和临床经验 |
| **患者导向** | 基于真实患者数据和治疗结果 |
| **多维度** | 整合医学、患者、社区多层面知识 |
| **灵活性** | 支持复杂问题和个性化查询 |
| **上下文感知** | 理解患者具体情况的微妙差异 |

### 4.2 本地数据库优势

| 特性 | 说明 |
|------|------|
| **结构化** | 高质量结构化数据 |
| **可控性** | 完全可控，无网络依赖 |
| **一致性** | 与本地分析模块无缝集成 |
| **快速** | 毫秒级响应时间 |
| **精准** | 准确的标准临床数据 |

### 4.3 信息融合策略

```
情况                        处理方式
════════════════════════════════════════════════════════
多源一致                    合并呈现，强调共识
  (RAG和本地DB都高置信)     

RAG高置信，本地低置信      优先RAG，但标注本地差异

本地高置信，RAG低置信      优先本地，但注明RAG观点

重大分歧                   两个都保留，明确标注
  (置信度都高但内容矛盾)    差异和可能原因

缺失信息                   说明数据不足，建议补充
```

---

## 五、API规范

### 5.1 XiaoyibaoRAGClient

#### 核心方法

```python
# 通用查询
query(query_text: str, chat_id: str = "default") -> RAGResponse

# 专用查询方法
query_genetic_info(gene_name: str, mutation: str) -> RAGResponse
query_pathology_info(pathology_type: str, marker: Optional[str]) -> RAGResponse
query_treatment_options(cancer_type: str, genetic_features: List[str], 
                       pathology_features: List[str]) -> RAGResponse
query_clinical_trials(cancer_type: str, genetic_mutations: List[str],
                     biomarkers: List[str]) -> RAGResponse
query_prognosis(cancer_type: str, risk_factors: List[str]) -> RAGResponse
```

#### 响应格式

```python
@dataclass
class RAGResponse:
    content: str                # 回复内容
    relevance_score: float      # 相关性评分 (0-1)
    source: str                 # 信息来源 ("xiaoyibao_rag")
    references: List[str]       # 引用来源列表
    is_confident: bool          # 是否高置信 (≥0.7)
```

### 5.2 MultiSourceAnalyzer

#### 核心方法

```python
# 多源分析
analyze_query(
    query_text: str,
    sources: Optional[List[str]] = None,  # ["xiaoyibao_rag", "local_db"]
    include_local_knowledge: bool = True
) -> MultiSourceResult

# 格式化输出
format_result(result: MultiSourceResult) -> str
```

#### 响应格式

```python
@dataclass
class MultiSourceResult:
    query: str                          # 原始查询
    results: List[RAGResponse]          # 各源的回复列表
    consensus: Optional[str]            # 共识（如有）
    conflicts: List[Dict]               # 冲突项（如有）
    recommended_answer: str             # 推荐答案
    source_attribution: Dict[str, str]  # 信息来源标注
```

---

## 六、集成到Skill

### 6.1 在分析流程中添加RAG查询

```python
# 在 src/analysis/genetic_extractor.py 中

from src.integration.rag_client import create_multi_source_analyzer

class GeneticAnalysisWithRAG:
    def __init__(self, rag_api_key: str):
        self.analyzer = create_multi_source_analyzer(rag_api_key)
        self.extractor = GeneticFeatureExtractor()
    
    def analyze_with_rag(self, genetic_report: Dict):
        """使用RAG增强的基因分析"""
        
        # 第1步: 本地特征提取
        features = self.extractor.extract_mutations(genetic_report)
        
        # 第2步: RAG查询补充信息
        for driver_gene in features.driver_genes:
            gene = driver_gene["gene"]
            mutation = driver_gene["mutation"]
            
            # 查询RAG获取最新治疗方案
            result = self.analyzer.analyze_query(
                f"{gene} {mutation} 胰腺癌最新治疗方案"
            )
            
            # 增强本地结果
            driver_gene["rag_enhanced_info"] = result.recommended_answer
            driver_gene["source_attribution"] = result.source_attribution
        
        return features
```

### 6.2 在病情互动分析中使用

```python
# 在Skill的交互流程中

class ClinicalInteractionEngine:
    def __init__(self, rag_api_key: str):
        self.analyzer = create_multi_source_analyzer(rag_api_key)
    
    def respond_to_patient_query(self, question: str, patient_context: Dict):
        """响应患者查询"""
        
        # 分析问题类型
        query_type = self._classify_query(question)
        
        if query_type in ["genetic", "pathology", "treatment", "prognosis"]:
            # 使用多源分析
            result = self.analyzer.analyze_query(
                question,
                sources=self._select_sources(query_type),
                include_local_knowledge=True
            )
            
            # 返回格式化答案
            return self.analyzer.format_result(result)
        else:
            # 其他问题使用常规LLM
            return llm_response(question)
```

---

## 七、配置说明

### 7.1 环境变量

```bash
# .env 文件
XIAOYIBAO_API_KEY=openapi-b417lLW6VhNdTog5PTWiNuSdhuvplEdn3GKQShXRLV2ZbLdHRLdO
XIAOYIBAO_BASE_URL=https://admin.xiaoyibao.com.cn/v1
```

### 7.2 Python配置

```python
# config.py
import os

XIAOYIBAO_CONFIG = {
    "api_key": os.getenv("XIAOYIBAO_API_KEY"),
    "base_url": os.getenv("XIAOYIBAO_BASE_URL", "https://admin.xiaoyibao.com.cn/v1"),
    "timeout": 30,  # 查询超时（秒）
    "enable_caching": True,  # 启用缓存
    "cache_ttl": 3600  # 缓存有效期（秒）
}
```

---

## 八、最佳实践

### 8.1 查询优化

```python
# ❌ 不推荐：过于宽泛
analyzer.analyze_query("胰腺癌治疗")

# ✅ 推荐：具体详细
analyzer.analyze_query(
    "导管腺癌伴KRAS-G12C和TP53-R248Q突变、claudin18+、Ki-67 >30% 的综合治疗方案"
)
```

### 8.2 错误处理

```python
try:
    result = analyzer.analyze_query(query_text)
except requests.exceptions.Timeout:
    logger.error("RAG查询超时，使用本地数据库")
    result = analyzer.analyze_query(
        query_text,
        sources=["local_db"]  # 降级到本地
    )
except Exception as e:
    logger.error(f"查询失败: {e}")
    # 返回备选答案或提示用户
```

### 8.3 信息来源权重

```python
# 根据场景调整信息源权重

# 场景A: 最新治疗方案 → 优先RAG
sources = ["xiaoyibao_rag", "local_db"]

# 场景B: 诊断标准 → 优先本地DB
sources = ["local_db", "xiaoyibao_rag"]

# 场景C: 预后评估 → 均衡
sources = ["xiaoyibao_rag", "local_db"]
```

---

## 九、故障排查

### 问题1: RAG连接失败

```
症状: 无法连接小胰宝API
解决:
1. 检查 API Key 是否正确
2. 检查 base_url 是否可访问
3. 检查网络连接
4. 降级到本地数据库查询
```

### 问题2: 信息冲突过多

```
症状: 多个信息源给出矛盾答案
解决:
1. 检查置信度评分 - 优先高置信度源
2. 检查查询的具体性 - 更详细的查询可能减少冲突
3. 检查信息源更新时间 - 优先最新信息
4. 必要时保留所有观点，让用户自行判断
```

### 问题3: 查询响应慢

```
症状: RAG查询超过30秒
解决:
1. 简化查询文本 - 去掉不必要的细节
2. 增加超时时间: timeout=60
3. 只查询RAG，不查询本地DB
4. 启用缓存机制
```

---

## 十、版本规划

### v1.0 (当前)
- ✅ 小胰宝RAG集成
- ✅ 多源聚合分析
- ✅ 基本的一致性检测

### v1.1 (计划)
- [ ] 缓存机制
- [ ] 批量查询优化
- [ ] 更精细的置信度评估
- [ ] 情感分析（区分医学信息和患者体验）

### v2.0 (计划)
- [ ] MCP支持
- [ ] LLM联动
- [ ] 医学文献集成
- [ ] 知识图谱应用

---

## 附录A: 查询示例

### A.1 基因突变查询

```
Q: "KRAS G12C突变的最新治疗方案"

预期回复:
推荐答案:
  KRAS-G12C是可靠的治疗靶点。当前推荐方案:
  1. 一线: sotorasib (KRAS抑制剂)
  2. 备选: adagrasib (另一种KRAS-G12C抑制剂)
  3. 联合: + 标准化疗 (吉西他滨+顺铂或FOLFIRINOX)
  4. 后续: 联合免疫检查点抑制剂
  
信息来源:
  • 小胰宝RAG (置信度: 高)
  • 本地基因数据库 (置信度: 高)
  
✅ 共识: 两个信息源都推荐sotorasib作为一线治疗
```

### A.2 病理标志物查询

```
Q: "claudin18+ 胰腺导管腺癌的靶向治疗"

预期回复:
推荐答案:
  claudin18是胰腺导管腺癌的特异标志物，约80%患者表达。推荐:
  1. 一线: anetumab ravtansine (claudin18.2靶向抗体)
  2. 联合: + 标准化疗
  3. 监测: 定期评估疗效和不良反应
  
信息来源:
  • 小胰宝RAG (置信度: 高)
  • 本地病理标志物数据库 (置信度: 高)
  
✅ 共识: 一致推荐claudin18靶向治疗
```

### A.3 复杂临床场景

```
Q: "导管腺癌伴KRAS-G12C+claudin18+的综合治疗方案"

预期回复:
推荐答案:
  这是典型的高价值患者（可以受益于多个靶向治疗）。推荐方案:
  1. 基础: FOLFIRINOX (标准化疗)
  2. 靶向1: sotorasib (KRAS-G12C)
  3. 靶向2: anetumab ravtansine (claudin18+)
  4. 免疫: 根据MSI状态考虑加PD-1抑制剂
  
信息来源:
  • 小胰宝RAG (置信度: 高) - 最新临床实践
  • 本地知识库 (置信度: 高) - 标准化推荐
  
⚠️ 不同观点:
  - 关于三药联合的毒性管理策略存在差异
    本地推荐: 先行FOLFIRINOX + sotorasib
    RAG建议: 可考虑更激进的三药联合
  
💡 建议: 建立多学科讨论(MDT)制定个性化方案
```

---

**文档维护**
- 版本管理: git history
- 更新频率: 与代码同步更新
- 贡献流程: PR审核后更新

