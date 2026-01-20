#!/usr/bin/env python3
"""
医学影像OCR测试脚本
测试多级降级策略：DeepSeek-OCR -> Gemini-3-Flash -> Local PaddleOCR
"""

import os
import sys
import logging
from pathlib import Path

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from file_handler.content_extractor import ContentExtractor, ExtractionMethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_medical_image_ocr():
    """测试医学影像OCR"""
    
    # 初始化提取器
    extractor = ContentExtractor(use_vl_model=True)
    
    # 测试图片路径
    test_images = [
        "/Users/qinxiaoqiang/Downloads/report_mess/IMG_0125.JPG",
        "/Users/qinxiaoqiang/Downloads/report_mess/01 病情概述_页面_01.JPG",
        "/Users/qinxiaoqiang/Downloads/report_mess/01 病情概述_页面_02.JPG",
    ]
    
    for img_path in test_images:
        if not os.path.exists(img_path):
            logger.warning(f"⊘ 图片不存在: {img_path}")
            continue
            
        logger.info(f"\n{'='*60}")
        logger.info(f"测试图片: {Path(img_path).name}")
        logger.info(f"{'='*60}")
        
        result = extractor.extract(img_path)
        
        logger.info(f"提取方法: {result.extraction_method.value}")
        logger.info(f"置信度: {result.confidence:.2f}")
        logger.info(f"错误: {result.error}")
        logger.info(f"文本长度: {len(result.text)} 字符")
        
        if result.text:
            logger.info(f"\n文本内容预览 (前500字符):")
            logger.info(result.text[:500])
            
        if result.raw_data:
            logger.info(f"\n结构化数据:")
            import json
            logger.info(json.dumps(result.raw_data, ensure_ascii=False, indent=2)[:500])
        
        logger.info("")

if __name__ == "__main__":
    test_medical_image_ocr()
