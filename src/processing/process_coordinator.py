"""主流程协调器 (v2.0)

协调整个文件处理流程：解析 → 重命名 → 汇总JSON → 分类移动
"""

import os
import logging
import json
from datetime import datetime
from typing import Dict

from src.processing.file_processor import FileProcessor
from src.processing.file_renamer import FileRenamer
from src.processing.json_aggregator import JsonAggregator
from src.processing.file_organizer import FileOrganizer
from src.reporting.report_generator import ReportGenerator

logger = logging.getLogger(__name__)


class ProcessCoordinator:
    """流程协调器"""
    
    def __init__(self, input_dir: str):
        """初始化协调器
        
        Args:
            input_dir: 输入目录
        """
        self.input_dir = input_dir
        
        # 初始化各个模块
        self.processor = FileProcessor(input_dir)
        self.renamer = FileRenamer(
            input_dir,
            os.path.join(input_dir, "backup", "original")
        )
        self.aggregator = JsonAggregator(
            os.path.join(input_dir, "data", "extracted")
        )
        self.organizer = FileOrganizer(input_dir)
        self.report_generator = ReportGenerator(
            output_dir=os.path.join(input_dir, "reports")
        )
        
        logger.info("✓ ProcessCoordinator 初始化完成\n")
    
    def run_full_pipeline(self) -> dict:
        """执行完整处理流程
        
        流程:
        1. 扫描并解析所有文件
        2. 基于内容重命名文件
        3. 汇总 JSON 数据
        4. 创建目录结构
        5. 分类移动文件
        6. 生成医学报告
        
        Returns:
            dict: 处理结果
        """
        start_time = datetime.now()
        
        logger.info("=" * 80)
        logger.info("开始处理患者医学文件 (v2.0)")
        logger.info("=" * 80)
        
        # ============ 第一步: 扫描并解析 ============
        logger.info("\n[1/5] 扫描并解析文件...")
        parse_results = self.processor.process_all_files()
        
        stats_1 = self.processor.get_success_stats(parse_results)
        logger.info(f"\n✓ 第一步完成:")
        logger.info(f"  总文件数: {stats_1['total']}")
        logger.info(f"  成功: {stats_1['successful']}")
        logger.info(f"  失败: {stats_1['failed']}")
        logger.info(f"  成功率: {stats_1['success_rate']:.1f}%")
        
        # 保存处理日志
        self.processor.save_processing_log(parse_results)
        
        # ============ 第二步: 重命名文件 ============
        logger.info("\n[2/5] 重命名文件...")
        files_to_move = self.renamer.rename_files_in_directory(parse_results)
        
        logger.info(f"\n✓ 第二步完成:")
        logger.info(f"  重命名文件数: {len(files_to_move)}")
        
        # 保存映射日志
        self.renamer.save_mapping_log(
            os.path.join(self.input_dir, "logs", "rename_mapping.log")
        )
        
        # ============ 第三步: 汇总 JSON ============
        logger.info("\n[3/5] 生成数据汇总...")
        self.aggregator.load_all_json()
        summary = self.aggregator.build_patient_summary()
        
        # 保存患者汇总
        summary_path = os.path.join(
            self.input_dir, "data", "patient_summary.json"
        )
        self.aggregator.save_patient_summary(summary_path)
        
        logger.info(f"\n✓ 第三步完成:")
        logger.info(f"  总文件数: {summary['metadata']['total_files']}")
        logger.info(f"  报告类型: {len(summary['by_type'])} 种")
        logger.info(f"  汇总文件: {summary_path}")
        
        # 打印汇总
        self.aggregator.print_summary()
        
        # ============ 第四步: 创建目录 ============
        logger.info("\n[4/5] 创建分类目录...")
        self.organizer.create_directory_structure()
        
        logger.info(f"✓ 第四步完成:")
        logger.info(f"  目录基础: {self.organizer.reports_dir}")
        
        # ============ 第五步: 分类移动 ============
        logger.info("\n[5/6] 分类并移动文件...")
        organize_stats = self.organizer.organize_files(files_to_move)
        
        logger.info(f"\n✓ 第五步完成:")
        logger.info(f"  成功移动: {organize_stats['successful']} 个")
        logger.info(f"  失败: {organize_stats['failed']} 个")
        
        # ============ 第六步: 生成医学报告 ============
        logger.info("\n[6/6] 生成医学报告...")
        try:
            reports = self.report_generator.generate_all_reports(summary['patient_data'])
            report_paths = self.report_generator.save_reports(
                reports,
                patient_name=summary['metadata'].get('patient_name', 'patient')
            )
            
            logger.info(f"\n✓ 第六步完成:")
            logger.info(f"  生成报告: {len(reports)} 份")
            for report_type, path in report_paths.items():
                logger.info(f"    - {report_type}: {path}")
        except Exception as e:
            logger.warning(f"\n⚠️  第六步失败（可选步骤）: {e}")
            report_paths = {}
        
        # ============ 最终报告 ============
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "=" * 80)
        logger.info("处理完成！")
        logger.info("=" * 80)
        logger.info(f"总耗时: {elapsed:.1f} 秒")
        if stats_1['total'] > 0:
            logger.info(f"平均每个文件: {elapsed/stats_1['total']:.1f} 秒")
        
        # 保存最终报告
        final_report = self._generate_final_report(
            parse_results, summary, organize_stats, elapsed
        )
        self._save_final_report(final_report)
        
        # 打印最终报告
        self._print_final_report(final_report)
        
        return {
            "status": "success",
            "total_files": stats_1['total'],
            "successful": stats_1['successful'],
            "failed": stats_1['failed'],
            "success_rate": stats_1['success_rate'],
            "elapsed_seconds": elapsed,
            "summary": summary,
            "organize_stats": organize_stats,
        }
    
    def _generate_final_report(self, 
                              parse_results: Dict,
                              summary: dict,
                              organize_stats: dict,
                              elapsed: float) -> dict:
        """生成最终报告
        
        Args:
            parse_results: 解析结果
            summary: 患者汇总
            organize_stats: 组织统计
            elapsed: 耗时 (秒)
        
        Returns:
            dict: 最终报告
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "input_directory": self.input_dir,
            "reports_directory": self.organizer.reports_dir,
            "processing_stats": {
                "total_files": len(parse_results),
                "successfully_parsed": sum(
                    1 for r in parse_results.values() if r.success
                ),
                "successfully_renamed": organize_stats['successful'],
                "successfully_organized": organize_stats['successful'],
                "failed": organize_stats['failed'],
                "elapsed_seconds": elapsed,
            },
            "file_statistics": summary['summary_stats'],
            "files_by_type": summary['by_type'],
            "files_by_date": summary['timeline'],
            "organize_breakdown": organize_stats['by_category'],
        }
    
    def _save_final_report(self, report: dict):
        """保存最终报告
        
        Args:
            report: 最终报告
        """
        report_path = os.path.join(
            self.input_dir, "logs", "final_report.json"
        )
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"\n✓ 最终报告已保存: {report_path}")
        except Exception as e:
            logger.error(f"✗ 保存报告失败: {e}")
    
    def _print_final_report(self, report: dict):
        """打印最终报告
        
        Args:
            report: 最终报告
        """
        stats = report['processing_stats']
        file_stats = report['file_statistics']
        
        logger.info("\n" + "=" * 80)
        logger.info("最终处理报告")
        logger.info("=" * 80)
        
        logger.info(f"\n处理统计:")
        logger.info(f"  总文件数: {stats['total_files']}")
        logger.info(f"  成功解析: {stats['successfully_parsed']}")
        logger.info(f"  成功重命名: {stats['successfully_renamed']}")
        logger.info(f"  成功组织: {stats['successfully_organized']}")
        logger.info(f"  失败: {stats['failed']}")
        logger.info(f"  耗时: {stats['elapsed_seconds']:.1f} 秒")
        
        logger.info(f"\n文件统计:")
        logger.info(f"  报告类型数: {len(report['files_by_type'])}")
        logger.info(f"  平均置信度: {file_stats['average_confidence']:.2f}")
        logger.info(f"  总文本字数: {file_stats['total_text_length']:,}")
        logger.info(f"  平均文本: {file_stats['avg_text_length']:,} 字")
        
        logger.info(f"\n分类统计:")
        for category, subcats in report['organize_breakdown'].items():
            total = sum(subcats.values()) if isinstance(subcats, dict) else subcats
            logger.info(f"  {category}: {total} 个文件")
        
        logger.info(f"\n输出目录: {report['reports_directory']}")
        logger.info("=" * 80)
