"""文件类型JSON记录器

记录文件分类结果到JSON文件
参考: DEVELOPMENT_PLAN.md § 2.0.2
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import asdict
from src.file_handler.content_classifier import ClassificationResult


class FileTypeRecorder:
    """记录文件分类结果到JSON
    
    生成 file_types.json 文件，记录每个文件的分类信息
    """
    
    def __init__(self, output_dir: str = "."):
        """
        初始化记录器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        self.json_path = os.path.join(output_dir, "file_types.json")
        self.records: Dict[str, Dict] = {}
        
        # 加载已有记录
        self._load_existing_records()
    
    def _load_existing_records(self):
        """加载已有的分类记录"""
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    self.records = json.load(f)
                print(f"✓ 加载已有记录: {len(self.records)} 个文件")
            except Exception as e:
                print(f"⚠️  加载记录失败: {e}")
                self.records = {}
        else:
            self.records = {}
    
    def record(self, filename: str, result: ClassificationResult, 
               extraction_method: str = "unknown"):
        """
        记录单个文件的分类结果
        
        Args:
            filename: 文件名
            result: 分类结果
            extraction_method: 内容提取方法
        """
        self.records[filename] = {
            "category": result.category.value,
            "confidence": round(result.confidence, 3),
            "keywords_found": result.keywords_found[:10],  # 最多记录10个关键词
            "extraction_method": extraction_method,
            "classification_method": result.method,
            "reasoning": result.reasoning,
            "classified_at": datetime.now().isoformat()
        }
    
    def record_batch(self, results: List[tuple]):
        """
        批量记录分类结果
        
        Args:
            results: [(filename, ClassificationResult, extraction_method), ...]
        """
        for filename, result, extraction_method in results:
            self.record(filename, result, extraction_method)
    
    def save(self):
        """保存记录到JSON文件"""
        try:
            # 确保目录存在
            os.makedirs(self.output_dir, exist_ok=True)
            
            # 保存JSON
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 分类记录已保存: {self.json_path} ({len(self.records)} 个文件)")
        except Exception as e:
            print(f"❌ 保存记录失败: {e}")
    
    def get_record(self, filename: str) -> Optional[Dict]:
        """
        获取指定文件的记录
        
        Args:
            filename: 文件名
            
        Returns:
            Dict or None: 分类记录
        """
        return self.records.get(filename)
    
    def get_by_category(self, category: str) -> List[str]:
        """
        获取指定分类的所有文件
        
        Args:
            category: 分类名称
            
        Returns:
            List[str]: 文件名列表
        """
        return [
            filename for filename, record in self.records.items()
            if record.get("category") == category
        ]
    
    def get_low_confidence_files(self, threshold: float = 0.5) -> List[tuple]:
        """
        获取低置信度的文件
        
        Args:
            threshold: 置信度阈值
            
        Returns:
            List[tuple]: [(filename, confidence, category), ...]
        """
        low_confidence = []
        for filename, record in self.records.items():
            confidence = record.get("confidence", 0.0)
            if confidence < threshold:
                low_confidence.append((
                    filename,
                    confidence,
                    record.get("category", "unknown")
                ))
        
        # 按置信度排序
        low_confidence.sort(key=lambda x: x[1])
        return low_confidence
    
    def get_statistics(self) -> Dict:
        """
        获取分类统计信息
        
        Returns:
            Dict: 统计信息
        """
        stats = {
            "total_files": len(self.records),
            "by_category": {},
            "by_confidence": {
                "high (≥0.85)": 0,
                "medium (0.5-0.85)": 0,
                "low (<0.5)": 0
            },
            "by_method": {}
        }
        
        for record in self.records.values():
            # 按分类统计
            category = record.get("category", "unknown")
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            # 按置信度统计
            confidence = record.get("confidence", 0.0)
            if confidence >= 0.85:
                stats["by_confidence"]["high (≥0.85)"] += 1
            elif confidence >= 0.5:
                stats["by_confidence"]["medium (0.5-0.85)"] += 1
            else:
                stats["by_confidence"]["low (<0.5)"] += 1
            
            # 按方法统计
            method = record.get("classification_method", "unknown")
            stats["by_method"][method] = stats["by_method"].get(method, 0) + 1
        
        return stats
    
    def print_summary(self):
        """打印分类摘要"""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("文件分类统计")
        print("="*60)
        print(f"总文件数: {stats['total_files']}")
        
        print("\n按分类统计:")
        for category, count in sorted(stats['by_category'].items(), 
                                      key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count}")
        
        print("\n按置信度统计:")
        for level, count in stats['by_confidence'].items():
            print(f"  {level}: {count}")
        
        print("\n按方法统计:")
        for method, count in stats['by_method'].items():
            print(f"  {method}: {count}")
        
        # 显示低置信度文件
        low_conf = self.get_low_confidence_files(0.5)
        if low_conf:
            print(f"\n⚠️  低置信度文件 ({len(low_conf)} 个):")
            for filename, conf, category in low_conf[:10]:
                print(f"  {filename}: {conf:.2f} ({category})")
            if len(low_conf) > 10:
                print(f"  ... 还有 {len(low_conf) - 10} 个")
        
        print("="*60 + "\n")
    
    def update_record(self, filename: str, updates: Dict):
        """
        更新指定文件的记录（用于人工校正）
        
        Args:
            filename: 文件名
            updates: 更新的字段
        """
        if filename in self.records:
            self.records[filename].update(updates)
            self.records[filename]["updated_at"] = datetime.now().isoformat()
            print(f"✓ 已更新记录: {filename}")
        else:
            print(f"⚠️  文件不存在: {filename}")
    
    def export_to_csv(self, csv_path: str = None):
        """
        导出为CSV格式
        
        Args:
            csv_path: CSV文件路径（默认为同目录下的file_types.csv）
        """
        if csv_path is None:
            csv_path = os.path.join(self.output_dir, "file_types.csv")
        
        try:
            import csv
            
            with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                
                # 写入表头
                writer.writerow([
                    "文件名", "分类", "置信度", "关键词数量", 
                    "提取方法", "分类方法", "分类时间"
                ])
                
                # 写入数据
                for filename, record in self.records.items():
                    writer.writerow([
                        filename,
                        record.get("category", ""),
                        record.get("confidence", 0.0),
                        len(record.get("keywords_found", [])),
                        record.get("extraction_method", ""),
                        record.get("classification_method", ""),
                        record.get("classified_at", "")
                    ])
            
            print(f"✓ CSV导出成功: {csv_path}")
        except Exception as e:
            print(f"❌ CSV导出失败: {e}")
