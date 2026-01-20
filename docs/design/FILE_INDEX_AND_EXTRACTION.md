# 文件索引与增量提取设计

**版本**: v2.1  
**更新**: 2026-01-20  
**核心改进**: 路径日志替代原始文件副本，支持增量处理和去重

---

## 一、目录结构优化

```
patient_case/
├── _metadata/
│   ├── patient_master.json           # 主病情（增量维护）
│   ├── file_index.json               # ★文件索引日志
│   ├── processing_status.json        # 增量处理标记
│   └── extraction_log.json           # 处理记录
│
├── extracted/                        # 所有提取的JSON
│   ├── report_20260120.json
│   ├── ct_image_20260115.json
│   ├── blood_test_20260110.json
│   └── ...
│
└── [医疗诊疗/影像/检查 等11个目录]
    ├── report.pdf (原文件，仅1份)
    ├── ct_image.jpg
    └── ...
```

**改进点**：
- ✅ 原始文件无重复（一份保存）
- ✅ 路径通过file_index.json记录
- ✅ 提取结果保存在extracted/（按时间戳标注）
- ✅ 支持增量处理（hash+mtime跟踪）

---

## 二、file_index.json 结构

### 核心设计

```json
{
  "schema_version": 2.1,
  "patient_id": "hash_xxx",
  "last_updated": "2026-01-20T10:30:00Z",
  
  "files": [
    {
      "file_id": "file_001",
      "original_path": "/Users/user/Downloads/病历/report.pdf",
      "relative_path": "医疗诊疗/病历/report.pdf",
      "filename": "report.pdf",
      "file_type": "pdf",
      "file_size": 2048576,
      
      "hash": "sha256_abc123def456...",
      "mtime": "2026-01-15T09:30:00Z",
      
      "extraction": {
        "extracted_json": "extracted/report_20260120.json",
        "extraction_method": "Pandoc",
        "extraction_time": "2026-01-20T10:30:00Z",
        "status": "success",
        "confidence": 0.95
      },
      
      "classification": {
        "category": "medical_records",
        "subcategory": "pathology",
        "confidence": 0.92
      },
      
      "import": {
        "import_id": "import_001",
        "import_time": "2026-01-20T10:30:00Z",
        "source": "user_upload"
      },
      
      "deduplication": {
        "is_duplicate": false,
        "duplicate_of": null,
        "notes": ""
      }
    }
  ],
  
  "deduplication_log": [
    {
      "kept": "file_001",
      "removed": ["file_002"],
      "hash": "sha256_abc123def456...",
      "reason": "identical_content",
      "detection_time": "2026-01-20T10:30:00Z"
    }
  ],
  
  "statistics": {
    "total_files": 50,
    "unique_files": 48,
    "duplicates_removed": 2,
    "extraction_success": 46,
    "extraction_failed": 2,
    "last_import_id": "import_001"
  }
}
```

---

## 三、提取流程 + JSON保存

### 单个文件的完整流程

```
原始文件
  ↓ [hash计算 + 去重检测]
新增/变更? (mtime/hash对比)
  ├─ No  → 跳过（增量优化）
  └─ Yes ↓
  
[内容提取] (Pandoc/pymupdf-4o/pypdf/OCR)
  ↓
extracted/{filename}_{timestamp}.json
  ├─ raw_text: 完整提取文本
  ├─ metadata: 文件元数据
  ├─ confidence: 提取置信度
  └─ ...
  
  ↓ [关键词提取 + 结构化]
  
[病情关键信息]
  ├─ 病理诊断
  ├─ 肿瘤标志物值
  ├─ TNM分期
  ├─ 基因突变
  └─ ...
  
  ↓ [增量合并]
  
patient_master.json (更新)
  ├─ 病理数据 (新增/更新)
  ├─ 肿瘤标志物历史 (追加)
  ├─ 版本时间戳
  └─ ...
```

### extracted/ 中的JSON结构

```json
{
  "file_id": "file_001",
  "filename": "report.pdf",
  "extraction_time": "2026-01-20T10:30:00Z",
  "extraction_method": "Pandoc",
  
  "raw_text": "完整的文本提取结果...",
  "text_length": 5432,
  
  "confidence": 0.95,
  "language": "zh",
  
  "metadata": {
    "report_date": "2026-01-15",
    "report_type": "病理报告",
    "patient_name": "***",
    "hospital": "医院名称"
  },
  
  "extracted_fields": {
    "diagnosis": "胰腺导管腺癌，中分化",
    "pathology_grade": "G2",
    "immune_markers": ["CK19+", "CA19-9+"],
    "tnm_stage": "T3N1M0",
    "genetic_mutations": ["KRAS+", "TP53+"]
  }
}
```

---

## 四、增量处理机制

### processing_status.json

```json
{
  "last_full_import": "2026-01-15T10:30:00Z",
  "last_incremental_import": "2026-01-20T10:30:00Z",
  
  "file_tracking": {
    "file_001": {
      "last_processed": "2026-01-20T10:30:00Z",
      "hash": "sha256_abc123...",
      "mtime": "2026-01-15T09:30:00Z",
      "status": "processed"
    },
    "file_002": {
      "last_processed": "2026-01-20T10:30:00Z",
      "hash": "sha256_def456...",
      "mtime": "2026-01-18T14:00:00Z",
      "status": "processed"
    }
  },
  
  "pending_files": [],
  
  "failed_files": [
    {
      "file_id": "file_999",
      "filename": "corrupted.pdf",
      "error": "PDF parse error",
      "retry_count": 1,
      "next_retry": "2026-01-21T10:30:00Z"
    }
  ]
}
```

### 增量检测逻辑

```python
def should_process_file(file_path, file_id, current_hash, current_mtime):
    """判断是否需要处理文件"""
    
    # 1. 新文件 (file_id不在index中)
    if file_id not in file_index:
        return True
    
    # 2. 内容变更 (hash不同)
    if current_hash != file_index[file_id]['hash']:
        return True
    
    # 3. 元数据变更 (mtime较晚)
    if current_mtime > file_index[file_id]['mtime']:
        return True
    
    # 4. 已处理过，跳过
    return False
```

---

## 五、patient_master.json 增量更新

### 原则

```
每次新增/更新文件 → 自动扫描extracted/ → 提取关键信息 → 合并入patient_master
```

### 示例：添加肿瘤标志物

```json
{
  "tumor_markers": {
    "last_updated": "2026-01-20T10:30:00Z",
    "sources": [
      {
        "date": "2026-01-20",
        "file_id": "file_003",
        "extraction_source": "blood_test_20260120.json"
      }
    ],
    "history": [
      {
        "date": "2026-01-20",
        "ca19_9": 245.5,
        "ca50": 128.0,
        "ca125": 35.8,
        "ca72_4": 12.1,
        "source_file": "file_003"
      }
    ]
  }
}
```

---

## 六、关键信息自动提取规则

### 正则表达式 + LLM混合

| 数据类型 | 提取方法 | 优先级 |
|---------|--------|------|
| 肿瘤标志物值 | 正则 `CA19-9[:\s]*(\d+\.?\d*)` | 1️⃣ |
| 诊断结论 | LLM (从结构化JSON) | 1️⃣ |
| TNM分期 | 正则 `(T[0-4]N[0-3]M[01])` | 1️⃣ |
| 基因突变 | 正则 `(KRAS\|TP53\|BRCA)` | 1️⃣ |
| 治疗方案 | LLM (文本分析) | 2️⃣ |
| 医院名称 | 正则 `医院名称` | 3️⃣ |

---

## 七、实施步骤

### Phase 1: 核心模块 (已完成)
- ✅ ContentExtractor (文件解析)
- ✅ Pandoc/pymupdf-4o集成
- ✅ 单文件JSON保存

### Phase 2: 文件索引 (待开发)
- [ ] FileIndexer 模块
  - hash计算 + 去重检测
  - file_index.json维护
  - processing_status.json更新
  
- [ ] IncrementalProcessor 模块
  - mtime/hash对比
  - 只处理变更文件
  - 失败重试机制

### Phase 3: 数据合并 (待开发)
- [ ] StructuredDataMerger 模块
  - 关键信息提取 (正则+LLM)
  - patient_master增量更新
  - 版本控制

---

## 八、优势对比

### 旧方案（复制原始文件）
```
病历目录/
├── report.pdf (原件)
├── report.pdf (副本1)
├── report.pdf (副本2)  ← 重复浪费
└── report.json
```
❌ 存储浪费、去重困难、来源不清

### 新方案（路径日志）
```
_metadata/
├── file_index.json  ← 记录所有路径
├── patient_master.json
└── processing_status.json

extracted/
├── report_20260120.json
├── report_20260115.json  ← 版本历史
└── ...
```
✅ 节省存储、自动去重、完整追踪、支持增量

---

## 九、配置说明

### requirements.txt 新增

```
pymupdf4llm>=0.2.0       # 最佳PDF提取
pandoc-python>=1.0       # Pandoc调用（需系统安装pandoc）
pypdf>=3.17              # 备选PDF提取
python-dotenv>=1.0       # .env加载
```

### 环境变量

```bash
# .env中新增
EXTRACTION_METHOD=pandoc         # 优先使用pandoc
INCREMENTAL_PROCESSING=true      # 启用增量处理
DEDUPLICATION_ENABLED=true       # 启用去重
HASH_ALGORITHM=sha256            # hash算法
```

---

**下一步**: 开发 `src/processing/file_indexer.py` 和 `src/processing/incremental_processor.py`
