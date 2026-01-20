# SQLite自动化部署指南

## 快速开始

### 1. 环境要求
- Python 3.8+（sqlite3是内置库，无需额外安装）
- 磁盘空间：至少100MB用于数据库文件

### 2. 自动化初始化流程

#### 步骤1：运行初始化脚本
```bash
# 在Skill启动时自动执行
python -c "
from src.database.init_database import DatabaseInitializer
initializer = DatabaseInitializer('patient_case/skill.db')
initializer.initialize()
print('✓ 数据库初始化完成')
"
```

#### 步骤2：验证数据库
```bash
# 检查数据库文件是否创建
ls -lh patient_case/skill.db

# 使用sqlite3命令行检查表结构
sqlite3 patient_case/skill.db ".tables"
# 输出: dedup_records file_index markers_history patient_index processing_log sys_params version_history
```

#### 步骤3：验证连接
```python
from src.database.db_manager import DatabaseManager

# 获取连接管理器（单例，自动连接）
db = DatabaseManager()

# 测试连接
result = db.execute("SELECT COUNT(*) as count FROM sys_params").fetchone()
print(f"✓ 系统参数表记录数: {result['count']}")
```

---

## 数据库架构

### 7个核心表

#### 1. **file_index** - 文件扫描和处理记录
```sql
CREATE TABLE file_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_hash TEXT UNIQUE NOT NULL,           -- MD5或SHA256哈希
    file_path TEXT NOT NULL,                  -- 文件完整路径
    file_size INTEGER,                        -- 文件大小（字节）
    file_type TEXT,                           -- 文件类型（pdf, docx等）
    mtime REAL,                               -- 文件修改时间（Unix时间戳）
    status TEXT DEFAULT 'pending',            -- 处理状态：pending/processing/success/failed
    error_msg TEXT,                           -- 错误信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**用途**：
- 增量识别：通过hash和mtime检测新增或变更文件
- 重复检测：hash检查防止处理重复文件
- 处理追踪：status字段记录处理状态

**关键索引**：
- idx_file_hash：快速查询文件
- idx_file_status：查询待处理文件列表

**查询示例**：
```python
# 检查文件是否已处理
existing = file_ops.query_by_hash(file_hash)
if existing:
    if existing['mtime'] == current_mtime:
        print("文件未变更，跳过")
    else:
        print("文件已变更，重新处理")
else:
    print("新文件，首次处理")
```

---

#### 2. **patient_index** - 患者记录索引
```sql
CREATE TABLE patient_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT UNIQUE NOT NULL,          -- 脱敏患者ID（hash）
    case_type TEXT NOT NULL,                  -- 癌肿类型（pancreatic_cancer等）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    import_count INTEGER DEFAULT 1            -- 导入次数
);
```

**用途**：
- 患者身份管理：使用脱敏patient_id
- 案例分类：支持多癌肿类型
- 导入计数：跟踪患者更新频率

---

#### 3. **markers_history** - 肿瘤标志物历史
```sql
CREATE TABLE markers_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL,                 -- 患者ID
    marker_type TEXT NOT NULL,                -- CA19-9, CA50, CA125, CA72-4
    date DATE NOT NULL,                       -- 检测日期
    value REAL,                               -- 检测值
    unit TEXT,                                -- 单位（U/mL, ng/mL等）
    source_file TEXT,                         -- 来源文件
    imputed INTEGER DEFAULT 0,                -- 是否为AI补全：0=实际, 1=补全
    confidence TEXT,                          -- 置信度：high/medium/low
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(patient_id) REFERENCES patient_index(patient_id)
);
```

**用途**：
- 肿瘤标志物时间序列数据
- 支持多标志物对比分析
- 记录补全标记和置信度

**关键查询**：
```python
# 获取肿瘤标志物趋势
marker_ops.get_marker_trend(patient_id, 'CA19-9')
# 返回：[{date, value, imputed}, ...]
```

---

#### 4. **processing_log** - 处理日志
```sql
CREATE TABLE processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL,
    import_id TEXT NOT NULL,                  -- 导入批次ID
    step TEXT NOT NULL,                       -- 处理步骤：classification/extraction/dedup/storage/report
    status TEXT NOT NULL,                     -- success/failed/skipped
    error_msg TEXT,
    duration_seconds REAL,                    -- 处理耗时
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(patient_id) REFERENCES patient_index(patient_id)
);
```

**用途**：
- 处理步骤记录
- 故障排查：错误追踪
- 性能监控：处理耗时统计

---

#### 5. **dedup_records** - 文件去重记录
```sql
CREATE TABLE dedup_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_hash TEXT UNIQUE NOT NULL,
    file_count INTEGER,                       -- 重复文件总数
    kept_file TEXT NOT NULL,                  -- 保留的文件名
    duplicates_json TEXT,                     -- JSON数组，重复文件列表
    recorded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**用途**：
- 记录去重结果
- 追踪文件来源（用于溯源）

---

#### 6. **version_history** - 数据版本控制
```sql
CREATE TABLE version_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL,
    data_type TEXT NOT NULL,                  -- genetics/pathology/diagnosis/markers
    version INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    source TEXT,                              -- 来源报告或文件
    content_hash TEXT,                        -- 内容哈希，用于变化检测
    metadata_json TEXT,                       -- 额外元数据
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(patient_id) REFERENCES patient_index(patient_id)
);
```

**用途**：
- 长期记忆版本控制
- 复诊时检测数据变化
- memos同步参考

---

#### 7. **sys_params** - 系统参数表
```sql
CREATE TABLE sys_params (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    param_key TEXT UNIQUE NOT NULL,
    param_value TEXT,
    param_type TEXT,                          -- string/integer/json
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**初始参数**：
```
db_version = "1.0"
db_created_at = "2026-01-19T10:30:00"
last_maintenance = "2026-01-19T10:30:00"
enable_privacy_mode = "1"
default_patient_id_method = "hash"
```

---

## 自动化连接和操作

### 连接管理器（单例模式）
```python
from src.database.db_manager import DatabaseManager

# 获取连接（自动初始化和重连）
db = DatabaseManager()

# 执行查询
result = db.execute("SELECT * FROM file_index WHERE status = ?", ('pending',))
for row in result:
    print(row['file_path'])

# 提交和回滚
db.commit()
db.rollback()
```

### 文件操作示例
```python
from src.database.db_operations import FileIndexOps
import hashlib

file_ops = FileIndexOps(db)

# 1. 插入新文件
with open('report.pdf', 'rb') as f:
    file_hash = hashlib.md5(f.read()).hexdigest()
    file_ops.insert_file(
        file_hash=file_hash,
        file_path='medical_diagnosis/report.pdf',
        file_size=1024000,
        mtime=1705660200.0
    )

# 2. 查询文件
record = file_ops.query_by_hash(file_hash)
if record:
    print(f"文件已存在，状态: {record['status']}")

# 3. 获取待处理文件
pending = file_ops.get_pending_files()
for file_record in pending:
    # 处理文件
    try:
        process_file(file_record['file_path'])
        file_ops.update_status(file_record['file_hash'], 'success')
    except Exception as e:
        file_ops.update_status(file_record['file_hash'], 'failed', str(e))
```

### 肿瘤标志物操作示例
```python
from src.database.db_operations import MarkerOps

marker_ops = MarkerOps(db)

# 1. 插入标志物记录
marker_ops.insert_marker(
    patient_id='hash_xxx',
    marker_type='CA19-9',
    date='2023-01-15',
    value=245.5,
    source_file='血液检查_2023-01-15.pdf',
    imputed=0,
    confidence='high'
)

# 2. 获取趋势数据（用于生成图表）
trend = marker_ops.get_marker_trend('hash_xxx', 'CA19-9')
for record in trend:
    print(f"{record['date']}: {record['value']} (补全: {record['imputed']})")
```

---

## 性能优化

### 批量操作
```python
# 批量插入文件记录（避免逐条插入）
cursor = db.get_connection().cursor()
files = [
    (hash1, path1, size1, mtime1),
    (hash2, path2, size2, mtime2),
    # ...
]
cursor.executemany('''
    INSERT INTO file_index (file_hash, file_path, file_size, mtime, status)
    VALUES (?, ?, ?, ?, 'pending')
''', files)
db.commit()
```

### 查询优化
```python
# 使用indexed字段查询
# ✓ 快速（使用了索引）
cursor = db.execute(
    "SELECT * FROM file_index WHERE file_hash = ?",
    (file_hash,)
)

# ✗ 慢速（全表扫描）
cursor = db.execute(
    "SELECT * FROM file_index WHERE file_path LIKE '%report%'"
)
```

### 事务处理
```python
try:
    # 关闭自动提交，启用事务
    db._connection.isolation_level = None  # 对于WAL模式
    
    # 多个操作
    file_ops.insert_file(...)
    marker_ops.insert_marker(...)
    
    # 一次性提交
    db.commit()
except Exception as e:
    # 失败时回滚
    db.rollback()
    raise
```

---

## 故障恢复

### 数据库损坏修复
```python
# 如果SQLite报告数据库损坏，可以尝试重建索引
sqlite3 patient_case/skill.db "REINDEX"

# 或者备份后删除，让系统重新初始化
cp patient_case/skill.db patient_case/skill.db.bak
rm patient_case/skill.db

# 重启Skill，自动重新初始化
```

### 连接失败处理
```python
# DatabaseManager已内置自动重连机制
# 如果连接仍然失败，可以手动重新初始化

from src.database.db_manager import DatabaseManager
db = DatabaseManager()

# 如果连接失败
if not db._connection:
    db.close()
    db = DatabaseManager()  # 重新创建单例
```

---

## 监控和维护

### 数据库大小监控
```bash
# 查看数据库文件大小
ls -lh patient_case/skill.db

# 查看表大小（SQLite没有原生命令，但可以估算）
sqlite3 patient_case/skill.db "
SELECT 'file_index' as table_name, COUNT(*) as row_count FROM file_index
UNION ALL
SELECT 'markers_history', COUNT(*) FROM markers_history
UNION ALL
SELECT 'processing_log', COUNT(*) FROM processing_log
"
```

### 定期维护
```python
# 定期VACUUM压缩数据库（释放已删除记录的空间）
db.execute("VACUUM")

# 重新索引（提升查询性能）
db.execute("REINDEX")
```

### 备份策略
```bash
# 每天备份数据库
cp patient_case/skill.db patient_case/skill.db.$(date +%Y%m%d)

# 保留最近7天的备份
find patient_case -name "skill.db.*" -mtime +7 -delete
```

---

## 常见问题

**Q: 数据库文件在哪里？**
A: 默认位置：`patient_case/skill.db`

**Q: 如何导出数据？**
A: 使用sqlite3命令行或Python sqlite3库导出CSV/JSON

**Q: 支持并发访问吗？**
A: SQLite的WAL模式支持多读一写，足以满足Skill的并发需求

**Q: 如何在多个患者间隔离数据？**
A: 使用patient_id进行数据隔离，确保查询时指定patient_id

---

**最后更新**：2026-01-19
