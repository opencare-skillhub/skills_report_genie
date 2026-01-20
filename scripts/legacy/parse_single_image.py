#!/usr/bin/env python3
"""
单个医学图片OCR解析脚本
支持多级降级：step-1o-turbo-vision -> DeepSeek-OCR -> Gemini -> PaddleOCR
每次解析一张图片，输出结构化数据和纯文本
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from file_handler.content_extractor import ContentExtractor, ExtractionMethod

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_image(image_path: str, output_dir: Optional[str] = None) -> dict:
    """
    解析单个医学图片
    
    Args:
        image_path: 图片文件路径
        output_dir: 输出目录（可选）
        
    Returns:
        dict: 包含解析结果的字典
    """
    
    if not os.path.exists(image_path):
        logger.error(f"❌ 文件不存在: {image_path}")
        return {"error": f"文件不存在: {image_path}"}
    
    logger.info(f"\n{'='*70}")
    logger.info(f"开始解析: {Path(image_path).name}")
    logger.info(f"{'='*70}")
    
    # 初始化提取器
    extractor = ContentExtractor(use_vl_model=True)
    
    # 执行解析
    result = extractor.extract(image_path)
    
    # 构建结果字典
    output = {
        "image_path": image_path,
        "image_name": Path(image_path).name,
        "extraction_method": result.extraction_method.value,
        "confidence": result.confidence,
        "language": result.language,
        "text_length": len(result.text),
        "error": result.error,
        "full_text": result.text,
        "structured_data": result.raw_data or {}
    }
    
    # 日志输出
    logger.info(f"✓ 解析完成")
    logger.info(f"  方法: {result.extraction_method.value}")
    logger.info(f"  置信度: {result.confidence:.2f}")
    logger.info(f"  文本长度: {len(result.text)} 字符")
    
    if result.error:
        logger.warning(f"  ⚠️ 错误: {result.error}")
    
    # 输出到文件（如果指定了输出目录）
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        stem = Path(image_path).stem
        
        # 保存JSON结果
        json_output = os.path.join(output_dir, f"{stem}_result.json")
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        logger.info(f"  💾 JSON已保存: {json_output}")
        
        # 保存纯文本
        txt_output = os.path.join(output_dir, f"{stem}_text.txt")
        with open(txt_output, 'w', encoding='utf-8') as f:
            f.write(result.text)
        logger.info(f"  💾 文本已保存: {txt_output}")
        
        # 如果有结构化数据，保存为单独的JSON
        if result.raw_data:
            data_output = os.path.join(output_dir, f"{stem}_data.json")
            with open(data_output, 'w', encoding='utf-8') as f:
                json.dump(result.raw_data, f, ensure_ascii=False, indent=2)
            logger.info(f"  💾 结构化数据已保存: {data_output}")
    
    # 打印文本预览
    if result.text:
        logger.info(f"\n📄 文本内容预览 (前300字符):")
        logger.info("-" * 70)
        preview = result.text[:300]
        logger.info(preview)
        if len(result.text) > 300:
            logger.info("...")
        logger.info("-" * 70)
    
    # 打印结构化数据
    if result.raw_data:
        logger.info(f"\n📊 结构化数据:")
        logger.info("-" * 70)
        try:
            # 只打印关键字段
            for key in ['patient_name', 'report_date', 'report_type', 'diagnosis', 'summary']:
                if key in result.raw_data and result.raw_data[key]:
                    logger.info(f"  {key}: {result.raw_data[key]}")
            
            if 'indicators' in result.raw_data and result.raw_data['indicators']:
                logger.info(f"  indicators: {len(result.raw_data['indicators'])} 项")
                for indicator in result.raw_data['indicators'][:3]:  # 只显示前3个
                    if isinstance(indicator, dict):
                        logger.info(f"    - {indicator.get('name', '未知')}: {indicator.get('value', 'N/A')} {indicator.get('unit', '')}")
        except:
            logger.info(json.dumps(result.raw_data, ensure_ascii=False, indent=2)[:500])
        logger.info("-" * 70)
    
    return output


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='医学图片OCR解析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 解析单个图片
  python parse_single_image.py /path/to/image.jpg
  
  # 解析并保存到输出目录
  python parse_single_image.py /path/to/image.jpg -o ./output
  
  # 解析多个图片
  python parse_single_image.py /path/to/image1.jpg /path/to/image2.jpg -o ./output
        """
    )
    
    parser.add_argument('images', nargs='+', help='图片文件路径')
    parser.add_argument('-o', '--output', help='输出目录（保存结果文件）', default=None)
    parser.add_argument('-q', '--quiet', action='store_true', help='不输出日志')
    
    args = parser.parse_args()
    
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    results = []
    
    for image_path in args.images:
        try:
            result = parse_image(image_path, args.output)
            results.append(result)
        except Exception as e:
            logger.error(f"❌ 解析失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            results.append({"error": str(e)})
    
    # 如果有输出目录，保存批量结果
    if args.output and len(results) > 1:
        summary_file = os.path.join(args.output, "summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total": len(results),
                "results": results
            }, f, ensure_ascii=False, indent=2)
        logger.info(f"\n✓ 批量结果已保存: {summary_file}")
    
    return results


if __name__ == "__main__":
    main()
