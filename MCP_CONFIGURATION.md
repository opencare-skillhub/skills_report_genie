# MCP配置指南

## 概览

本Skill集成了7个MCP服务器，用于支持病情整理、临床知识检索、图表生成、长期记忆等功能。所有MCP服务已在`mcp.json`中完整配置。

---

## MCP服务器清单

### 1. Quickchart-MCP-Server (SSE)
**用途**：生成肿瘤标志物趋势图

**配置**：
```json
{
  "type": "sse",
  "url": "https://mcp-api.tencent-cloud.com/sse/d20f0f73a45f1bc6"
}
```

**功能**：
- 支持多序列折线图（CA19-9/CA50/CA125/CA72-4）
- 生成PNG图片，直接嵌入报告
- 支持参考线、数据点标记、图例等定制

**调用示例**：
```python
# 在report_generator.py中
response = call_mcp("Quickchart-MCP-Server", {
    "type": "line",
    "data": {
        "labels": ["术前", "C1", "C2", ...],
        "datasets": [...]
    },
    "options": {...}
})
# 返回PNG图片，保存至 questions/images/肿瘤标志物趋势图.png
```

---

### 2. metaso (HTTP API)
**用途**：知识补充搜索和RAG

**配置**：
```json
{
  "url": "https://metaso.cn/api/mcp",
  "headers": {
    "Authorization": "Bearer mk-8477E39D1CE97AAB3432EED9306E02F2"
  }
}
```

**功能**：
- RAG方式搜索补充临床常识
- 回答患者常见问题
- 补充治疗方案背景信息

**使用场景**：
- 生成问诊清单时补充医学背景知识
- 解释并发症风险时的知识补充
- 治疗方案选择的临床依据

---

### 3. pubmed-data-server (Node.js本地进程)
**用途**：PubMed文献检索和全文获取（胰腺癌定制）

**配置**：
```json
{
  "command": "node",
  "args": ["/Users/qinxiaoqiang/Downloads/mcp-pubmed-server-pancrpal/src/index.js"],
  "cwd": "/Users/qinxiaoqiang/Downloads/mcp-pubmed-server-pancrpal",
  "env": {
    "PUBMED_API_KEY": "9c1f5cb4ff62971cf4b383e944913da50808",
    "PUBMED_EMAIL": "qinxiaoqiang@gmail.com",
    "ABSTRACT_MODE": "deep",
    "FULLTEXT_MODE": "enabled"
  }
}
```

**功能**：
- 基于基因、病理类型检索相关文献
- 深度摘要模式（提取关键研究成果）
- 全文获取和链接提供
- 胰腺癌专门优化

**使用场景**：
- 临床知识增强阶段
- 基于患者基因检测结果推荐文献
- 最新治疗方案和临床试验查询

**调用示例**：
```python
# 在clinical_enhancer.py中
papers = call_mcp("pubmed-data-server", {
    "query": "KRAS G12D pancreatic cancer treatment",
    "max_results": 5
})
# 返回：[{title, abstract_summary, pmid, url}, ...]
```

---

### 4. mcp-pubmed-llm-server (NPX命令)
**用途**：PubMed文献的LLM智能处理和总结

**配置**：
```json
{
  "command": "npx",
  "args": ["mcp-pubmed-llm-server"]
}
```

**功能**：
- 对PubMed全文进行智能摘要
- 提取关键研究发现
- 评估临床适用性

**使用场景**：
- 处理pubmed-data-server返回的全文
- 生成可读的文献总结
- 评估研究质量和相关性

---

### 5. memos-api-mcp (NPX命令)
**用途**：患者长期记忆存储

**配置**：
```json
{
  "command": "npx",
  "args": ["-y", "@memtensor/memos-api-mcp@latest"],
  "env": {
    "MEMOS_API_KEY": "pg-XTF8X0lKOJVUpewkyvdL1GwR1T7MebYrgzJ3zhWo",
    "MEMOS_CHANNEL": "MEMOS",
    "MEMOS_USER_ID": "sam.qin@xiaoyibao.com.cn"
  }
}
```

**功能**：
- 存储患者基本长期记忆（病理、基因、诊断）
- 版本控制（时间戳+来源）
- 跨会话持久化

**存储内容示例**：
```json
{
  "patient_id": "hash_xxx",
  "memory_type": "genetics",
  "content": {
    "mutations": ["KRAS G12D", "TP53"],
    "test_date": "2023-02-01",
    "confidence": "high"
  },
  "version": 1,
  "timestamp": "2024-01-15T10:30:00Z",
  "source": "基因检测报告_2023-02-01.pdf"
}
```

**使用场景**：
- 初诊后第一次信息提取时保存基本信息
- 复诊更新时检查版本变化
- 多患者管理时的身份区分

**调用示例**：
```python
# 在data_manager.py中
save_to_memos({
    "patient_id": patient_id,
    "memory_type": "pathology",
    "content": pathology_data,
    "version": 1,
    "source": source_file
})
```

---

### 6. clinical-trials (NPX命令 - xiaoyibao API)
**用途**：临床试验检索（小胰宝社区）

**配置**：
```json
{
  "command": "npx",
  "args": ["-y", "xiaoyibao-clinical-trials"]
}
```

**功能**：
- 基于癌肿类型、分期、基因检索临床试验
- 返回纳入排斥标准
- 小胰宝社区链接

**搜索参数示例**：
```python
{
  "cancer_type": "pancreatic_cancer",
  "stage": "IIIB",
  "mutations": ["KRAS", "TP53"],
  "region": "China",
  "max_results": 10
}
```

**返回数据示例**：
```json
{
  "trial_id": "NCT0XXXXXXX",
  "title": "KRAS G12C Inhibitor in Advanced Pancreatic Cancer",
  "phase": "II",
  "status": "recruiting",
  "inclusion": "KRAS G12C mutant, Stage III-IV",
  "exclusion": "Prior KRAS inhibitor therapy",
  "site_url": "https://xiaoyibao.com.cn/trials/..."
}
```

**使用场景**：
- 临床知识增强第一步
- 根据患者基因/分期推荐相关试验
- 生成临床建议报告

---

### 7. searxng-simple-mcp (UVX命令)
**用途**：网页搜索（最新指南和资讯）

**配置**：
```json
{
  "command": "uvx",
  "args": [
    "--from", "iflow-mcp_searxng-simple-mcp",
    "searxng-simple-mcp"
  ]
}
```

**功能**：
- 实时网页搜索
- 获取最新临床指南
- 权威医疗资源搜索

**使用场景**：
- 补充非PubMed的临床信息
- 获取最新治疗指南（NCCN、ESMO等）
- 患者教育资源搜索

---

## 集成工作流

### 初诊流程中的MCP调用

```
【第1步】文件扫描分类 → 无MCP调用

【第2步】信息提取 → 无MCP调用（本地处理）

【第3步】长期记忆存储
  → memos-api-mcp: 保存患者基本信息

【第4步】报告生成
  a) 结构化病情报告
     → Quickchart-MCP: 生成肿瘤标志物折线图
     → metaso: 补充临床常识（可选）
  
  b) 问诊清单
     → metaso: 医学背景知识补充
  
  c) 并发症风险预警
     → metaso: 补充并发症知识

【第5步】临床知识增强（可选，需授权）
  1. clinical-trials: 搜索相关临床试验
  2. pubmed-data-server: 搜索最新文献
  3. mcp-pubmed-llm-server: 文献智能总结
  4. searxng-simple-mcp: 补充最新指南
  5. metaso: 知识背景补充
  → 输出：临床增强报告
```

### 复诊更新流程中的MCP调用

```
【增量识别】→ 无MCP调用

【信息提取】→ 无MCP调用

【报告更新】
  → memos-api-mcp: 检查版本，更新长期记忆
  → Quickchart-MCP: 重新生成更新的趋势图
  → metaso: 补充新的临床背景（可选）

【临床知识更新】
  → clinical-trials: 刷新试验列表
  → pubmed-data-server: 检索最新文献
```

---

## 环境变量管理

### 需要维护的关键环境变量

| 变量 | 来源 | 维护周期 | 备注 |
|------|------|--------|------|
| MEMOS_API_KEY | memos系统 | 手动更新 | 定期验证有效性 |
| metaso Bearer Token | metaso控制台 | 手动更新 | 需要申请新token时重新配置 |
| PUBMED_API_KEY | NCBI官网 | 年度 | 需要有效邮箱 |
| PUBMED_EMAIL | 用户邮箱 | 手动 | 与PUBMED_API_KEY配对 |
| clinical-trials API Key | xiaoyibao | 手动 | 如需要的话 |

### 安全建议
1. **不要提交敏感信息**：将mcp.json添加到.gitignore（如有版本控制）
2. **定期轮换API密钥**：按平台规定周期更新
3. **监控API使用量**：防止配额超限
4. **日志脱敏**：不记录API密钥在日志中

---

## 故障排除

### MCP服务不可用时的降级方案

| 服务 | 降级方案 | 影响范围 |
|------|--------|--------|
| Quickchart-MCP | 本地matplotlib生成图表 | 图表质量降低，仍可生成 |
| metaso | 跳过知识补充 | 报告内容略简化 |
| pubmed-data-server | 跳过文献检索 | 跳过临床知识增强，报告仍完整 |
| memos-api-mcp | 本地JSON存储 | 无跨会话长期记忆，仍可工作 |
| clinical-trials | 跳过试验推荐 | 临床建议不完整 |

### 常见问题

**Q1: mcp.json中的API密钥过期了怎么办？**
A: 需要获取新的密钥并更新mcp.json中对应的环境变量。建议建立更新日志。

**Q2: Quickchart生成失败会影响报告吗？**
A: 不会。系统会自动降级到本地matplotlib生成，用户不会感知。

**Q3: 如何测试MCP连接？**
A: 在Claude中直接尝试调用该工具，观察返回结果。官方MCP也会给出诊断信息。

**Q4: 多个患者共用这些MCP服务吗？**
A: 是的。注意使用patient_id进行隔离，防止数据混淆。

---

## 维护清单

- [ ] 每月检查API密钥有效性
- [ ] 每季度更新PubMed搜索索引
- [ ] 定期验证临床试验数据库最新性
- [ ] 监控MCP服务可用性和响应时间
- [ ] 备份关键API密钥（安全存储）

---

**最后更新**：2026-01-19
**维护人**：开发团队
