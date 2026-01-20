# 医学文件处理系统 - 实现规范 (v2.0)

**版本**: 2.0  
**日期**: 2024-01-19  
**状态**: 设计阶段完成，等待实现

---

## 核心模块设计

### 模块 1: 文件扫描与解析 (`file_processor.py`)

```python
class FileProcessor:
    """统一的文件扫描与解析器"""
    
    def __init__(self, input_dir: str):
        """初始化"""
        self.input_dir = input_dir
        self.output_dir = f"{input_dir}/data/extracted"
        self.backup_dir = f"{input_dir}/backup/original"
        self.parser = parse_single_image  # 使用已有的解析工具
    
    def scan_directory(self) -> List[str]:
        """扫描目录获取所有文件
        
        Returns:
            List[str]: 文件路径列表
        """
        # 实现细节...
    
    def process_all_files(self) -> Dict[str, FileParseResult]:
        """逐个处理所有文件
        
        Returns:
            Dict[str, FileParseResult]: 文件路径 -> 解析结果
        """
        results = {}
        
        for file_path in self.scan_directory():
            try:
                # 调用 parse_single_image
                result = self.parser(file_path)
                results[file_path] = result
                
                # 保存 JSON
                self._save_extraction_json(file_path, result)
                
                logger.info(f"✓ 解析完成: {file_path}")
            except Exception as e:
                logger.error(f"✗ 解析失败: {file_path}: {e}")
                results[file_path] = None
        
        return results
    
    def _save_extraction_json(self, file_path: str, result: dict):
        """保存提取结果 JSON"""
        # 实现细节...
```

### 模块 2: 文件重命名 (`file_renamer.py`)

```python
class FileRenamer:
    """标准化文件重命名"""
    
    NAMING_PATTERN = "{date}_{type}_{digest}_{sequence:03d}.{ext}"
    
    TYPE_MAPPING = {
        # 映射报告类型到标准类型
        "DICOM CT": "CT",
        "CT影像": "CT",
        "CT scan": "CT",
        # ... 更多映射
    }
    
    def __init__(self, backup_dir: str):
        self.backup_dir = backup_dir
        self.mapping = {}  # 原始名 -> 新名
    
    def rename_file(self, 
                   file_path: str,
                   extraction_result: dict) -> str:
        """重命名单个文件
        
        Args:
            file_path: 原始文件路径
            extraction_result: 提取的结构化数据
        
        Returns:
            str: 新文件名
        """
        # 提取信息
        date = extraction_result['report_date']  # YYYY-MM-DD
        report_type = extraction_result['report_type']
        diagnosis = extraction_result['diagnosis']
        
        # 标准化类型
        std_type = self.TYPE_MAPPING.get(
            report_type, 
            report_type[:2] if report_type else "Other"
        )
        
        # 生成摘要 (从诊断中提取关键词)
        digest = self._generate_digest(diagnosis)
        
        # 获取序列号
        sequence = self._get_sequence_number(date, std_type)
        
        # 生成新名
        ext = os.path.splitext(file_path)[1].lstrip('.')
        new_name = self.NAMING_PATTERN.format(
            date=date,
            type=std_type,
            digest=digest,
            sequence=sequence,
            ext=ext.lower()
        )
        
        # 备份原文件
        self._backup_original(file_path, new_name)
        
        # 记录映射
        self.mapping[os.path.basename(file_path)] = new_name
        
        return new_name
    
    def _generate_digest(self, diagnosis: str) -> str:
        """从诊断生成摘要
        
        Examples:
            "疑似胰腺癌，建议进一步检查"
            → "胰腺癌建议"
        """
        # 实现细节...
    
    def _get_sequence_number(self, date: str, doc_type: str) -> int:
        """获取同日期同类型文件的序列号"""
        # 实现细节...
    
    def _backup_original(self, src: str, new_name: str):
        """备份原始文件，记录映射"""
        # 实现细节...
    
    def get_mapping(self) -> Dict[str, str]:
        """获取文件名映射关系"""
        return self.mapping

    def save_mapping_log(self, output_path: str):
        """保存映射日志，用于恢复"""
        # 实现细节...
```

### 模块 3: JSON 汇总 (`json_aggregator.py`)

```python
class JsonAggregator:
    """汇总所有提取结果"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.individual_results = []
        self.patient_summary = {}
    
    def load_all_json(self) -> List[dict]:
        """加载所有提取的 JSON 文件"""
        # 实现细节...
    
    def build_patient_summary(self) -> dict:
        """构建患者汇总
        
        Returns:
            dict: 患者信息汇总
            {
                "metadata": {
                    "date_processed": "...",
                    "total_files": 50,
                },
                "timeline": {
                    "2024-09-05": [...],
                    "2023-06-27": [...],
                },
                "by_type": {
                    "imaging": [...],
                    "lab": [...],
                },
                "all_files": [...]
            }
        """
        summary = {
            "metadata": {
                "date_processed": datetime.now().isoformat(),
                "total_files": len(self.individual_results),
                "files_by_category": self._count_by_category(),
            },
            "timeline": self._build_timeline(),
            "by_type": self._build_by_type(),
            "summary_stats": self._build_stats(),
            "all_files": self.individual_results,
        }
        return summary
    
    def _build_timeline(self) -> Dict[str, List]:
        """按时间轴组织文件"""
        # 实现细节...
    
    def _build_by_type(self) -> Dict[str, List]:
        """按类型分组"""
        # 实现细节...
    
    def _build_stats(self) -> dict:
        """统计信息"""
        # 实现细节...
    
    def save_patient_summary(self, output_path: str):
        """保存患者汇总 JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.patient_summary, f, 
                     ensure_ascii=False, indent=2)
```

### 模块 4: 文件分类与组织 (`file_organizer.py`)

```python
class FileOrganizer:
    """基于文件名的文件分类与组织"""
    
    DIRECTORY_STRUCTURE = {
        "imaging": {
            "CT": "CT扫描",
            "MRI": "核磁共振",
            "ultrasound": "超声检查",
            "xray": "X光检查",
        },
        "lab_reports": {
            "blood": "血液检验",
            "pathology": "病理诊断",
            "genetic": "基因检测",
        },
        "medical_records": "病历记录",
        "prescriptions": "处方用药",
        "psychology": "心理支持",
        "nutrition": "营养管理",
        "other": "其他文件",
    }
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.reports_dir = os.path.join(base_dir, "reports")
    
    def classify_by_filename(self, filename: str) -> Tuple[str, str]:
        """从文件名提取分类信息
        
        文件名格式: <date>_<type>_<digest>_<sequence>.<ext>
        
        Args:
            filename: 标准化文件名
        
        Returns:
            (category, subcategory): 分类和子分类
            
        Examples:
            "2024-09-05_CT_病灶标注_001.jpg"
            → ("imaging", "CT")
            
            "2023-06-27_血检_肿瘤标志物_001.jpg"
            → ("lab_reports", "blood")
        """
        # 解析文件名
        parts = filename.rsplit('_', 2)  # 分离 序列 和 扩展名
        if len(parts) < 3:
            return ("other", "uncategorized")
        
        date_type = parts[0].rsplit('_', 1)
        date = date_type[0]
        type_str = date_type[1] if len(date_type) > 1 else ""
        
        # 分类映射
        category_map = {
            "CT": ("imaging", "CT"),
            "MRI": ("imaging", "MRI"),
            "超声": ("imaging", "ultrasound"),
            "X光": ("imaging", "xray"),
            "血检": ("lab_reports", "blood"),
            "病理": ("lab_reports", "pathology"),
            "遗传": ("lab_reports", "genetic"),
            "病历": ("medical_records", "medical_records"),
            "处方": ("prescriptions", "prescriptions"),
            "心理": ("psychology", "psychology"),
            "营养": ("nutrition", "nutrition"),
        }
        
        return category_map.get(type_str, ("other", "other"))
    
    def create_directory_structure(self):
        """创建标准目录结构"""
        for category, subcats in self.DIRECTORY_STRUCTURE.items():
            if isinstance(subcats, dict):
                for subcat in subcats:
                    path = os.path.join(
                        self.reports_dir, category, subcat
                    )
                    os.makedirs(path, exist_ok=True)
            else:
                path = os.path.join(self.reports_dir, category)
                os.makedirs(path, exist_ok=True)
        
        logger.info(f"✓ 目录结构已创建: {self.reports_dir}")
    
    def organize_files(self, 
                      files_to_move: Dict[str, str]):
        """组织文件
        
        Args:
            files_to_move: {原始路径: 新文件名}
        """
        for src_path, new_name in files_to_move.items():
            category, subcat = self.classify_by_filename(new_name)
            
            if subcat == "uncategorized":
                dest_dir = os.path.join(self.reports_dir, "other")
            elif category in ["medical_records", "prescriptions", 
                             "psychology", "nutrition"]:
                dest_dir = os.path.join(self.reports_dir, category)
            else:
                dest_dir = os.path.join(
                    self.reports_dir, category, subcat
                )
            
            # 移动文件和对应的 JSON
            self._move_file_with_json(
                src_path, new_name, dest_dir
            )
    
    def _move_file_with_json(self, src: str, new_name: str, dest_dir: str):
        """移动文件及其 JSON 数据"""
        # 实现细节...
        pass
```

### 模块 5: 主控制器 (`process_coordinator.py`)

```python
class ProcessCoordinator:
    """协调整个处理流程"""
    
    def __init__(self, input_dir: str):
        self.input_dir = input_dir
        self.processor = FileProcessor(input_dir)
        self.renamer = FileRenamer(f"{input_dir}/backup/original")
        self.aggregator = JsonAggregator(f"{input_dir}/data/extracted")
        self.organizer = FileOrganizer(input_dir)
    
    def run_full_pipeline(self) -> dict:
        """执行完整处理流程"""
        
        logger.info("="*70)
        logger.info("开始处理患者文件...")
        logger.info("="*70)
        
        # 第一步: 扫描并解析
        logger.info("\n[1/5] 扫描并解析文件...")
        parse_results = self.processor.process_all_files()
        successful = sum(1 for r in parse_results.values() if r)
        logger.info(f"✓ 解析完成: {successful}/{len(parse_results)}")
        
        # 第二步: 重命名
        logger.info("\n[2/5] 重命名文件...")
        files_to_move = {}
        for file_path, result in parse_results.items():
            if result:
                new_name = self.renamer.rename_file(
                    file_path, result
                )
                files_to_move[file_path] = new_name
        logger.info(f"✓ 重命名完成: {len(files_to_move)}")
        self.renamer.save_mapping_log(
            f"{self.input_dir}/logs/rename_mapping.log"
        )
        
        # 第三步: 汇总 JSON
        logger.info("\n[3/5] 生成数据汇总...")
        self.aggregator.load_all_json()
        summary = self.aggregator.build_patient_summary()
        self.aggregator.save_patient_summary(
            f"{self.input_dir}/data/patient_summary.json"
        )
        logger.info(f"✓ 汇总完成: {summary['metadata']['total_files']} 个文件")
        
        # 第四步: 创建目录
        logger.info("\n[4/5] 创建分类目录...")
        self.organizer.create_directory_structure()
        logger.info("✓ 目录创建完成")
        
        # 第五步: 分类移动
        logger.info("\n[5/5] 分类并移动文件...")
        self.organizer.organize_files(files_to_move)
        logger.info(f"✓ 文件分类完成")
        
        # 生成报告
        logger.info("\n" + "="*70)
        logger.info("处理完成！")
        logger.info("="*70)
        
        return {
            "status": "success",
            "total_files": len(parse_results),
            "successful": successful,
            "summary": summary,
        }
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

### 字段说明

| 字段 | 格式 | 说明 | 示例 |
|------|------|------|------|
| date | YYYY-MM-DD | 报告日期 | 2024-09-05 |
| type | 2-4字 | 报告类型 | CT, MRI, 血检, 病理 |
| digest | 任意 | 内容摘要 | 病灶标注, 肿瘤标志物 |
| sequence | 3位数 | 序列号 | 001, 002, ... |
| ext | 小写 | 扩展名 | jpg, pdf, json |

---

## JSON 结构规范

### 单个文件 JSON

```json
{
  "metadata": {
    "original_name": "IMG_0125.JPG",
    "standard_name": "2024-09-05_CT_病灶标注_001.jpg",
    "file_hash": "abc123...",
    "processed_time": "2024-01-19T10:30:00Z"
  },
  "extraction_result": {
    "confidence": 0.98,
    "report_date": "2024-09-05",
    "report_type": "DICOM CT",
    "diagnosis": "疑似胰腺或腹膜后病变",
    "summary": "腹部CT显示特定区域有异常...",
    "indicators": [],
    "findings": "腹部横断面CT图像..."
  }
}
```

### 患者汇总 JSON

```json
{
  "metadata": {
    "date_processed": "2024-01-19T10:30:00Z",
    "total_files": 50,
    "files_by_category": {
      "imaging": 15,
      "lab_reports": 20,
      "medical_records": 10,
      "other": 5
    }
  },
  "timeline": {
    "2024-09-05": [...],
    "2023-06-27": [...]
  },
  "by_type": {
    "imaging": {...},
    "lab_reports": {...}
  },
  "summary_stats": {...},
  "all_files": [...]
}
```

---

## 入口脚本

```python
# scripts/process_patient_files.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processing.process_coordinator import ProcessCoordinator

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='处理患者混乱的医学文件'
    )
    parser.add_argument('input_dir', 
                       help='包含医学文件的目录')
    parser.add_argument('-o', '--output', 
                       help='输出目录 (默认: input_dir/reports)',
                       default=None)
    
    args = parser.parse_args()
    
    coordinator = ProcessCoordinator(args.input_dir)
    result = coordinator.run_full_pipeline()
    
    print(f"\n结果: {result['successful']}/{result['total_files']} 成功")
    
    return 0 if result['status'] == 'success' else 1

if __name__ == '__main__':
    sys.exit(main())
```

---

## 使用示例

```bash
# 基本用法
python scripts/process_patient_files.py /path/to/messy/files

# 输出
[1/5] 扫描并解析文件...
  检测到 50 个文件
  ✓ 解析完成: 50/50

[2/5] 重命名文件...
  ✓ 重命名完成: 50

[3/5] 生成数据汇总...
  ✓ 汇总完成: 50 个文件

[4/5] 创建分类目录...
  ✓ 目录创建完成

[5/5] 分类并移动文件...
  ✓ 文件分类完成

处理完成！
成功率: 100% (50/50)
```

---

**版本**: 2.0  
**状态**: 设计完成，等待实现
