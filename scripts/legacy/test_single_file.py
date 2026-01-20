#!/usr/bin/env python3
"""简单测试：测试单个文件的内容提取"""

import sys
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

sys.path.insert(0, '/Users/qinxiaoqiang/Downloads/skill-report-genie')

from src.file_handler.content_extractor import ContentExtractor
from src.file_handler.content_classifier import ContentClassifier

def main():
    # 测试文件
    test_file = "/Users/qinxiaoqiang/Downloads/report_mess/2023-06-23_处方用药.JPG"
    
    print("="*80)
    print("单文件内容提取测试")
    print("="*80)
    print(f"\n测试文件: {test_file}\n")
    
    # 1. 提取内容
    print("1. 提取文件内容...")
    extractor = ContentExtractor()
    result = extractor.extract(test_file)
    
    print(f"   提取方法: {result.extraction_method.value}")
    print(f"   文件类型: {result.file_type}")
    print(f"   置信度: {result.confidence}")
    print(f"   错误: {result.error or '无'}")
    print(f"   文本长度: {len(result.text)} 字符")
    
    if result.text:
        print(f"\n   提取的文本（前500字符）:")
        print("   " + "-"*76)
        print("   " + result.text[:500].replace("\n", "\n   "))
        print("   " + "-"*76)

    if result.raw_data:
        print(f"\n   结构化数据 (JSON):")
        print("   " + "-"*76)
        import json
        print("   " + json.dumps(result.raw_data, indent=2, ensure_ascii=False).replace("\n", "\n   "))
        print("   " + "-"*76)
    
    # 2. 分类
    print("\n2. 基于内容分类...")
    classifier = ContentClassifier()
    import os
    classification = classifier.classify(result.text, os.path.basename(test_file))
    
    print(f"   分类: {classification.category.value}")
    print(f"   置信度: {classification.confidence:.3f}")
    print(f"   方法: {classification.method}")
    print(f"   理由: {classification.reasoning}")
    print(f"   找到的关键词: {classification.keywords_found[:10]}")
    
    # 3. 提取元数据（日期等）
    print("\n3. 提取元数据...")
    from src.file_handler.metadata_extractor import MetadataExtractor
    import json
    
    metadata_extractor = MetadataExtractor()
    
    extracted_date = None
    patient_name = None

    # 优先从结构化数据中获取
    if result.raw_data:
        extracted_date = result.raw_data.get("report_date")
        patient_name = result.raw_data.get("patient_name")
        print(f"   (从JSON) 提取日期: {extracted_date}")
        print(f"   (从JSON) 患者姓名: {patient_name}")
    
    # 如果没找到，尝试从文本提取
    if not extracted_date:
        extracted_date = metadata_extractor.extract_date(result.text)
        print(f"   (从文本) 提取日期: {extracted_date}")
        
    if not patient_name:
        patient_name = metadata_extractor.extract_patient_name(result.text)
        print(f"   (从文本) 患者姓名: {patient_name}")

    # 4. 生成新文件名
    print("\n4. 生成建议文件名...")
    new_filename = None
    if extracted_date and classification.category:
        # 获取文件扩展名
        _, ext = os.path.splitext(test_file)
        # 映射分类到中文简写
        # 映射分类到中文简写 (根据 FileCategory 枚举值)
        category_map = {
            "医疗诊疗/检查检测报告": "检验报告",
            "医疗诊疗/影像": "影像报告",
            "医疗诊疗/病历": "病历记录",
            "医疗诊疗/处方用药": "处方用药",
            "并发症管理": "并发症记录",
            "营养管理": "营养记录",
            "心理支持": "心理记录",
            "待确认": "待确认资料"
        }
        category_cn = category_map.get(classification.category.value, "其他资料")
        
        new_filename = f"{extracted_date}_{category_cn}{ext}"
        print(f"   建议重命名为: {new_filename}")
        
        # 执行重命名
        new_path = os.path.join(os.path.dirname(test_file), new_filename)
        try:
            os.rename(test_file, new_path)
            print(f"   ✓ 文件已重命名为: {new_filename}")
            # 更新test_file变量以供后续从新路径读取（如果需要）
            # 注意：后续的JSON保存逻辑使用的是原test_file变量作为key，这里暂时保持原状
            # 但JSON文件最好也保存一份到新文件名对应的位置
        except Exception as e:
            print(f"   ❌ 重命名失败: {e}")
    else:
        print("   无法生成新文件名 (缺少日期或分类)")

    # 5. 保存结果到JSON
    print("\n5. 保存处理结果...")
    output_data = {
        "original_file": test_file,
        "new_filename": new_filename,
        "category": classification.category.value,
        "category_cn": category_map.get(classification.category.value, "其他资料") if 'category_map' in locals() else classification.category.value,
        "confidence": classification.confidence,
        "extracted_date": extracted_date,
        "patient_name": patient_name,
        "content_summary": result.text[:200] if result.text else "",
        "keywords": classification.keywords_found,
        "raw_data": result.raw_data if result.raw_data else {}
    }
    
    json_path = test_file + ".json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"   结果已保存至: {json_path}")
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)

if __name__ == "__main__":
    main()
