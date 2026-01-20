# 文件提取与增量处理 - 实施指导

**版本**: v2.1  
**日期**: 2026-01-20  
**负责**: 开发团队

---

## 一、核心流程（快速概览）

```
原始文件输入
  ↓
[1] ContentExtractor
    ├─ Pandoc (本地)
    ├─ pymupdf-4o (本地)
    ├─ pypdf (本地)
    └─ OCR (本地)
  ↓
extracted/{filename}_{timestamp}.json
  ↓
[2] StructuredDataMerger
    ├─ 关键词提取 (正则+LLM)
    ├─ 病情字段识别
    └─ 数据标准化
  ↓
[3] IncrementalProcessor
    ├─ hash计算 + 去重
    ├─ mtime对比 + 变更检测
    ├─ 增量合并到patient_master.json
    └─ file_index.json更新
  ↓
patient_master.json (更新)
```

---

## 二、待开发模块

### 2.1 FileIndexer（文件索引器）

**位置**: `src/processing/file_indexer.py`

**核心功能**:
- ✅ 维护file_index.json
- ✅ hash计算（SHA256）
- ✅ 去重检测
- ✅ 路径记录

**接口**:
```python
class FileIndexer:
    def add_file(self, file_path: str, file_id: str) -> FileRecord
    def is_duplicate(self, hash: str) -> bool
    def mark_extracted(self, file_id: str, extracted_json: str)
    def get_by_hash(self, hash: str) -> Optional[FileRecord]
    def update_processing_status(self, file_id: str, status: str)
    def save_index(self) -> None
```

### 2.2 IncrementalProcessor（增量处理器）

**位置**: `src/processing/incremental_processor.py`

**核心功能**:
- ✅ mtime/hash对比
- ✅ 只处理变更文件
- ✅ 失败重试机制
- ✅ 处理状态跟踪

**接口**:
```python
class IncrementalProcessor:
    def should_process(self, file_id: str, current_hash: str, 
                      current_mtime: datetime) -> bool
    def mark_processed(self, file_id: str, status: str, error: str = None)
    def get_pending_files(self) -> List[str]
    def retry_failed_files(self, max_retries: int = 3)
    def save_status(self) -> None
```

### 2.3 StructuredDataMerger（结构化数据合并器）

**位置**: `src/processing/structured_data_merger.py`

**核心功能**:
- ✅ 从extracted/ JSON提取关键信息
- ✅ 病情字段识别（病理/肿瘤标志物/基因等）
- ✅ 增量合并到patient_master.json
- ✅ 版本控制和历史追踪

**接口**:
```python
class StructuredDataMerger:
    def extract_key_fields(self, extracted_json: dict) -> dict
    def merge_to_master(self, extracted_json: dict, 
                       file_id: str, file_type: str) -> None
    def update_patient_master(self) -> None
    def get_version_history(self, field: str) -> List[dict]
```

---

## 三、集成到现有流程

### 3.1 修改 process_single.py

在现有6步流程基础上添加：

```python
# 步骤6.5：新增 - 文件索引 + 去重
file_indexer = FileIndexer(work_dir)
if not file_indexer.is_duplicate(file_hash):
    file_indexer.add_file(image_path, file_id)
else:
    logger.warning(f"重复文件: {image_path}")
    return {"status": "duplicate", "kept_file_id": file_indexer.get_by_hash(file_hash)['file_id']}

# 步骤6.6：新增 - 增量提取
extractor = ContentExtractor()
result = extractor.extract(image_path)

# 保存extracted JSON
extracted_json_path = f"extracted/{file_id}_{timestamp}.json"
save_extracted_json(result, extracted_json_path)

# 步骤6.7：新增 - 结构化合并
merger = StructuredDataMerger(work_dir)
merger.merge_to_master(result.raw_data, file_id, result.file_type)

# 步骤6.8：新增 - 更新索引
file_indexer.mark_extracted(file_id, extracted_json_path)
file_indexer.save_index()
```

### 3.2 修改 process_coordinator.py

添加增量检测：

```python
def run_full_pipeline(self) -> dict:
    """执行完整处理流程（支持增量）"""
    
    # 初始化增量处理器
    incremental = IncrementalProcessor(self.input_dir)
    
    # 获取待处理文件
    files_to_process = []
    for file_path in scan_files(self.input_dir):
        file_id = generate_file_id(file_path)
        file_hash = calculate_hash(file_path)
        file_mtime = get_mtime(file_path)
        
        if incremental.should_process(file_id, file_hash, file_mtime):
            files_to_process.append(file_path)
    
    logger.info(f"发现 {len(files_to_process)} 个新增/变更文件")
    
    # 处理文件
    for file_path in files_to_process:
        try:
            result = process_single_image(file_path, self.input_dir)
            incremental.mark_processed(file_id, "success")
        except Exception as e:
            incremental.mark_processed(file_id, "failed", str(e))
    
    # 更新状态
    incremental.save_status()
```

---

## 四、关键信息提取规则

### 4.1 病理报告

```python
PATHOLOGY_PATTERNS = {
    'diagnosis': r'诊断[：:]\s*([^,\n]+)',
    'grade': r'分[化]?(G\d|[低中高])',
    'stage': r'(T[0-4]N[0-3]M[01])',
    'immune_markers': r'(CK\d+|CA\d+|HER\d+)[：:]*(\+|-)',
}
```

### 4.2 检验报告

```python
LAB_PATTERNS = {
    'ca19_9': r'CA\s*19\s*-?\s*9[：:]*(\d+\.?\d*)',
    'ca50': r'CA\s*50[：:]*(\d+\.?\d*)',
    'ca125': r'CA\s*125[：:]*(\d+\.?\d*)',
    'cea': r'CEA[：:]*(\d+\.?\d*)',
}
```

### 4.3 遗传/基因

```python
GENETIC_PATTERNS = {
    'kras': r'KRAS[：:]*([A-Z\d\+\-]+)',
    'tp53': r'TP53[：:]*([A-Z\d\+\-]+)',
    'brca': r'BRCA[1-2][：:]*([A-Z\d\+\-]+)',
}
```

---

## 五、测试用例

### 5.1 FileIndexer测试

```python
def test_file_indexer():
    indexer = FileIndexer('/tmp/test')
    
    # 测试：添加文件
    record = indexer.add_file('/path/to/file.pdf', 'file_001')
    assert record.file_id == 'file_001'
    
    # 测试：去重检测
    assert indexer.is_duplicate(record.hash) == False
    assert indexer.is_duplicate('other_hash') == False
    
    # 测试：mark_extracted
    indexer.mark_extracted('file_001', 'extracted/file_20260120.json')
    
    # 测试：save
    indexer.save_index()
    assert os.path.exists('_metadata/file_index.json')
```

### 5.2 IncrementalProcessor测试

```python
def test_incremental_processor():
    processor = IncrementalProcessor('/tmp/test')
    
    # 测试：新文件应该处理
    assert processor.should_process('file_001', 'hash1', datetime.now()) == True
    
    # 测试：标记为已处理后不应该处理
    processor.mark_processed('file_001', 'success')
    assert processor.should_process('file_001', 'hash1', datetime.now()) == False
    
    # 测试：mtime变更应该处理
    new_mtime = datetime.now() + timedelta(hours=1)
    assert processor.should_process('file_001', 'hash1', new_mtime) == True
```

### 5.3 StructuredDataMerger测试

```python
def test_merger():
    merger = StructuredDataMerger('/tmp/test')
    
    # 准备测试数据
    extracted = {
        'diagnosis': '胰腺导管腺癌',
        'ca19_9': 245.5,
        'report_date': '2026-01-20'
    }
    
    # 提取字段
    fields = merger.extract_key_fields(extracted)
    assert fields['diagnosis'] == '胰腺导管腺癌'
    assert fields['tumor_markers']['ca19_9'] == 245.5
    
    # 合并到主文件
    merger.merge_to_master(extracted, 'file_001', 'pathology')
    merger.update_patient_master()
    
    # 验证更新
    assert 'file_001' in master_json['pathology']['sources']
```

---

## 六、部署清单

- [ ] 创建 `src/processing/file_indexer.py`
- [ ] 创建 `src/processing/incremental_processor.py`
- [ ] 创建 `src/processing/structured_data_merger.py`
- [ ] 修改 `src/processing/process_coordinator.py`
- [ ] 修改 `process_single.py` (集成新模块)
- [ ] 添加单元测试
- [ ] 更新 requirements.txt
- [ ] 验证 .env 配置
- [ ] 文档说明更新

---

## 七、配置示例

### .env 新增项

```bash
# 文件提取配置
PDF_EXTRACTION_METHOD=pandoc              # pandoc/pymupdf4o/pypdf/ocr
INCREMENTAL_PROCESSING=true               # 启用增量处理
DEDUPLICATION_ENABLED=true                # 启用去重
HASH_ALGORITHM=sha256                     # 哈希算法

# 处理限制
MAX_RETRIES=3                             # 失败重试次数
BATCH_SIZE=10                             # 批处理大小
```

---

## 八、预期效果

| 指标 | 值 |
|-----|-----|
| 存储节省 | ~60% (去除重复) |
| 处理时间 | ~80% (增量检测) |
| 去重准确率 | 99.9% (SHA256) |
| 数据追踪 | 完整 (file_index) |

---

**下一步**: 开发上述3个新模块，集成到现有流程
