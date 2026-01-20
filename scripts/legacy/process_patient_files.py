#!/usr/bin/env python3
"""处理患者医学文件的主脚本 (v2.0)

使用流程:
  python process_patient_files.py /path/to/messy/medical/files

工作流程:
  1. 扫描并解析所有文件
  2. 基于内容重命名文件
  3. 汇总 JSON 数据
  4. 创建分类目录
  5. 组织和移动文件
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.processing.process_coordinator import ProcessCoordinator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='处理患者混乱的医学文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法
  python process_patient_files.py /path/to/medical/files

  # 查看帮助
  python process_patient_files.py -h

流程描述:
  1. [第1步] 扫描并解析所有文件
     - 检测支持的格式 (JPG, PDF, Word, Excel)
     - 使用 StepFun step-1o-turbo-vision 解析内容
     - 保存提取结果为 JSON

  2. [第2步] 基于内容重命名文件
     - 标准化文件名: <date>_<type>_<digest>_<seq>.<ext>
     - 备份原始文件
     - 记录映射关系

  3. [第3步] 汇总 JSON 数据
     - 加载所有提取的 JSON
     - 按时间线和报告类型组织
     - 生成患者汇总文件

  4. [第4步] 创建分类目录
     - 影像检查 (CT, MRI, 超声, X光, PET-CT)
     - 检验报告 (血检, 病理, 遗传)
     - 病历、处方、心理、营养

  5. [第5步] 组织和移动文件
     - 移动文件到对应分类目录
     - 复制 JSON 数据文件
     - 生成处理报告

输出目录结构:
  <input_dir>/
  ├── data/
  │   ├── extracted/
  │   │   ├── hash1.json (单个文件的提取结果)
  │   │   ├── hash2.json
  │   │   └── ...
  │   └── patient_summary.json (患者汇总)
  ├── backup/
  │   └── original/
  │       ├── 原始文件名.jpg
  │       └── ...
  ├── logs/
  │   ├── processing.log
  │   ├── rename_mapping.log
  │   └── final_report.json
  └── reports/ (分类后的文件)
      ├── imaging/
      │   ├── CT/
      │   ├── MRI/
      │   └── ...
      ├── lab_reports/
      │   ├── 血检/
      │   ├── 病理/
      │   └── ...
      └── ...
        """
    )
    
    parser.add_argument(
        'input_dir',
        help='包含混乱医学文件的输入目录'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='输出目录 (默认: input_dir/reports)',
        default=None
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='输出详细日志'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='不备份原始文件 (不推荐)'
    )
    
    args = parser.parse_args()
    
    # 验证输入目录
    if not os.path.isdir(args.input_dir):
        print(f"✗ 错误: 目录不存在: {args.input_dir}")
        return 1
    
    # 调整日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 运行处理
    try:
        coordinator = ProcessCoordinator(args.input_dir)
        result = coordinator.run_full_pipeline()
        
        # 检查结果
        if result['status'] == 'success':
            print(f"\n✓ 处理成功!")
            print(f"  成功率: {result['success_rate']:.1f}%")
            print(f"  耗时: {result['elapsed_seconds']:.1f} 秒")
            return 0
        else:
            print(f"\n✗ 处理失败")
            return 1
    
    except KeyboardInterrupt:
        print("\n✗ 用户中断")
        return 1
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
