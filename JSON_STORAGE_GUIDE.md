# JSON数据存储与版本控制指南

## 概览

本Skill采用**JSON + 版本控制 + 时间戳**作为主要数据存储方案，完全本地存储，适配非技术患者，隐私安全第一。

---

## 核心特点

✅ **非技术用户友好**
- 无需数据库维护
- 文件夹和文件名直观易懂
- 版本和日期清晰标注

✅ **完全本地存储**
- 所有数据保存在本地文件系统
- 无云端依赖
- 隐私保护最高

✅ **版本控制**
- 自动保存历史版本
- 支持复诊更新和对比
- 完整的演变历史

✅ **增量识别**
- 通过hash检测新增/重复文件
- 通过mtime检测文件变更
- 避免重复处理

---

## 目录结构

```
patient_case/
├── _metadata/                          # 系统元数据
│   ├── patient_master_v1_2024-01-15.json
│   ├── patient_master_v2_2024-06-20.json   # 版本历史
│   ├── processing_log_2024-01-15.json
│   └── processing_log_2024-06-20.json
│
├── _reports/                           # AI生成的输出报告
│   ├── disease_report_2024-06-20.md
│   ├── disease_report_2024-06-20.pdf
│   └── ...
│
├── [11个顶级目录...]
│   └── [具体文件和数据JSON]
│
└── _version_history/                   # 版本历史存档（可选）
    ├── patient_master/
    │   ├── v1_2024-01-15.json
    │   ├── v2_2024-06-20.json
    │   └── v3_2024-12-15.json
    └── markers_history/
        ├── v1_2024-01-15.json
        └── v2_2024-06-20.json
```

---

## JSON文件命名规则

### 主要数据文件

**格式**：`{file_name}_v{version}_{date}.json`

**示例**：
- `patient_master_v1_2024-01-15.json`
- `patient_master_v2_2024-06-20.json`
- `markers_history_v1_2024-01-15.json`
- `genetics_v1_2024-01-15.json`
- `pathology_v1_2024-01-15.json`

### 临时日志文件

**格式**：`{log_type}_{date}.json`

**示例**：
- `processing_log_2024-01-15.json`
- `extraction_log_2024-06-20.json`
- `dedup_records_2024-01-15.json`

---

## 核心JSON结构

### 1. patient_master.json - 患者主数据

```json
{
  "metadata": {
    "patient_id": "hash_xxx",
    "version": 2,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-06-20T14:45:00Z",
    "version_history": [
      {
        "version": 1,
        "timestamp": "2024-01-15T10:30:00Z",
        "source": "初诊导入",
        "changes": "创建患者记录"
      },
      {
        "version": 2,
        "timestamp": "2024-06-20T14:45:00Z",
        "source": "复诊更新",
        "changes": "更新肿瘤标志物数据"
      }
    ]
  },
  "basic_info": {
    "age": 58,
    "gender": "M",
    "case_type": "pancreatic_cancer",
    "diagnosis_date": "2023-01-15"
  },
  "pathology": {...},
  "genetic_testing": {...},
  "treatments": [...],
  "imaging_reports": [...],
  "tumor_markers": [...]
}
```

### 2. markers_history.json - 肿瘤标志物历史

```json
{
  "patient_id": "hash_xxx",
  "version": 2,
  "updated_at": "2024-06-20T14:45:00Z",
  "markers": {
    "CA19-9": {
      "unit": "U/mL",
      "reference_value": "< 43",
      "measurements": [
        {
          "date": "2023-01-10",
          "value": 245.5,
          "source": "初诊检查_血液检查.pdf",
          "imputed": 0,
          "confidence": "high"
        },
        {
          "date": "2023-02-15",
          "value": 95.2,
          "source": "C1化疗后_血液检查.pdf",
          "imputed": 0,
          "confidence": "high"
        }
      ]
    },
    "CA50": {...},
    "CA125": {...},
    "CA72-4": {...}
  }
}
```

### 3. processing_log.json - 处理日志

```json
{
  "patient_id": "hash_xxx",
  "logs": [
    {
      "import_id": "import_001",
      "timestamp": "2024-01-15T10:30:00Z",
      "step": "file_classification",
      "status": "success",
      "files_processed": 50,
      "files_successful": 48,
      "files_failed": 2,
      "duration_seconds": 120
    },
    {
      "import_id": "import_001",
      "timestamp": "2024-01-15T10:32:00Z",
      "step": "information_extraction",
      "status": "success",
      "records_extracted": 48,
      "duration_seconds": 180
    }
  ]
}
```

### 4. dedup_records.json - 文件去重记录

```json
{
  "records": [
    {
      "file_hash": "abc123def456",
      "file_count": 2,
      "kept_file": "file_v1.pdf",
      "duplicates": ["file_副本.pdf"],
      "recorded_date": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

## 版本控制实现

### 版本号管理

**递增版本号**：v1 → v2 → v3 ...

```python
def get_next_version(existing_versions):
    """获取下一个版本号"""
    if not existing_versions:
        return 1
    return max(existing_versions) + 1

# 示例
existing_versions = [1, 2, 3]
next_version = get_next_version(existing_versions)  # 返回 4
```

### 日期后缀

**格式**：YYYY-MM-DD

```python
from datetime import datetime

def get_date_suffix():
    """获取今天的日期后缀"""
    return datetime.now().strftime("%Y-%m-%d")

# 返回：2024-06-20
```

### 版本历史记录

每个JSON文件包含完整版本历史：

```python
def add_version_entry(json_data, version, source, changes):
    """添加版本历史条目"""
    version_entry = {
        "version": version,
        "timestamp": datetime.now().isoformat(),
        "source": source,  # 来源文件或更新原因
        "changes": changes  # 主要变更说明
    }
    json_data["metadata"]["version_history"].append(version_entry)
    return json_data
```

---

## 增量识别实现

### 文件Hash计算

```python
import hashlib

def calculate_file_hash(file_path):
    """计算文件的SHA256哈希"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# 示例
file_hash = calculate_file_hash("medical_diagnosis/report.pdf")
# 返回：abc123def456...（64个十六进制字符）
```

### 变更检测

```python
import os
import json

def detect_file_changes(file_path, last_known_state):
    """检测文件是否有变更"""
    current_mtime = os.path.getmtime(file_path)
    current_hash = calculate_file_hash(file_path)
    
    last_mtime = last_known_state.get("mtime")
    last_hash = last_known_state.get("hash")
    
    if current_mtime != last_mtime or current_hash != last_hash:
        return {
            "changed": True,
            "reason": "mtime" if current_mtime != last_mtime else "content"
        }
    
    return {"changed": False}

# 示例
file_state = {
    "mtime": 1705660200.0,
    "hash": "abc123..."
}

changes = detect_file_changes("report.pdf", file_state)
# 返回：{"changed": True, "reason": "content"}
```

### 增量识别记录

```json
{
  "file_index": [
    {
      "file_path": "medical_diagnosis/report.pdf",
      "file_hash": "abc123...",
      "mtime": 1705660200.0,
      "status": "processed",
      "last_processed": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

## 数据读写操作

### 读取JSON文件

```python
import json

def load_json_file(file_path):
    """加载JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 示例
patient_data = load_json_file("_metadata/patient_master_v2_2024-06-20.json")
```

### 写入JSON文件（新建版本）

```python
def save_json_version(data, base_filename, patient_id):
    """保存JSON文件新版本"""
    # 1. 加载现有版本找到最新版本号
    existing_files = glob.glob(f"_metadata/{base_filename}_v*_*.json")
    versions = [int(re.search(r'_v(\d+)_', f).group(1)) for f in existing_files]
    next_version = max(versions) + 1 if versions else 1
    
    # 2. 获取今天日期
    date_suffix = datetime.now().strftime("%Y-%m-%d")
    
    # 3. 更新metadata
    data["metadata"]["version"] = next_version
    data["metadata"]["updated_at"] = datetime.now().isoformat()
    
    # 4. 保存新文件
    filename = f"_metadata/{base_filename}_v{next_version}_{date_suffix}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filename

# 示例
new_file = save_json_version(
    data=patient_master,
    base_filename="patient_master",
    patient_id="hash_xxx"
)
# 返回：_metadata/patient_master_v2_2024-06-20.json
```

### 更新JSON文件

```python
def update_json_field(file_path, field_path, new_value):
    """更新JSON文件中的特定字段"""
    # 1. 加载文件
    data = load_json_file(file_path)
    
    # 2. 使用点号路径更新（如 "basic_info.age"）
    keys = field_path.split(".")
    current = data
    for key in keys[:-1]:
        current = current[key]
    current[keys[-1]] = new_value
    
    # 3. 保存新版本
    return save_json_version(data, "patient_master", data["metadata"]["patient_id"])

# 示例
update_json_field(
    file_path="_metadata/patient_master_v1_2024-01-15.json",
    field_path="basic_info.age",
    new_value=59
)
```

---

## 多患者管理

每个患者有独立的JSON目录和文件：

```
patient_case_root/
├── patient_hash_001/
│   ├── _metadata/
│   │   └── patient_master_v1_2024-01-15.json
│   ├── genetics/
│   └── [其他目录...]
│
└── patient_hash_002/
    ├── _metadata/
    │   └── patient_master_v1_2024-01-15.json
    ├── genetics/
    └── [其他目录...]
```

---

## 版本对比和合并

### 对比两个版本

```python
from deepdiff import DeepDiff

def compare_versions(v1_path, v2_path):
    """对比两个版本的差异"""
    v1_data = load_json_file(v1_path)
    v2_data = load_json_file(v2_path)
    
    differences = DeepDiff(v1_data, v2_data, ignore_order=True)
    return differences

# 示例
diffs = compare_versions(
    "patient_master_v1_2024-01-15.json",
    "patient_master_v2_2024-06-20.json"
)
# 输出：{'values_changed': {...}, 'items_added': [...]}
```

### 简单版本合并（复诊更新）

```python
def merge_updates(base_version_path, new_data):
    """合并新数据到现有版本"""
    # 1. 加载基础版本
    base_data = load_json_file(base_version_path)
    
    # 2. 递归合并（新数据覆盖旧数据）
    import copy
    merged = copy.deepcopy(base_data)
    merged.update(new_data)
    
    # 3. 保存新版本
    return save_json_version(merged, "patient_master", merged["metadata"]["patient_id"])
```

---

## 性能考虑

### JSON文件大小

典型患者JSON文件大小：
- `patient_master.json`：50-200KB
- `markers_history.json`：10-50KB
- `processing_log.json`：5-20KB

**总计**：每患者约100-300KB，完全在本地存储可接受。

### 文件数量

初诊：
- 根文件夹：1-2个JSON
- 子文件夹：10-15个JSON

复诊（年）：
- 每患者增加3-5个新版本文件

**管理**：手动清理或自动归档旧版本到 `_version_history/`

---

## 备份和安全

### 自动备份策略

```python
import shutil
from datetime import datetime

def backup_patient_data(patient_dir):
    """备份患者数据"""
    backup_dir = f"{patient_dir}/_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copytree(patient_dir, backup_dir)
    return backup_dir

# 在重要操作前自动备份
backup_path = backup_patient_data(f"patient_case/{patient_id}")
```

### 版本恢复

```python
def restore_from_version(patient_id, version):
    """从指定版本恢复数据"""
    version_file = f"patient_case/{patient_id}/_metadata/patient_master_v{version}_*.json"
    matching_files = glob.glob(version_file)
    if matching_files:
        # 加载旧版本并保存为新版本
        old_data = load_json_file(matching_files[0])
        return save_json_version(old_data, "patient_master", patient_id)
```

---

## 常见问题

**Q: 如何选择某个特定日期的版本？**
A: 文件名包含日期后缀，查看目录列表即可选择。例如：
```
patient_master_v2_2024-06-20.json  ← 2024年6月20日的版本
patient_master_v3_2024-12-15.json  ← 2024年12月15日的版本
```

**Q: 版本号和日期不匹配怎么办（如v1日期是2024-06-20）？**
A: 说明该版本是在那个日期生成或更新的。版本号是递增的，日期是生成日期。

**Q: 如何导出患者的完整历史？**
A: 收集所有版本文件，按版本号排序，可生成时间线对比。

**Q: 如何处理超大患者数据（多年跟踪）？**
A: 
- 定期清理冗余版本（保留关键版本+最新版本）
- 将旧版本归档到 `_version_history/` 目录
- 若需要数据库性能，可启用SQLite（enable_sqlite=true）

**Q: JSON文件损坏怎么办？**
A: 从最近的备份或版本历史恢复：
```python
# 恢复上个版本
restore_from_version(patient_id, version_number - 1)
```

---

**最后更新**：2026-01-19
**主方案**：JSON + 版本控制（非技术用户友好，完全本地）
**可选增强**：SQLite（enable_sqlite=true）
