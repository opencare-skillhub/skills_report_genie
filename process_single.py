#!/usr/bin/env python3
"""单张图片处理脚本

每次处理一张医学图片，快速高效
流程: 扫描 -> 解析 -> 添加JSON -> 重命名 -> 分类 -> 报告解析 -> 智能体调用 -> 生成报告 -> 发布Web
"""

import sys
import os
import json
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.processing.file_processor import FileProcessor
from src.processing.file_renamer import FileRenamer
from src.processing.file_organizer import FileOrganizer
from src.processing.json_aggregator import JsonAggregator
from src.reporting.report_generator import ReportGenerator
from src.analysis.marker_analyzer import MarkerAnalyzer
from src.analysis.pathology_extractor import PathologyFeatureExtractor
from src.analysis.genetic_extractor import GeneticFeatureExtractor
from src.analysis.risk_stratifier import RiskStratifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_single_image(image_path: str, work_dir: str, generate_report: bool = True) -> dict:
    """处理单张医学图片 (完整流程)
    
    流程: 扫描 -> 解析 -> 添加JSON -> 重命名 -> 分类 -> 报告解析 -> 智能体调用 -> 生成报告
    
    Args:
        image_path: 图片路径
        work_dir: 工作目录 (保存数据和分类文件)
        generate_report: 是否生成医学报告 (默认True)
    
    Returns:
        dict: 处理结果
    """
    
    if not os.path.exists(image_path):
        logger.error(f"✗ 文件不存在: {image_path}")
        return {"status": "error", "error": "文件不存在"}
    
    logger.info("="*80)
    logger.info(f"处理图片: {os.path.basename(image_path)}")
    logger.info("="*80)
    
    try:
        # 初始化处理器
        processor = FileProcessor(work_dir)
        renamer = FileRenamer(work_dir, os.path.join(work_dir, "backup"))
        organizer = FileOrganizer(work_dir)
        aggregator = JsonAggregator(os.path.join(work_dir, "data", "extracted"))
        
        # ========== 第一步: 解析图片 ==========
        logger.info("\n[1/6] 解析图片...")
        result = processor.parse_single_file(image_path)
        
        if not result.success:
            logger.error(f"✗ 解析失败: {result.error}")
            return {
                "status": "error",
                "error": result.error,
                "file": os.path.basename(image_path),
            }
        
        # 验证解析内容的质量
        if not result.extraction_result:
            logger.error(f"✗ 解析失败: 未生成结构化数据")
            return {
                "status": "error",
                "error": "未生成结构化数据",
                "file": os.path.basename(image_path),
            }
        
        raw_data = result.extraction_result.get('raw_data', {})
        text_length = result.extraction_result.get('text_length', 0)
        full_text = result.extraction_result.get('full_text', '')
        
        # 检查内容是否为空或信息太少
        if text_length < 20 or not full_text or not full_text.strip():
            logger.error(f"✗ 解析失败: 提取内容过少 ({text_length} 字符)")
            return {
                "status": "error",
                "error": f"提取内容过少 ({text_length} 字符)",
                "file": os.path.basename(image_path),
            }
        
        # 检查是否提取了关键信息
        report_type = raw_data.get('report_type', '')
        diagnosis = raw_data.get('diagnosis', '')
        
        # 如果没有识别出报告类型，视为失败
        if not report_type or report_type == 'Unknown':
            logger.error(f"✗ 解析失败: 无法识别报告类型")
            return {
                "status": "error",
                "error": "无法识别报告类型",
                "file": os.path.basename(image_path),
            }
        
        # ========== 第二步: 保存JSON (主病情数据记录) ==========
        logger.info("\n[2/6] 保存主病情JSON...")
        processor._save_json(result)
        logger.info(f"✓ JSON已保存")
        logger.info(f"  报告类型: {report_type}")
        logger.info(f"  诊断: {diagnosis[:50] if diagnosis else '(无)'}") 
        
        # ========== 第三步: 重命名文件 ==========
        logger.info("\n[3/6] 重命名文件...")
        new_name = renamer.rename_file(image_path, result.extraction_result)
        logger.info(f"✓ 重命名: {os.path.basename(image_path)} → {new_name}")
        
        # ========== 第四步: 分类移动文件 ==========
        logger.info("\n[4/6] 分类和移动文件...")
        organizer.create_directory_structure()
        organize_stats = organizer.organize_files({image_path: new_name})
        
        if organize_stats['successful'] > 0:
            category, subcat = organizer.classify_by_filename(new_name)
            logger.info(f"✓ 文件已分类: {category}/{subcat}")
        else:
            logger.warning(f"✗ 分类失败")
        
        # ========== 第五步: 报告重点解析 ==========
        logger.info("\n[5/6] 报告重点解析...")
        try:
            # 加载所有JSON数据
            aggregator.load_all_json()
            summary = aggregator.build_patient_summary()
            logger.info(f"✓ 已生成患者数据汇总")
            
            # 提取关键特征用于后续智能体分析
            pathology_features = PathologyFeatureExtractor().extract_from_summary(summary)
            genetic_features = GeneticFeatureExtractor().extract_from_summary(summary)
            risk_assessment = RiskStratifier().assess_risk(summary)
            
            logger.info(f"✓ 特征提取完成 (病理/遗传/风险)")
        except Exception as e:
            logger.warning(f"⚠️  报告解析失败 (非关键步骤): {e}")
            summary = None
            pathology_features = {}
            genetic_features = {}
            risk_assessment = {}
        
        # ========== 第六步: 生成医学报告 & 调用智能体 ==========
        if generate_report and summary:
            logger.info("\n[6/6] 生成医学报告 (调用两个智能体)...")
            try:
                # 初始化报告生成器 (包含PopularScienceAgent & VisualizationAgent)
                report_generator = ReportGenerator(
                    output_dir=os.path.join(work_dir, "reports")
                )
                
                # 生成所有报告格式: 完整版 + 科普版 + 可视化 + 问诊清单
                patient_data = summary.get('patient_data', {})
                reports = report_generator.generate_all_reports(patient_data)
                
                # 保存报告文件
                report_paths = report_generator.save_reports(
                    reports,
                    patient_name=summary.get('metadata', {}).get('patient_name', 'patient')
                )
                
                logger.info(f"✓ 医学报告生成完成:")
                for report_type, path in report_paths.items():
                    logger.info(f"  - {report_type}: {path}")
                
            except Exception as e:
                logger.warning(f"⚠️  报告生成失败 (可选步骤): {e}")
                report_paths = {}
        else:
            logger.info("\n[6/6] 跳过医学报告生成")
            report_paths = {}
        
        # ========== 最终结果 ==========
        logger.info("\n" + "="*80)
        logger.info("处理完成！")
        logger.info("="*80)
        
        final_report = {
            "status": "success",
            "file": os.path.basename(image_path),
            "new_name": new_name,
            "category": category if organize_stats['successful'] > 0 else "unknown",
            "confidence": result.extraction_result['confidence'],
            "report_date": raw_data.get('report_date', 'N/A'),
            "report_type": raw_data.get('report_type', 'Unknown'),
            "diagnosis": raw_data.get('diagnosis', ''),
            "summary": raw_data.get('summary', ''),
            "text_length": result.extraction_result['text_length'],
            "reports_generated": report_paths,
        }
        
        logger.info(f"报告类型: {final_report['report_type']}")
        logger.info(f"报告日期: {final_report['report_date']}")
        logger.info(f"诊断: {final_report['diagnosis'][:50] if final_report['diagnosis'] else '(无)'}...")
        logger.info(f"新文件名: {new_name}")
        logger.info(f"分类: {final_report['category']}")
        logger.info(f"生成报告: {len(report_paths)} 份")
        logger.info("="*80)
        
        return final_report
    
    except Exception as e:
        logger.error(f"✗ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "error": str(e),
            "file": os.path.basename(image_path),
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='单张医学图片处理 - 完整流程',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理单张图片到指定工作目录，生成医学报告
  python process_single.py image.jpg -w /path/to/work/dir

  # 默认工作目录为当前目录，跳过报告生成
  python process_single.py image.jpg --no-report

  # 处理多张图片 (shell 脚本)
  for img in *.jpg; do
    python process_single.py "$img" -w ~/work --report
  done

完整流程:
  扫描 → 解析 → 添加JSON → 重命名 → 分类 → 报告解析 → 智能体调用 → 生成报告
        """
    )
    
    parser.add_argument('image', help='医学图片路径')
    parser.add_argument('-w', '--work-dir', default='.',
                       help='工作目录 (默认: 当前目录)')
    parser.add_argument('-o', '--output', help='输出 JSON 文件路径')
    parser.add_argument('--report', action='store_true', default=True,
                       help='生成医学报告 (默认开启)')
    parser.add_argument('--no-report', dest='report', action='store_false',
                       help='跳过医学报告生成')
    
    args = parser.parse_args()
    
    # 处理图片 (完整流程)
    result = process_single_image(args.image, args.work_dir, generate_report=args.report)
    
    # 保存结果
    if args.output:
        os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"\n✓ 结果已保存: {args.output}")
    
    return 0 if result['status'] == 'success' else 1


if __name__ == '__main__':
    sys.exit(main())
