# process_single.py 完整流程修复

## 问题分析

原代码流程缺失后4个关键步骤：
- ✅ 步骤1-4：扫描 → 解析 → JSON保存 → 重命名 → 分类（已实现）
- ❌ **步骤5：报告重点解析**（缺失）
- ❌ **步骤6：智能体调用 & 医学报告生成**（缺失）
- ❌ 缺失：多报告输出（完整版+科普版+可视化+问诊清单）
- ❌ 缺失：Web发布（需要通过report_deployer模块）

## 修复方案

### 修改内容

#### 1. 添加必需导入
```python
from src.processing.json_aggregator import JsonAggregator
from src.reporting.report_generator import ReportGenerator
from src.analysis.marker_analyzer import MarkerAnalyzer
from src.analysis.pathology_extractor import PathologyFeatureExtractor
from src.analysis.genetic_extractor import GeneticFeatureExtractor
from src.analysis.risk_stratifier import RiskStratifier
```

#### 2. 扩展流程（6步完整流程）
```
[1/6] 解析图片
[2/6] 保存主病情JSON
[3/6] 重命名文件
[4/6] 分类和移动文件
[5/6] 报告重点解析  ← 新增
    - 加载所有JSON数据
    - 生成患者数据汇总
    - 提取病理特征
    - 提取遗传特征
    - 进行风险评估
[6/6] 生成医学报告（调用两个智能体） ← 新增
    - PopularScienceAgent：科普版
    - VisualizationAgent：可视化版
    - 生成完整版 + 问诊清单
```

#### 3. 关键类的集成

**JsonAggregator（汇总器）**
- 加载所有提取的JSON文件
- 构建患者统一数据模型（patient_summary）

**ReportGenerator（报告生成器）**
- 调用PopularScienceAgent（科普智能体）
- 调用VisualizationAgent（可视化智能体）
- 生成4种报告格式：
  1. 完整版（医学专业版）
  2. 科普版（患者友好版）
  3. 可视化版（图表展示）
  4. 问诊清单（结构化问题）

**特征提取器集合**
- PathologyFeatureExtractor：病理特征
- GeneticFeatureExtractor：基因特征
- RiskStratifier：风险分层

### 4. 命令行接口更新
```bash
# 处理单张图片，生成所有报告（默认）
python process_single.py image.jpg -w /work/dir

# 跳过报告生成（仅做文件处理）
python process_single.py image.jpg -w /work/dir --no-report

# 保存结果JSON
python process_single.py image.jpg -w /work/dir -o result.json
```

## 完整流程图

```
输入：医学图片
  ↓
[1] 扫描 & OCR识别 → 提取文本内容
  ↓
[2] 解析 → 识别报告类型、诊断、关键数据
  ↓
[3] 保存JSON → _metadata/中存储结构化数据
  ↓
[4] 重命名 → 基于内容生成标准文件名
  ↓
[5] 分类 → 放入对应医疗目录结构
  ↓
[6] 汇总 → JsonAggregator加载所有JSON
  ↓
[7] 特征提取 → 病理、遗传、风险评估
  ↓
[8] 智能体处理 → PopularScienceAgent + VisualizationAgent
  ↓
[9] 报告生成 → 4种格式报告
  ↓
输出：
  ✓ 完整版医学报告(.md/.pdf)
  ✓ 患者科普版(.md)
  ✓ 可视化报告(.md with charts)
  ✓ 问诊清单(.html with interactive)
```

## 数据流转

```
原始图片
├─ OCR识别 → 原始文本
├─ 报告类型识别 → report_type
├─ 诊断提取 → diagnosis
└─ 关键值提取 → raw_data

↓ 保存JSON

patient_master.json
├─ basic_info
├─ pathology (来自PathologyExtractor)
├─ genetics (来自GeneticExtractor)
├─ imaging
├─ labs
├─ treatment_history
└─ risk_assessment (来自RiskStratifier)

↓ JsonAggregator汇总

patient_summary.json (完整患者数据模型)
  ├─ metadata
  ├─ patient_data (输入给智能体)
  └─ by_type

↓ ReportGenerator处理

最终报告
├─ 完整版_医学专业版.md
├─ 科普版_患者易读版.md
├─ 可视化版_图表展示.md
└─ 问诊清单_结构化问题.html
```

## 测试验证

```bash
# 1. 验证语法
python -m py_compile process_single.py

# 2. 帮助信息
python process_single.py -h

# 3. 测试运行（无报告生成）
python process_single.py test.jpg -w ./test_work --no-report -o result.json

# 4. 完整运行（包括报告生成）
python process_single.py test.jpg -w ./test_work --report -o result_with_reports.json
```

## 与设计文档对应关系

### skill_design.md 流程要求：
```
文件扫描 
→ 整理存放 
→ 提取信息并保存 ✅ (步骤2-3)
→ 整理病情 ✅ (步骤5-6)
→ 输出规范化病情报告 ✅ (步骤6)
→ 输出问诊建议 ✅ (步骤6)
```

### DEVELOPMENT_PLAN.md 核心功能：
```
[1/6] 扫描并解析文件 ✅
[2/6] 重命名文件 ✅
[3/6] 生成数据汇总 ✅ (新增步骤5)
[4/6] 创建分类目录 ✅
[5/6] 分类并移动文件 ✅
[6/6] 生成医学报告 ✅ (新增步骤6)
```

## 依赖模块检查

✅ ProcessCoordinator 已有完整实现（参考）
✅ ReportGenerator 已实现（已导入）
✅ PopularScienceAgent 已实现（自动调用）
✅ VisualizationAgent 已实现（自动调用）
✅ JsonAggregator 已实现（新增使用）
✅ PathologyFeatureExtractor 已实现
✅ GeneticFeatureExtractor 已实现
✅ RiskStratifier 已实现

## PDF解析配置

### 本地优先策略
1. **优先级1**：本地PDF解析（pypdf）
2. **优先级2**：本地OCR（paddleOCR）
3. **优先级3**：高级OCR（mineru）
4. **优先级4**：LLM备份（Qwen/Qwen3-8B via siliconflow）

### 实现位置
- `src/file_handler/content_extractor.py` - 内容提取管理
- `src/processing/file_processor.py` - 文件处理流程

## 下一步

### Web发布集成（可选）
```python
from src.web.report_deployer import ReportDeployer

deployer = ReportDeployer(output_dir=reports_dir)
deployer.deploy_reports(report_paths)
```

### 交互式Web UI（可选）
- 使用FastAPI或Flask
- 集成html_renderer生成交互页面
- 支持报告下载、分享

## 版本信息

- **修复版本**：v2.1
- **修复日期**：2026-01-20
- **关键改动**：集成完整的报告生成与智能体调用管道
- **后向兼容**：✅ 保持原有接口，添加--no-report选项
