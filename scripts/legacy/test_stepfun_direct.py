#!/usr/bin/env python3
"""直接测试 StepFun API 调用"""

import sys
import os
import base64
import json

sys.path.insert(0, '.')

# 加载环境变量
for line in open('.env'):
    if line.strip() and not line.startswith('#'):
        key, val = line.strip().split('=', 1)
        os.environ[key] = val

from src.file_handler.content_extractor import ContentExtractor

# 测试图片
test_img = "/Users/qinxiaoqiang/Downloads/report_mess/01 病情概述_页面_04.JPG"

print(f"测试图片: {test_img}")
print(f"文件存在: {os.path.exists(test_img)}\n")

extractor = ContentExtractor(use_vl_model=True)

print("调用 extract_image...")
try:
    result = extractor.extract(test_img)
    
    print(f"\n✓ 成功!")
    print(f"方法: {result.extraction_method.value}")
    print(f"置信度: {result.confidence}")
    print(f"错误: {result.error}")
    print(f"文本长度: {len(result.text)}")
    
    if result.raw_data:
        print(f"\n结构化数据:")
        print(json.dumps(result.raw_data, ensure_ascii=False, indent=2)[:500])

except Exception as e:
    print(f"✗ 异常: {e}")
    import traceback
    traceback.print_exc()
