# 单个医学图片OCR解析指南

## 概述

`parse_single_image.py` 是一个独立的命令行工具，用于快速准确地解析医学图片并提取结构化信息。

## 多级降级策略

系统优先级顺序（按速度和准确性）：

```
step-1o-turbo-vision (StepFun) ⚡ 最快最准
    ↓ (失败时)
DeepSeek-OCR (SiliconFlow) ⚙️ 中等速度
    ↓ (失败时)
Gemini-3-Flash (Google) 🔄 备选方案
    ↓ (失败时)
PaddleOCR (本地) 📱 最后方案
```

## 环境配置

在 `.env` 文件中配置以下参数：

```ini
# StepFun API 配置 (推荐)
STEPFUN_API_KEY=your_stepfun_api_key
STEPFUN_BASE_URL=https://api.stepfun.com/v1
STEPFUN_MODEL=step-1o-turbo-vision

# SiliconFlow (DeepSeek) 备选配置
SILICONFLOW_API_KEY=your_siliconflow_api_key
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_MODEL=deepseek-ai/DeepSeek-OCR

# Google Gemini 备选配置
GOOGLE_API_KEY=your_google_api_key
# 或
GEMINI_API_KEY=your_gemini_api_key
```

## 使用方法

### 基本用法

解析单个图片：

```bash
python parse_single_image.py /path/to/image.jpg
```

### 保存结果

解析并保存结果到指定目录：

```bash
python parse_single_image.py /path/to/image.jpg -o ./output
```

输出文件：
- `image_name_result.json` - 完整结果（包括元数据和结构化数据）
- `image_name_text.txt` - 提取的纯文本
- `image_name_data.json` - 结构化数据（仅当API返回时）

### 批量处理

解析多个图片：

```bash
python parse_single_image.py image1.jpg image2.jpg image3.jpg -o ./output
```

会自动生成：
- 各个图片的输出文件
- `summary.json` - 批量结果摘要

### 高级选项

```bash
# 不输出日志（静默模式）
python parse_single_image.py /path/to/image.jpg -q
```

## 输出格式

### JSON 结果结构

```json
{
  "image_path": "/path/to/image.jpg",
  "image_name": "image.jpg",
  "extraction_method": "ocr",
  "confidence": 0.98,
  "language": "zh",
  "text_length": 1234,
  "error": null,
  "full_text": "提取的完整文本内容...",
  "structured_data": {
    "patient_name": "患者姓名",
    "report_date": "2024-09-05",
    "report_type": "CT影像",
    "summary": "报告摘要...",
    "full_text": "完整文字内容...",
    "indicators": [
      {
        "name": "指标名称",
        "value": "数值",
        "unit": "单位",
        "reference_range": "参考范围",
        "is_abnormal": false,
        "arrow": "-"
      }
    ],
    "findings": "影像发现...",
    "diagnosis": "诊断结论"
  }
}
```

## 返回值说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `extraction_method` | 使用的提取方法 | `ocr`, `text`, `parsing` |
| `confidence` | 提取置信度 (0-1) | `0.98` |
| `text_length` | 提取文本的字符数 | `1234` |
| `error` | 错误信息（成功时为null） | `null` |
| `language` | 检测到的语言 | `zh`, `en` |

## 医学数据提取规范

### 支持的报告类型

- 血常规报告
- 生化检验报告
- CT/MRI影像报告
- 病理诊断报告
- 处方用药记录
- B超检查报告
- 其他医疗文档

### 指标提取

如果检测到的是检验报告，系统会自动提取：
- 指标名称 (如 CA19-9, CEA)
- 数值和单位
- 参考范围
- 异常标记 (↑/↓)
- 是否异常 (true/false)

## 常见问题

### Q: 为什么需要配置多个API？

A: 为了保证高可用性。当某个API服务不可用或速率限制时，系统会自动切换到备选方案。

### Q: step-1o-turbo-vision 比 DeepSeek-OCR 快吗？

A: 是的，step-1o-turbo-vision 通常更快更准确，推荐优先使用。

### Q: 如果全部API都失败会怎样？

A: 系统会自动使用本地 PaddleOCR 进行离线识别，但准确度可能较低。

### Q: 如何处理多页医疗文档？

A: 建议逐页转换为图片后分别解析，再合并结果。可使用 PDF 转图片工具如 `pdf2image`。

### Q: 识别结果不准确怎么办？

A: 
1. 检查图片质量（清晰度、亮度）
2. 确认使用了 StepFun API（最准确）
3. 尝试调整图片方向
4. 对于手写内容，准确度会降低

## 完整工作流示例

```bash
#!/bin/bash

# 1. 将PDF转换为图片
pdf2image medical_report.pdf output_images/

# 2. 逐个解析图片
for img in output_images/*.jpg; do
    python parse_single_image.py "$img" -o ./parsed_results
done

# 3. 查看结果
cat ./parsed_results/summary.json
```

## 性能指标

| 方法 | 平均速度 | 准确率 | 成本 |
|------|--------|--------|------|
| step-1o-turbo-vision | ~2-3s | 98% | 💰 低 |
| DeepSeek-OCR | ~3-4s | 95% | 💰 低 |
| Gemini-3-Flash | ~5-6s | 92% | 💰 中 |
| PaddleOCR (本地) | ~1-2s | 85% | 🆓 免费 |

## 故障排除

### 错误：`STEPFUN_API_KEY` 未配置

```bash
# 检查 .env 文件是否存在
ls -la .env

# 查看配置
grep STEPFUN .env

# 如果不存在，复制模板并编辑
cp .env.template .env
# 编辑 .env 文件，填入实际的 API 密钥
```

### 错误：图片文件不存在

确保提供的路径正确，可以使用绝对路径：

```bash
python parse_single_image.py /Users/username/path/to/image.jpg
```

### 错误：API 超时

增加超时时间或检查网络连接：

```python
# 在 content_extractor.py 中修改超时时间
response = requests.post(..., timeout=120)  # 改为120秒
```

## 脚本集成

### Python 脚本集成

```python
from parse_single_image import parse_image

# 解析图片
result = parse_image("/path/to/image.jpg")

# 访问提取的文本
print(result['full_text'])

# 访问结构化数据
print(result['structured_data'])
```

### 批量处理集成

```python
from pathlib import Path
from parse_single_image import parse_image

# 处理目录中所有图片
image_dir = Path("/path/to/images")
results = [parse_image(str(img)) for img in image_dir.glob("*.jpg")]
```

## 许可和条款

使用本工具需要配置有效的 API 密钥。每次API调用都会产生相应的费用。详见各API提供商的使用条款。

## 联系和支持

如有问题，请提交 Issue 或联系开发团队。
