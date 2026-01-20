#!/usr/bin/env python3
"""测试内容提取和分类功能

使用 /Users/qinxiaoqiang/Downloads/report_mess 中的文件进行测试
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, '/Users/qinxiaoqiang/Downloads/skill-report-genie')

from src.file_handler.scanner import FileScanner


def main():
    """主测试函数"""
    print("="*80)
    print("内容提取和分类功能测试")
    print("="*80)
    
    # 测试目录
    test_dir = "/Users/qinxiaoqiang/Downloads/report_mess"
    
    if not os.path.exists(test_dir):
        print(f"❌ 测试目录不存在: {test_dir}")
        return
    
    print(f"\n📁 测试目录: {test_dir}")
    print(f"📊 启用内容提取: True\n")
    
    # 创建扫描器（启用内容提取）
    scanner = FileScanner(base_path=test_dir, use_content_extraction=True)
    
    # 扫描目录
    print("开始扫描...\n")
    scanned_files = scanner.scan_directory()
    
    # 打印结果
    print(f"\n✓ 扫描完成，共 {len(scanned_files)} 个文件\n")
    
    # 按分类分组显示
    by_category = {}
    for f in scanned_files:
        category = f.category.value
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(f)
    
    print("="*80)
    print("分类结果详情")
    print("="*80)
    
    for category, files in sorted(by_category.items()):
        print(f"\n【{category}】 ({len(files)} 个文件)")
        print("-" * 80)
        for f in files:
            confidence_bar = "█" * int(f.confidence * 20)
            print(f"  {f.file_name}")
            print(f"    置信度: {f.confidence:.2f} {confidence_bar}")
            print(f"    大小: {f.file_size / 1024:.1f} KB")
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)
    
    # 检查file_types.json
    json_path = os.path.join(test_dir, "file_types.json")
    if os.path.exists(json_path):
        print(f"\n✓ 文件类型记录已生成: {json_path}")
    else:
        print(f"\n⚠️  未生成文件类型记录")


if __name__ == "__main__":
    main()
