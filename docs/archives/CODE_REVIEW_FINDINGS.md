# 代码审查结果 - Skill Report Genie

## 审查日期
2026-01-19

## 用户需求回顾

用户提出的三个主要改进需求：

1. **通过内容提取判断文件类型** - 需要读取文件内容，而不仅仅依赖文件名
2. **中文目录名** - 分类目录应该使用中文命名
3. **参数提取改善** - 第一轮测试数据全错，需要改进提取逻辑

## 当前实现状态分析

### 1. 文件分类机制 (`src/file_handler/scanner.py`)

**当前实现：**
- ✅ 使用中文目录名（FileCategory枚举）
  ```python
  MEDICAL_RECORDS = "医疗诊疗/病历"
  IMAGING = "医疗诊疗/影像"
  LAB_REPORTS = "医疗诊疗/检查检测报告"
  PRESCRIPTIONS = "医疗诊疗/处方用药"
  NUTRITION = "营养管理"
  PSYCHOLOGY = "心理支持管理"
  COMPLICATIONS = "并发症管理"
  ```

- ❌ **仅基于文件名分类，未实现内容提取**
  - `_classify_file()` 方法只检查文件扩展名和文件名关键词
  - 没有读取文件内容进行分类
  - 缺少OCR或文本提取功能

**关键代码片段：**
```python
def _classify_file(self, file_path: str, file_name: str) -> Tuple[FileCategory, float]:
    extension = self._get_file_extension(file_path)
    file_name_lower = file_name.lower()
    
    # 仅检查扩展名和文件名，未读取内容
    for rule in self.CLASSIFICATION_RULES:
        if extension not in rule['extensions']:
            continue
        
        keywords = rule.get('keywords', [])
        keyword_matches = sum(
            1 for kw in keywords 
            if kw.lower() in file_name_lower  # 只检查文件名
        )
```

### 2. 参数提取机制

**当前实现：**
- ✅ `src/analysis/pathology_extractor.py` - 病理特征提取
- ✅ `src/analysis/genetic_extractor.py` - 基因信息提取  
- ✅ `src/analysis/marker_analyzer.py` - 肿瘤标志物分析

**问题：**
- ❌ 这些提取器需要**结构化输入**（字典格式），而不是原始文件
- ❌ 缺少从原始文件（PDF/图片/Word）到结构化数据的转换层
- ❌ 没有OCR或文档解析模块

**示例：**
```python
# pathology_extractor.py 需要这样的输入：
report = {
    "primary_pathology": "pancreatic_ductal_adenocarcinoma",
    "differentiation_grade": "II",
    "special_markers": {"claudin18": "positive", "HER2": "negative"}
}
# 但是缺少从 PDF/图片 → 这个字典 的转换过程
```

### 3. 测试文件分析

**第一轮测试目录** (`/Users/qinxiaoqiang/Downloads/report_mess`):
- 129个文件，主要是图片（JPG/PNG/HEIC）
- 文件名多为 `IMG_xxxx.JPG` 这样的通用名称
- 只有1个Excel文件 (`ca199.xlsx`) 和1个PDF (`01 病情概述.pdf`)

**为什么第一轮测试失败：**
1. 文件名无意义（IMG_0073.PNG），无法通过文件名分类
2. 没有内容提取，无法识别图片中的医疗信息
3. 缺少OCR功能，无法读取图片中的文字

### 4. 缺失的功能模块

根据 `DEVELOPMENT_PLAN.md`，以下功能被标记为"可选"但实际上是**必需的**：

❌ **OCR模块** (`src/file_handler/ocr_handler.py`) - 不存在
- 计划使用：paddleOCR / mineru
- 状态：未实现

❌ **文档解析模块** - 不存在  
- PDF文本提取
- Word文档解析
- Excel数据读取

❌ **内容分类智能体** - 不存在
- 读取文件内容
- 基于内容判断文件类型
- 生成文件类型JSON

## 需要实现的功能

### 优先级1：内容提取与分类

1. **创建 `src/file_handler/content_extractor.py`**
   - PDF文本提取（pypdf）
   - Word文档解析（python-docx）
   - Excel数据读取（openpyxl）
   - 图片OCR（paddleOCR/mineru）

2. **创建 `src/file_handler/content_classifier.py`**
   - 基于提取的内容进行分类
   - 生成文件类型JSON
   - 与现有的 `scanner.py` 集成

3. **更新 `scanner.py`**
   - 调用 `content_extractor` 读取文件内容
   - 使用内容+文件名综合判断分类
   - 生成置信度评分

### 优先级2：参数提取改善

1. **创建文档解析管道**
   ```
   原始文件 → 内容提取 → 文本清洗 → 结构化提取 → JSON输出
   ```

2. **改进提取器输入**
   - 让提取器接受原始文本输入
   - 使用LLM或正则表达式从文本中提取字段
   - 生成标准化的字典格式

### 优先级3：元数据管理

1. **文件类型JSON**
   - 记录每个文件的分类结果
   - 包含置信度和分类依据
   - 支持人工校正

## 建议的实现步骤

1. **第一步：实现内容提取**
   - 创建 `content_extractor.py`
   - 支持PDF、图片、Word、Excel
   - 返回提取的文本内容

2. **第二步：改进分类逻辑**
   - 更新 `scanner.py` 调用内容提取
   - 基于内容+文件名综合分类
   - 生成文件类型JSON

3. **第三步：改进参数提取**
   - 创建文本解析管道
   - 从提取的文本中识别关键字段
   - 生成结构化数据

4. **第四步：第二轮测试**
   - 使用改进的代码处理 `/Users/qinxiaoqiang/Downloads/report_mess`
   - 验证分类准确性
   - 检查参数提取结果

## 总结

**已满足的需求：**
- ✅ 中文目录名（已实现）

**未满足的需求：**
- ❌ 内容提取判断文件类型（缺少OCR和文档解析）
- ❌ 参数提取改善（缺少从原始文件到结构化数据的转换）

**核心问题：**
当前代码架构完整，但缺少**内容提取层**，导致：
1. 只能基于文件名分类，对通用文件名（IMG_xxxx.JPG）无能为力
2. 参数提取器需要结构化输入，但缺少从原始文件生成结构化数据的模块
3. 第一轮测试失败是因为大量图片文件无法被正确识别和处理

**建议：**
实现内容提取模块是解决所有问题的关键。
