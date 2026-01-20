# Scripts 目录说明

本目录包含项目使用的脚本文件，分为活跃脚本和历史脚本。

## 📂 目录结构

### 根目录 (活跃脚本)
项目主要使用的脚本

- ❌ **process_single.py** - 单张医学图片处理 (v2.1 已修复)
  - 流程: 扫描 → 解析 → JSON → 重命名 → 分类 → 分析 → 报告
  - 使用: `python process_single.py image.jpg -w /work/dir`
  - 新增: `--report` / `--no-report` 选项

### legacy/ (废弃脚本)
历史开发过程中使用过但已被替代的脚本

| 脚本 | 原用途 | 替代方案 | 原因 |
|------|--------|---------|------|
| `test_*.py` (4个) | 单元测试 | src/tests/ | 测试模块已集成 |
| `list_models.py` | 列出模型 | 已过时 | API服务变更 |
| `parse_single_image.py` | 单图解析 | process_single.py | 功能已集成 |
| `process_batch.py` | 批量处理 | process_single.py loop | 已整合到主脚本 |
| `process_patient_files.py` | 患者文件处理 | ProcessCoordinator | 已集成到协调器 |

**保留原因**: 
- 用于版本控制和历史追溯
- 某些功能片段可参考
- 后续可用于对比测试

### tools/ (工具脚本)
未来用于存放辅助工具脚本

**规划工具** (需后续开发):
- `generate_report.py` - 报告生成工具
- `export_data.py` - 数据导出工具
- `migrate_data.py` - 数据迁移工具
- `backup_patient_data.py` - 患者数据备份

## 🚀 使用指南

### 运行主脚本
```bash
# 1. 基本使用 (包含报告生成)
python process_single.py medical_report.jpg -w /work/dir

# 2. 仅做文件处理
python process_single.py medical_report.jpg -w /work/dir --no-report

# 3. 保存结果为JSON
python process_single.py medical_report.jpg -w /work/dir -o result.json

# 4. 查看帮助
python process_single.py -h
```

### 查看废弃脚本
```bash
# 查看历史脚本列表
ls scripts/legacy/

# 查看特定脚本
cat scripts/legacy/parse_single_image.py

# 参考历史实现
grep -r "特定功能" scripts/legacy/
```

## 📊 脚本统计

- **活跃脚本**: 1 个 (process_single.py)
- **废弃脚本**: 8 个 (scripts/legacy/)
- **工具脚本**: 0 个 (规划中, scripts/tools/)

## 🔄 脚本演进历史

```
parse_single_image.py (v1)
    ↓ 功能扩展
process_single.py (v1) → process_batch.py (v2)
    ↓ 重新设计
process_single.py (v2) [现在: 包含完整6步流程]
    ↓ 后续
process_single.py (v2.1+) [计划: 添加Web发布功能]
```

## ⚠️ 废弃脚本注意事项

- **不应直接使用**: legacy/ 中的脚本已被替代
- **可作为参考**: 某些实现细节可参考
- **保留时限**: 建议保留1年后评估是否删除
- **归档时间**: 2026-01-20

## 🎯 后续规划

### 短期 (1个月内)
- [ ] 补充单元测试 (tests/ 目录)
- [ ] 创建集成测试脚本

### 中期 (3个月内)
- [ ] 开发 tools/ 目录中的工具脚本
- [ ] 添加数据导入导出工具
- [ ] 创建数据迁移脚本

### 长期 (6个月+)
- [ ] 清理legacy脚本 (如无需要)
- [ ] 模块化脚本设计
- [ ] CLI工具统一框架

## 📝 添加新脚本指南

1. **新功能脚本**: 放在根目录
2. **辅助工具**: 放在 tools/ 目录
3. **测试脚本**: 放在 src/tests/ 目录
4. **备份脚本**: 放在 legacy/ 目录

### 脚本模板
```python
#!/usr/bin/env python3
"""脚本说明

用途: 简述脚本功能
用法: python script.py [选项]
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def main():
    """主函数"""
    pass

if __name__ == '__main__':
    sys.exit(main())
```

## 🔗 相关资源

- **主脚本文档**: 见 `docs/guides/` 中的指南
- **源代码**: 见 `src/` 目录
- **开发记录**: 见 `records/` 目录

## 版本信息

- **最后更新**: 2026-01-20
- **废弃脚本版本**: v1 - v2
- **当前活跃版本**: v2.1
- **维护者**: Skill Report Genie Team
