"""JSON 汇总与聚合模块 (v2.0)

根据提取结果生成患者汇总 JSON
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class JsonAggregator:
    """JSON 汇总器"""
    
    def __init__(self, data_dir: str):
        """初始化聚合器
        
        Args:
            data_dir: 数据目录 (包含提取的 JSON 文件)
        """
        self.data_dir = data_dir
        self.individual_results = []
        self.patient_summary = {}
        
        logger.info("✓ JsonAggregator 初始化完成")
    
    def load_all_json(self) -> List[dict]:
        """加载所有提取的 JSON 文件
        
        Returns:
            List[dict]: JSON 对象列表
        """
        json_files = list(Path(self.data_dir).glob("*.json"))
        
        logger.info(f"\n加载 {len(json_files)} 个 JSON 文件...\n")
        
        for json_file in sorted(json_files):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.individual_results.append(data)
                    logger.debug(f"  加载: {json_file.name}")
            except Exception as e:
                logger.error(f"  加载失败 {json_file.name}: {e}")
        
        logger.info(f"✓ 加载完成: {len(self.individual_results)} 个")
        return self.individual_results
    
    def _build_timeline(self) -> Dict[str, List[dict]]:
        """按时间轴组织文件
        
        Returns:
            Dict[str, List[dict]]: {日期: 文件列表}
        """
        timeline = defaultdict(list)
        
        for result in self.individual_results:
            extraction = result.get('extraction_result', {})
            raw_data = extraction.get('raw_data', {})
            date = raw_data.get('report_date', 'Unknown')
            
            timeline[date].append({
                'original_name': result['metadata']['original_name'],
                'file_hash': result['metadata']['file_hash'],
                'report_type': raw_data.get('report_type', 'Unknown'),
                'confidence': extraction.get('confidence', 0),
            })
        
        # 按日期排序
        return {k: timeline[k] for k in sorted(timeline.keys(), reverse=True)}
    
    def _build_by_type(self) -> Dict[str, List[dict]]:
        """按报告类型分组
        
        Returns:
            Dict[str, List[dict]]: {报告类型: 文件列表}
        """
        by_type = defaultdict(list)
        
        for result in self.individual_results:
            extraction = result.get('extraction_result', {})
            raw_data = extraction.get('raw_data', {})
            report_type = raw_data.get('report_type', 'Unknown')
            
            by_type[report_type].append({
                'original_name': result['metadata']['original_name'],
                'file_hash': result['metadata']['file_hash'],
                'report_date': raw_data.get('report_date', 'Unknown'),
                'confidence': extraction.get('confidence', 0),
                'diagnosis': raw_data.get('diagnosis', ''),
            })
        
        # 按类型排序
        return {k: by_type[k] for k in sorted(by_type.keys())}
    
    def _build_stats(self) -> dict:
        """统计信息
        
        Returns:
            dict: 统计数据
        """
        type_count = defaultdict(int)
        total_text_length = 0
        avg_confidence = 0
        confidence_count = 0
        
        for result in self.individual_results:
            extraction = result.get('extraction_result', {})
            raw_data = extraction.get('raw_data', {})
            
            # 统计类型
            report_type = raw_data.get('report_type', 'Unknown')
            type_count[report_type] += 1
            
            # 统计文本长度
            text_len = extraction.get('text_length', 0)
            total_text_length += text_len
            
            # 统计置信度
            confidence = extraction.get('confidence', 0)
            avg_confidence += confidence
            confidence_count += 1
        
        avg_confidence = (
            avg_confidence / confidence_count 
            if confidence_count > 0 
            else 0
        )
        
        return {
            'total_files': len(self.individual_results),
            'files_by_type': dict(sorted(type_count.items())),
            'total_text_length': total_text_length,
            'avg_text_length': (
                total_text_length // len(self.individual_results)
                if self.individual_results else 0
            ),
            'average_confidence': round(avg_confidence, 3),
        }
    
    def build_patient_summary(self) -> dict:
        """构建患者汇总
        
        Returns:
            dict: 患者信息汇总
        """
        logger.info(f"\n构建患者汇总...\n")
        
        self.patient_summary = {
            "metadata": {
                "date_processed": datetime.now().isoformat(),
                "total_files": len(self.individual_results),
            },
            "timeline": self._build_timeline(),
            "by_type": self._build_by_type(),
            "summary_stats": self._build_stats(),
            "all_files": [
                {
                    'original_name': r['metadata']['original_name'],
                    'file_hash': r['metadata']['file_hash'],
                    'extraction': r.get('extraction_result', {}),
                }
                for r in self.individual_results
            ]
        }
        
        logger.info(f"✓ 汇总构建完成")
        logger.info(f"  总文件数: {self.patient_summary['metadata']['total_files']}")
        logger.info(f"  报告类型: {len(self.patient_summary['by_type'])} 种")
        logger.info(f"  平均置信度: {self.patient_summary['summary_stats']['average_confidence']:.2f}")
        
        return self.patient_summary
    
    def save_patient_summary(self, output_path: str):
        """保存患者汇总 JSON
        
        Args:
            output_path: 输出文件路径
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    self.patient_summary,
                    f,
                    ensure_ascii=False,
                    indent=2,
                    default=str
                )
            logger.info(f"✓ 患者汇总已保存: {output_path}")
        except Exception as e:
            logger.error(f"✗ 保存失败: {e}")
    
    def get_files_by_date(self, date: str) -> List[dict]:
        """获取特定日期的所有文件
        
        Args:
            date: 日期 (YYYY-MM-DD)
        
        Returns:
            List[dict]: 文件列表
        """
        return self.patient_summary.get('timeline', {}).get(date, [])
    
    def get_files_by_type(self, report_type: str) -> List[dict]:
        """获取特定类型的所有文件
        
        Args:
            report_type: 报告类型
        
        Returns:
            List[dict]: 文件列表
        """
        return self.patient_summary.get('by_type', {}).get(report_type, [])
    
    def print_summary(self):
        """打印汇总信息"""
        if not self.patient_summary:
            logger.info("✗ 尚未构建汇总，请先调用 build_patient_summary()")
            return
        
        logger.info("\n" + "="*70)
        logger.info("患者信息汇总")
        logger.info("="*70)
        
        metadata = self.patient_summary.get('metadata', {})
        logger.info(f"\n处理时间: {metadata.get('date_processed', 'N/A')}")
        logger.info(f"总文件数: {metadata.get('total_files', 0)}")
        
        stats = self.patient_summary.get('summary_stats', {})
        logger.info(f"\n统计信息:")
        logger.info(f"  报告类型数: {len(self.patient_summary.get('by_type', {}))}")
        logger.info(f"  平均置信度: {stats.get('average_confidence', 0):.2f}")
        logger.info(f"  总文本字数: {stats.get('total_text_length', 0):,}")
        
        by_type = self.patient_summary.get('by_type', {})
        logger.info(f"\n按类型分类:")
        for report_type, files in sorted(by_type.items()):
            logger.info(f"  {report_type}: {len(files)} 个文件")
        
        timeline = self.patient_summary.get('timeline', {})
        logger.info(f"\n时间轴 (最近):")
        for date, files in list(timeline.items())[:5]:
            logger.info(f"  {date}: {len(files)} 个文件")
        
        logger.info("\n" + "="*70)
