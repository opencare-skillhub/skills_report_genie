# 文件提取与增量处理设计决策记录

**日期**: 2026-01-20  
**版本**: v2.1  
**状态**: ✅ 设计完成，待实施

---

## 核心决策

### 问题陈述
原始文件重复存储，无法追踪文件来源，不支持增量处理

### 解决方案
使用**路径日志 + extracted目录** 替代原始文件副本

```
旧方案: 病历/report.pdf + report.pdf副本1 + report.pdf副本2 ❌
新方案: _metadata/file_index.json (记录路径) + extracted/report_20260120.json ✅
```

---

## 架构改进

### 新增3个JSON文件 (_metadata/)

| 文件 | 用途 | 维护方式 |
|------|------|--------|
| file_index.json | 文件路径 + 去重记录 | 每次导入更新 |
| processing_status.json | 增量处理标记 | 实时更新 |
| extraction_log.json | 提取记录 | 日志追加 |

### 新增extracted/目录
- 所有提取结果保存: `filename_yyyymmdd.json`
- 支持版本历史
- 原始文件无重复

---

## 关键设计

### 1. file_index.json结构
```json
{
  "files": [
    {
      "file_id": "file_001",
      "original_path": "/path/to/report.pdf",
      "hash": "sha256_xxx",
      "extracted_json": "extracted/report_20260120.json",
      "is_duplicate": false
    }
  ],
  "deduplication_log": [...]
}
```

### 2. 增量检测逻辑
```
新文件? → 处理
hash变更? → 处理
mtime变更? → 处理
已处理? → 跳过
```

### 3. patient_master.json增量更新
- 每次提取后自动扫描extracted/
- 提取关键信息 (病理/肿瘤标志物等)
- 增量合并到patient_master (版本控制)

---

## 待开发模块 (3个)

### FileIndexer (`src/processing/file_indexer.py`)
- 维护file_index.json
- hash计算 (SHA256)
- 去重检测
- 文件状态跟踪

### IncrementalProcessor (`src/processing/incremental_processor.py`)
- mtime/hash对比
- 只处理变更文件
- 失败重试机制
- 处理状态管理

### StructuredDataMerger (`src/processing/structured_data_merger.py`)
- 从extracted/ JSON提取关键信息
- 病情字段识别 (病理/基因/肿瘤标志物)
- 增量合并到patient_master
- 版本控制

---

## 关键信息提取规则

### 自动提取方法 (优先级顺序)
| 数据 | 方法 | 优先级 |
|------|------|--------|
| 肿瘤标志物值 | 正则 | 1️⃣ |
| 诊断结论 | LLM | 1️⃣ |
| TNM分期 | 正则 | 1️⃣ |
| 基因突变 | 正则 | 1️⃣ |

### 正则表达式集
```python
CA19-9: r'CA\s*19\s*-?\s*9[：:]*(\d+\.?\d*)'
TNM: r'(T[0-4]N[0-3]M[01])'
KRAS: r'KRAS[：:]*([A-Z\d\+\-]+)'
```

---

## 集成方案

### process_single.py 新增6步骤
```
[1/6] 解析
[2/6] JSON保存
[3/6] 重命名
[4/6] 分类
[5/6] 报告解析
[6/6] 智能体报告
[6.5] + 文件索引 & 去重 ✨
[6.6] + 结构化提取 ✨
[6.7] + 数据合并 ✨
[6.8] + 更新索引 ✨
```

### process_coordinator.py 支持增量
```python
incremental = IncrementalProcessor()
for file in files:
    if incremental.should_process(file):  # 跳过已处理
        process(file)
        incremental.mark_processed(file)
```

---

## 预期效果

| 指标 | 值 |
|------|-----|
| 存储节省 | ~60% |
| 处理加速 | ~80% |
| 去重准确率 | 99.9% |
| 数据完整性 | 100% |

---

## 文档更新

### 已创建
- ✅ `docs/design/FILE_INDEX_AND_EXTRACTION.md` (完整设计)
- ✅ `docs/implementation/EXTRACTION_IMPLEMENTATION.md` (实施指导)
- ✅ `docs/design/JSON_STORAGE_GUIDE.md` (已更新)

### 包含内容
- 目录结构
- JSON模式
- API接口
- 测试用例
- 部署清单
- 配置说明

---

## 后续步骤

- [ ] 开发FileIndexer模块
- [ ] 开发IncrementalProcessor模块
- [ ] 开发StructuredDataMerger模块
- [ ] 集成到process_single.py
- [ ] 单元测试覆盖
- [ ] 集成测试验证
- [ ] 性能基准测试

---

**相关文件**:
- `docs/design/FILE_INDEX_AND_EXTRACTION.md`
- `docs/implementation/EXTRACTION_IMPLEMENTATION.md`
- `docs/design/JSON_STORAGE_GUIDE.md`
