"""文件分类与组织模块 (v2.0)

根据标准化文件名进行分类，创建目录结构并移动文件
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class FileOrganizer:
    """文件分类与组织器"""
    
    # 目录结构定义
    DIRECTORY_STRUCTURE = {
        "imaging": {
            "CT": "CT扫描",
            "MRI": "核磁共振",
            "超声": "超声检查",
            "X光": "X光检查",
            "PET-CT": "PET-CT",
        },
        "lab_reports": {
            "血检": "血液检验",
            "病理": "病理诊断",
            "遗传": "基因检测",
        },
        "medical_records": "病历记录",
        "prescriptions": "处方用药",
        "psychology": "心理支持",
        "nutrition": "营养管理",
        "other": "其他文件",
    }
    
    def __init__(self, base_dir: str):
        """初始化分类器
        
        Args:
            base_dir: 基础目录
        """
        self.base_dir = base_dir
        self.reports_dir = os.path.join(base_dir, "reports")
        
        logger.info("✓ FileOrganizer 初始化完成")
    
    def classify_by_filename(self, filename: str) -> Tuple[str, str]:
        """从文件名提取分类信息
        
        文件名格式: <date>_<type>_<digest>_<sequence>.<ext>
        例如: 2024-01-15_血检_test_001.jpg
        
        Args:
            filename: 标准化文件名
        
        Returns:
            Tuple[str, str]: (category, subcategory)
        """
        # 分离扩展名
        name_part = filename.rsplit('.', 1)[0]
        parts = name_part.split('_')
        
        # 需要至少: date(可能含下划线，如2024-01-15) + type + digest + sequence
        if len(parts) < 4:
            return ("other", "other")
        
        # 日期格式: YYYY-MM-DD，一定在第一个位置
        # 类型在第二个位置
        type_str = parts[1]  # 这是 <type>
        
        # 分类映射
        category_map = {
            "CT": ("imaging", "CT"),
            "MRI": ("imaging", "MRI"),
            "超声": ("imaging", "超声"),
            "X光": ("imaging", "X光"),
            "PET-CT": ("imaging", "PET-CT"),
            
            "血检": ("lab_reports", "血检"),
            "病理": ("lab_reports", "病理"),
            "遗传": ("lab_reports", "遗传"),
            
            "病历": ("medical_records", "medical_records"),
            "处方": ("prescriptions", "prescriptions"),
            "心理": ("psychology", "psychology"),
            "营养": ("nutrition", "nutrition"),
        }
        
        result = category_map.get(type_str, ("other", "other"))
        logger.debug(f"  分类 '{filename}' → {result}")
        
        return result
    
    def create_directory_structure(self):
        """创建标准目录结构"""
        logger.info(f"\n创建目录结构...\n")
        
        count = 0
        for category, subcats in self.DIRECTORY_STRUCTURE.items():
            if isinstance(subcats, dict):
                # 有子分类
                for subcat, desc in subcats.items():
                    path = os.path.join(
                        self.reports_dir, category, subcat
                    )
                    os.makedirs(path, exist_ok=True)
                    logger.debug(f"  创建: {path}")
                    count += 1
            else:
                # 无子分类
                path = os.path.join(self.reports_dir, category)
                os.makedirs(path, exist_ok=True)
                logger.debug(f"  创建: {path}")
                count += 1
        
        logger.info(f"✓ 目录结构已创建: {self.reports_dir}")
        logger.info(f"  创建 {count} 个目录")
    
    def _get_destination_dir(self, 
                            category: str, 
                            subcat: str) -> str:
        """获取目标目录
        
        Args:
            category: 分类
            subcat: 子分类
        
        Returns:
            str: 目标目录路径
        """
        if subcat == "other" or category == "other":
            return os.path.join(self.reports_dir, "other")
        elif category in ["medical_records", "prescriptions", 
                         "psychology", "nutrition"]:
            return os.path.join(self.reports_dir, category)
        else:
            return os.path.join(self.reports_dir, category, subcat)
    
    def _move_file_with_data(self,
                            src_path: str,
                            new_name: str,
                            dest_dir: str) -> bool:
        """移动文件及其关联的 JSON 数据文件
        
        Args:
            src_path: 源文件路径
            new_name: 新文件名
            dest_dir: 目标目录
        
        Returns:
            bool: 是否成功
        """
        try:
            os.makedirs(dest_dir, exist_ok=True)
            
            # 目标路径
            dest_path = os.path.join(dest_dir, new_name)
            
            # 移动主文件
            if os.path.exists(src_path):
                shutil.move(src_path, dest_path)
                logger.debug(f"  移动: {os.path.basename(src_path)} → {dest_dir}")
            
            # 移动关联的 JSON (如果存在)
            src_dir = os.path.dirname(src_path)
            data_dir = os.path.join(src_dir, "..", "data", "extracted")
            
            if os.path.exists(data_dir):
                # 查找匹配的 JSON 文件
                for json_file in Path(data_dir).glob("*.json"):
                    # 这里可以根据 file_hash 或其他方式匹配
                    # 暂时简化处理：复制所有 JSON
                    dest_json_path = os.path.join(dest_dir, json_file.name)
                    if not os.path.exists(dest_json_path):
                        shutil.copy2(str(json_file), dest_json_path)
            
            return True
            
        except Exception as e:
            logger.error(f"  移动失败 {os.path.basename(src_path)}: {e}")
            return False
    
    def organize_files(self, 
                      files_to_move: Dict[str, str]) -> dict:
        """组织文件
        
        Args:
            files_to_move: {原始路径: 新文件名}
        
        Returns:
            dict: 组织结果统计
        """
        logger.info(f"\n组织文件到分类目录...\n")
        
        # 首先创建目录结构
        self.create_directory_structure()
        
        stats = {
            "total": len(files_to_move),
            "successful": 0,
            "failed": 0,
            "by_category": {},
        }
        
        for i, (src_path, new_name) in enumerate(files_to_move.items(), 1):
            
            # 分类
            category, subcat = self.classify_by_filename(new_name)
            
            # 获取目标目录
            dest_dir = self._get_destination_dir(category, subcat)
            
            # 移动文件
            if self._move_file_with_data(src_path, new_name, dest_dir):
                stats["successful"] += 1
                
                # 统计分类
                if category not in stats["by_category"]:
                    stats["by_category"][category] = {}
                if subcat not in stats["by_category"][category]:
                    stats["by_category"][category][subcat] = 0
                stats["by_category"][category][subcat] += 1
                
                logger.info(f"✓ {new_name} → {category}/{subcat}")
            else:
                stats["failed"] += 1
                logger.info(f"✗ {new_name}")
        
        # 输出统计
        logger.info(f"\n✓ 组织完成: {stats['successful']}/{stats['total']} 成功")
        logger.info(f"  失败: {stats['failed']}")
        
        if stats["by_category"]:
            logger.info(f"\n分类统计:")
            for category, subcats in stats["by_category"].items():
                total = sum(subcats.values())
                logger.info(f"  {category}: {total} 个")
                for subcat, count in subcats.items():
                    logger.info(f"    └─ {subcat}: {count} 个")
        
        return stats
    
    def print_directory_structure(self):
        """打印目录结构"""
        logger.info(f"\n目录结构:")
        logger.info(f"reports/")
        
        for root, dirs, files in os.walk(self.reports_dir):
            level = root.replace(self.reports_dir, '').count(os.sep)
            indent = ' ' * 2 * (level + 1)
            logger.info(f"{indent}{os.path.basename(root)}/")
            
            subindent = ' ' * 2 * (level + 2)
            for file in files[:5]:  # 只显示前5个文件
                logger.info(f"{subindent}{file}")
            
            if len(files) > 5:
                logger.info(f"{subindent}... 及 {len(files) - 5} 个文件")
