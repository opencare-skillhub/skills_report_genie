#!/usr/bin/env python3
"""分批处理医学文件

每次只处理 1-2 张图片，避免 API 超时和堆积错误
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent))

from src.processing.file_processor import FileProcessor
from src.processing.file_renamer import FileRenamer
from src.processing.json_aggregator import JsonAggregator
from src.processing.file_organizer import FileOrganizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchProcessor:
    """分批处理器 - 每次处理 1-2 张图片"""
    
    def __init__(self, input_dir: str, batch_size: int = 2):
        """初始化
        
        Args:
            input_dir: 输入目录
            batch_size: 每批处理的文件数 (1-2)
        """
        self.input_dir = input_dir
        self.batch_size = min(batch_size, 2)  # 最多 2 张
        
        self.processor = FileProcessor(input_dir)
        self.renamer = FileRenamer(
            input_dir,
            os.path.join(input_dir, "backup", "original")
        )
        self.organizer = FileOrganizer(input_dir)
        
        logger.info(f"✓ BatchProcessor 初始化完成 (批大小: {self.batch_size})")
    
    def get_unprocessed_files(self) -> List[str]:
        """获取未处理的文件
        
        Returns:
            List[str]: 文件路径列表
        """
        processed_dir = os.path.join(self.input_dir, "data", "extracted")
        processed_hashes = set()
        
        if os.path.exists(processed_dir):
            for json_file in Path(processed_dir).glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        file_hash = data.get('metadata', {}).get('file_hash')
                        if file_hash:
                            processed_hashes.add(file_hash)
                except:
                    pass
        
        # 扫描所有文件
        all_files = self.processor.scan_directory()
        
        # 过滤已处理的文件
        unprocessed = []
        for file_path in all_files:
            try:
                file_hash = self.processor._calculate_file_hash(file_path)
                if file_hash not in processed_hashes:
                    unprocessed.append(file_path)
            except:
                unprocessed.append(file_path)
        
        return unprocessed
    
    def process_batch(self, batch_num: int = 1) -> dict:
        """处理一批文件
        
        Args:
            batch_num: 批次号 (用于日志)
        
        Returns:
            dict: 处理结果
        """
        # 获取未处理的文件
        unprocessed = self.get_unprocessed_files()
        
        if not unprocessed:
            logger.info("✓ 所有文件已处理！")
            return {"status": "complete", "remaining": 0}
        
        # 获取本批要处理的文件
        batch_files = unprocessed[:self.batch_size]
        remaining = len(unprocessed) - len(batch_files)
        
        logger.info("\n" + "="*80)
        logger.info(f"第 {batch_num} 批: 处理 {len(batch_files)} 个文件 (剩余 {remaining} 个)")
        logger.info("="*80)
        
        # 第一步: 解析这批文件
        logger.info(f"\n[1/3] 解析文件...\n")
        
        parse_results = {}
        for file_path in batch_files:
            try:
                logger.info(f"  解析: {os.path.basename(file_path)}")
                result = self.processor.parse_single_file(file_path)
                parse_results[file_path] = result
                
                if result.success:
                    self.processor._save_json(result)
                    logger.info(f"    ✓ 成功 (置信度: {result.extraction_result['confidence']:.2f})")
                else:
                    logger.warning(f"    ✗ 失败: {result.error}")
            except Exception as e:
                logger.error(f"    ✗ 错误: {e}")
        
        successful = sum(1 for r in parse_results.values() if r.success)
        logger.info(f"\n✓ 解析完成: {successful}/{len(batch_files)}")
        
        # 第二步: 重命名文件
        logger.info(f"\n[2/3] 重命名文件...\n")
        
        files_to_move = {}
        for file_path, result in parse_results.items():
            if result.success and result.extraction_result:
                try:
                    new_name = self.renamer.rename_file(
                        file_path,
                        result.extraction_result
                    )
                    files_to_move[file_path] = new_name
                except Exception as e:
                    logger.error(f"  ✗ 重命名失败 {os.path.basename(file_path)}: {e}")
        
        logger.info(f"✓ 重命名完成: {len(files_to_move)} 个")
        
        # 第三步: 分类移动文件
        logger.info(f"\n[3/3] 分类和移动文件...\n")
        
        organize_stats = self.organizer.organize_files(files_to_move)
        
        logger.info(f"\n✓ 批处理完成")
        logger.info(f"  本批成功: {organize_stats['successful']}")
        logger.info(f"  本批失败: {organize_stats['failed']}")
        logger.info(f"  剩余文件: {remaining}")
        logger.info("="*80)
        
        return {
            "status": "success",
            "batch_num": batch_num,
            "processed": len(batch_files),
            "successful": organize_stats['successful'],
            "failed": organize_stats['failed'],
            "remaining": remaining,
        }
    
    def process_all_batches(self, auto: bool = False, wait_seconds: int = 5) -> dict:
        """处理所有批次
        
        Args:
            auto: 自动模式（不交互）
            wait_seconds: 批次间等待时间（秒）
        
        Returns:
            dict: 总结结果
        """
        import time
        
        batch_num = 1
        total_stats = {
            "total_batches": 0,
            "total_files": 0,
            "total_successful": 0,
            "total_failed": 0,
        }
        
        while True:
            result = self.process_batch(batch_num)
            
            if result["status"] == "complete":
                break
            
            total_stats["total_batches"] += 1
            total_stats["total_files"] += result["processed"]
            total_stats["total_successful"] += result["successful"]
            total_stats["total_failed"] += result["failed"]
            
            if result["remaining"] == 0:
                break
            
            batch_num += 1
            
            # 自动模式：等待后继续；手动模式：询问用户
            if auto:
                logger.info(f"\n⏳ {wait_seconds}秒后自动处理下一批...")
                for i in range(wait_seconds, 0, -1):
                    logger.info(f"  {i} 秒...", extra={'countdown': True})
                    time.sleep(1)
            else:
                user_input = input(f"\n继续处理下一批? (y/n): ").strip().lower()
                if user_input != 'y':
                    logger.info(f"用户停止处理。剩余 {result['remaining']} 个文件")
                    break
        
        # 最后汇总所有JSON
        logger.info(f"\n最后汇总 JSON 数据...")
        self._finalize_summary()
        
        logger.info("\n" + "="*80)
        logger.info("全部处理完成！")
        logger.info("="*80)
        logger.info(f"总批次: {total_stats['total_batches']}")
        logger.info(f"总文件: {total_stats['total_files']}")
        logger.info(f"成功: {total_stats['total_successful']}")
        logger.info(f"失败: {total_stats['total_failed']}")
        
        return total_stats
    
    def _finalize_summary(self):
        """最后汇总 JSON 数据"""
        try:
            aggregator = JsonAggregator(
                os.path.join(self.input_dir, "data", "extracted")
            )
            aggregator.load_all_json()
            summary = aggregator.build_patient_summary()
            
            summary_path = os.path.join(
                self.input_dir, "data", "patient_summary.json"
            )
            aggregator.save_patient_summary(summary_path)
            
            logger.info(f"✓ 患者汇总已保存")
            aggregator.print_summary()
        except Exception as e:
            logger.error(f"汇总失败: {e}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='分批处理医学文件 (每次 1-2 张)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
工作模式:
  • 默认: 自动模式 (每批处理后等待5秒，自动处理下一批)
  • --interactive: 交互模式 (每批处理后询问用户)

示例:
  # 默认: 自动模式，每次2张，等待5秒
  python process_batch.py /path/to/medical/files

  # 自动模式，每次1张，等待3秒
  python process_batch.py /path/to/medical/files -b 1 -w 3

  # 交互模式 (每批处理后询问)
  python process_batch.py /path/to/medical/files --interactive

  # 显示未处理文件数
  python process_batch.py /path/to/medical/files --status
        """
    )
    
    parser.add_argument('input_dir', help='输入目录')
    parser.add_argument('-b', '--batch-size', type=int, default=2,
                       help='每批处理的文件数 (1-2, 默认 2)')
    parser.add_argument('--auto', action='store_true',
                       help='自动处理全部 (默认，等待5秒后处理下一批)')
    parser.add_argument('-w', '--wait', type=int, default=5,
                       help='批次间等待时间（秒，默认5秒）')
    parser.add_argument('--interactive', action='store_true',
                       help='交互模式 (每批处理后询问)')
    parser.add_argument('--status', action='store_true',
                       help='显示未处理文件数并退出')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.input_dir):
        print(f"✗ 错误: 目录不存在: {args.input_dir}")
        return 1
    
    try:
        processor = BatchProcessor(args.input_dir, args.batch_size)
        
        if args.status:
            unprocessed = processor.get_unprocessed_files()
            print(f"\n未处理文件数: {len(unprocessed)}")
            if unprocessed:
                print(f"需要 {len(unprocessed) // args.batch_size + 1} 批处理")
            return 0
        
        # 默认自动模式（除非 --interactive）
        auto_mode = not args.interactive
        
        processor.process_all_batches(auto=auto_mode, wait_seconds=args.wait)
        return 0
    
    except KeyboardInterrupt:
        print("\n✗ 用户中断")
        return 1
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
