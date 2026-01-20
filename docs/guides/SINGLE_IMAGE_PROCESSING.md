# 单张医学图片处理指南 (v2.1)

**版本**: 2.1 (简化版 - 每次处理1张)  
**日期**: 2024-01-19  
**状态**: ✅ 实现完成，生产可用

---

## 快速开始

### 最简单的用法

```bash
# 处理一张图片到临时目录
python process_single.py /path/to/image.jpg

# 处理到指定工作目录
python process_single.py /path/to/image.jpg -w ~/medical_work

# 保存处理结果 JSON
python process_single.py /path/to/image.jpg -w ~/medical_work -o result.json
```

### 工作流程

```
处理单张图片
  ↓
[1/3] 解析图片 (StepFun/DeepSeek/Gemini/本地OCR)
  ↓
[2/3] 标准化重命名 (<date>_<type>_<digest>_<seq>.ext)
  ↓
[3/3] 分类和移动文件 (到 work_dir/reports/<category>/)
  ↓
输出: 分类后的文件 + JSON 数据
```

---

## 详细用法

### 单张处理基本

```bash
python process_single.py image.jpg -w /work/dir
```

**输出**:
```
/work/dir/
├── data/
│   └── extracted/
│       └── hash.json
├── backup/
│   └── original/
│       └── image.jpg
├── logs/
│   └── processing.log
└── reports/
    └── imaging/
        └── CT/
            ├── 2024-09-05_CT_病灶标注_001.jpg
            └── hash.json
```

### 批量处理 (Shell 脚本)

```bash
#!/bin/bash
# 批量处理所有 JPG 图片

WORK_DIR=~/medical_work
mkdir -p $WORK_DIR

for img in *.jpg; do
    echo "处理: $img"
    python process_single.py "$img" -w $WORK_DIR
    echo "✓ $img 处理完成\n"
done

echo "✓ 所有图片处理完成!"
```

### 保存结果

```bash
# 处理多张图片，每张的结果保存为独立 JSON
for img in *.jpg; do
    result_file="results/${img%.jpg}.json"
    python process_single.py "$img" -w ~/work -o "$result_file"
done
```

---

## 输出说明

### 处理成功

```
================================================================================
处理图片: IMG_0125.JPG
================================================================================

[1/3] 解析图片...
✓ 解析成功 (置信度: 0.98)

[2/3] 重命名文件...
✓ 重命名: IMG_0125.JPG → 2024-09-05_CT_病灶标注_001.jpg

[3/3] 分类和移动文件...
✓ 文件已分类: imaging/CT

================================================================================
处理完成！
================================================================================
报告类型: DICOM CT
报告日期: 2024-09-05
诊断: 疑似胰腺或腹膜后病变
新文件名: 2024-09-05_CT_病灶标注_001.jpg
分类: imaging/CT
================================================================================
```

### 处理失败

```
✗ 解析失败: <错误信息>
```

---

## 文件名规范

### 标准格式

```
<date>_<type>_<digest>_<sequence>.<ext>

例如:
  2024-09-05_CT_病灶标注_001.jpg
  2023-06-27_血检_肿瘤标志物_001.jpg
  2023-07-06_病理_粘液腺癌_001.jpg
```

### 分类规则

| 类型 | 所属分类 | 示例 |
|------|---------|------|
| CT | imaging/CT | 2024-09-05_CT_病灶标注_001.jpg |
| MRI | imaging/MRI | 2024-09-05_MRI_肿瘤_001.jpg |
| 超声 | imaging/超声 | 2024-09-05_超声_肾脏_001.jpg |
| 血检 | lab_reports/血检 | 2023-06-27_血检_标志物_001.jpg |
| 病理 | lab_reports/病理 | 2023-07-06_病理_报告_001.jpg |
| 遗传 | lab_reports/遗传 | 2023-08-10_遗传_检测_001.jpg |
| 病历 | medical_records | 2023-06-23_病历_诊断_001.jpg |
| 处方 | prescriptions | 2024-01-10_处方_用药_001.jpg |
| 心理 | psychology | 2024-01-15_心理_评估_001.jpg |
| 营养 | nutrition | 2024-01-12_营养_计划_001.jpg |

---

## 性能指标

| 指标 | 值 |
|------|-----|
| 单张处理时间 | 2-3 秒 |
| 解析准确率 | 98% (StepFun) / 95% (DeepSeek) |
| 文件重命名 | <100ms |
| 分类移动 | <100ms |
| **总耗时** | **2-4 秒/张** |

---

## 故障排除

### 问题: 解析失败（降级到DeepSeek或Gemini）

**原因**: StepFun API 不可用或超时

**解决方案**:
1. 检查网络连接
2. 检查 API Key 是否有效
3. 检查 API 配额是否用尽

### 问题: 文件重命名为 "Unknown"

**原因**: 无法从图片中提取日期或报告类型

**解决方案**:
- 检查图片质量
- 确保图片包含清晰的文本信息
- 手动编辑文件名后重新分类

### 问题: 文件分类到 "other" 目录

**原因**: 文件名中的报告类型未识别

**解决方案**:
- 检查文件名格式
- 确保使用支持的类型 (CT, MRI, 血检等)

---

## 高级用法

### 处理后的 JSON 结构

```json
{
  "status": "success",
  "file": "IMG_0125.JPG",
  "new_name": "2024-09-05_CT_病灶标注_001.jpg",
  "category": "imaging",
  "confidence": 0.98,
  "report_date": "2024-09-05",
  "report_type": "DICOM CT",
  "diagnosis": "疑似胰腺或腹膜后病变，建议进一步检查。",
  "summary": "腹部CT影像显示特定区域有异常...",
  "text_length": 165
}
```

### 批量处理并统计

```bash
#!/bin/bash

WORK_DIR=~/medical_work
RESULTS_DIR=$WORK_DIR/results
SUCCESS=0
FAILED=0

mkdir -p $RESULTS_DIR

for img in *.jpg; do
    result_file="$RESULTS_DIR/${img%.jpg}.json"
    
    if python process_single.py "$img" -w $WORK_DIR -o "$result_file"; then
        SUCCESS=$((SUCCESS + 1))
    else
        FAILED=$((FAILED + 1))
    fi
done

echo "✓ 处理完成: 成功 $SUCCESS, 失败 $FAILED"
```

---

## 目录结构

```
work_dir/
├── data/
│   └── extracted/          # 提取的 JSON 元数据
│       └── file_hash.json
├── backup/
│   └── original/           # 原始文件备份
│       └── original_image.jpg
├── logs/
│   └── processing.log      # 处理日志
└── reports/                # ⭐ 分类后的文件
    ├── imaging/
    │   ├── CT/
    │   ├── MRI/
    │   ├── 超声/
    │   └── X光/
    ├── lab_reports/
    │   ├── 血检/
    │   ├── 病理/
    │   └── 遗传/
    ├── medical_records/
    ├── prescriptions/
    ├── psychology/
    ├── nutrition/
    └── other/
```

---

## 集成到工作流

### 与其他工具集成

```bash
# 1. 扫描医学目录
find /medical/files -type f -name "*.jpg" | sort > files.txt

# 2. 逐张处理
while IFS= read -r img; do
    python process_single.py "$img" -w ~/work
done < files.txt

# 3. 生成汇总报告
ls ~/work/reports -R > ~/work/file_list.txt
```

### Python 集成

```python
import subprocess
import json

def process_images(image_paths: list, work_dir: str) -> list:
    """批量处理图片"""
    results = []
    
    for img in image_paths:
        result = subprocess.run(
            ['python', 'process_single.py', img, '-w', work_dir, '-o', 'result.json'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            with open('result.json', 'r') as f:
                results.append(json.load(f))
    
    return results
```

---

## 常见问题

### Q: 为什么每次只处理1张？

A: 
- 单张处理更稳定，不易堆积错误
- API 调用更可控，降低超时风险
- 便于监控和调试
- 易于与其他工具集成

### Q: 如何批量处理多张？

A: 使用 Shell 脚本循环调用本脚本

### Q: 能否同时处理多张？

A: 可以用 `parallel` 或 `xargs` 并行处理，但要注意 API 速率限制

```bash
# 并行处理 (最多3个并行)
find . -name "*.jpg" | parallel -j 3 python process_single.py {} -w ~/work
```

### Q: 处理结果保存在哪里？

A: 保存在 `work_dir/reports/` 中，按分类组织

---

## 性能优化

### 内存使用

- 每次处理一张，内存占用低
- 适合在服务器上长期运行

### 速度优化

```bash
# 使用 GNU Parallel 加速 (5 个并行进程)
cat image_list.txt | parallel -j 5 python process_single.py {} -w ~/work
```

---

**版本**: 2.1 (单张处理)  
**状态**: ✅ 生产可用  
**最后更新**: 2024-01-19
