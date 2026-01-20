"""文件扫描与解析模块 (v2.0)

根据 WORKFLOW_REDESIGN.md 实现
流程：扫描目录 → 解析所有文件 → 保存 JSON
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

# 导入解析工具
from src.file_handler.content_extractor import ContentExtractor, ExtractionMethod
from src.file_handler.document_analyzer import DocumentAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class ParseResult:
    """单个文件解析结果"""
    original_name: str
    file_path: str
    file_hash: str
    file_size: int
    mtime: float
    extraction_result: Optional[dict] = None
    error: Optional[str] = None
    success: bool = False


class FileProcessor:
    """统一的文件扫描与解析器"""
    
    # 支持的文件类型
    SUPPORTED_EXTENSIONS = {
        'image': ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'heic', 'gif'],
        'pdf': ['pdf'],
        'word': ['doc', 'docx'],
        'excel': ['xls', 'xlsx', 'csv'],
        'text': ['txt', 'md'],
    }
    
    def __init__(self, input_dir: str, output_dir: Optional[str] = None):
        """初始化处理器
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录（默认为 input_dir/data/extracted）
        """
        self.input_dir = input_dir
        self.output_dir = output_dir or os.path.join(input_dir, "data", "extracted")
        self.backup_dir = os.path.join(input_dir, "backup", "original")
        self.log_dir = os.path.join(input_dir, "logs")
        
        # 创建必要的目录
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 初始化解析器
        self.extractor = ContentExtractor(use_vl_model=True)
        self.analyzer = DocumentAnalyzer()
        
        logger.info(f"✓ FileProcessor 初始化完成")
        logger.info(f"  输入目录: {self.input_dir}")
        logger.info(f"  输出目录: {self.output_dir}")
    
    def scan_directory(self) -> List[str]:
        """扫描目录获取所有支持的文件
        
        Returns:
            List[str]: 文件路径列表
        """
        file_paths = []
        all_exts = set()
        for exts in self.SUPPORTED_EXTENSIONS.values():
            all_exts.update(exts)
        
        logger.info(f"扫描目录: {self.input_dir}")
        
        for root, dirs, files in os.walk(self.input_dir):
            # 跳过已处理的目录
            if 'data' in root or 'backup' in root or 'reports' in root:
                continue
            
            for file in files:
                ext = file.rsplit('.', 1)[-1].lower()
                if ext in all_exts:
                    file_path = os.path.join(root, file)
                    file_paths.append(file_path)
        
        logger.info(f"✓ 检测到 {len(file_paths)} 个文件")
        return sorted(file_paths)
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件 SHA256 哈希
        
        Args:
            file_path: 文件路径
        
        Returns:
            str: 哈希值
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def parse_single_file(self, file_path: str) -> ParseResult:
        """解析单个文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            ParseResult: 解析结果
        """
        try:
            
            # 获取文件信息
            file_stat = os.stat(file_path)
            file_name = os.path.basename(file_path)
            file_hash = self._calculate_file_hash(file_path)
            
            # 解析内容
            extraction_result = self.extractor.extract(file_path)
            
            # 获取文件类型
            ext = os.path.splitext(file_path)[1].lower().lstrip('.')
            
            # 对非图片文件进行 LLM 分析
            raw_data = extraction_result.raw_data or {}
            if ext in ['pdf', 'docx', 'doc', 'xlsx', 'xls', 'csv', 'txt', 'md'] and extraction_result.text:
                try:
                    # 判断文件类型
                    if ext in ['txt', 'md']:
                        analyze_type = 'txt'
                    elif ext in ['xlsx', 'xls', 'csv']:
                        analyze_type = 'excel'
                    elif ext in ['docx', 'doc']:
                        analyze_type = 'word'
                    else:
                        analyze_type = 'pdf'
                    
                    # 调用 LLM 分析
                    analysis_result = self.analyzer.analyze_document(
                        file_path,
                        extraction_result.text,
                        analyze_type
                    )
                    
                    # 合并分析结果
                    raw_data['analysis'] = analysis_result.structured_data
                    raw_data['analysis_confidence'] = analysis_result.confidence
                    
                    # 从LLM分析结果中提取report_type
                    analysis_data = analysis_result.structured_data or {}
                    if not raw_data.get('report_type'):
                        # 尝试从不同的分析结果字段中提取类型信息
                        if 'data_type' in analysis_data:
                            raw_data['report_type'] = analysis_data['data_type']
                        elif 'document_type' in analysis_data:
                            raw_data['report_type'] = analysis_data['document_type']
                        elif 'content_type' in analysis_data:
                            raw_data['report_type'] = analysis_data['content_type']
                    
                    # 从LLM分析结果中提取诊断/摘要
                    if not raw_data.get('summary'):
                        if 'summary' in analysis_data:
                            raw_data['summary'] = analysis_data['summary']
                    
                    if not raw_data.get('diagnosis'):
                        if 'diagnosis' in analysis_data:
                            raw_data['diagnosis'] = analysis_data['diagnosis']
                    
                    if not analysis_result.error:
                        logger.debug(f"  ✓ LLM 分析成功")
                    else:
                        logger.debug(f"  ⚠️  LLM 分析降级: {analysis_result.error}")
                
                except Exception as e:
                    logger.warning(f"  ⚠️  LLM 分析失败，跳过: {e}")
            
            # 构建结果
            result = ParseResult(
                original_name=file_name,
                file_path=file_path,
                file_hash=file_hash,
                file_size=file_stat.st_size,
                mtime=file_stat.st_mtime,
                extraction_result={
                    "confidence": extraction_result.confidence,
                    "extraction_method": extraction_result.extraction_method.value,
                    "language": extraction_result.language,
                    "text_length": len(extraction_result.text),
                    "error": extraction_result.error,
                    "full_text": extraction_result.text,
                    "raw_data": raw_data,
                },
                success=extraction_result.error is None,
            )
            
            if result.success:
                logger.debug(f"  ✓ 成功 (置信度: {extraction_result.confidence:.2f})")
            else:
                logger.debug(f"  ⚠️  警告: {extraction_result.error}")
            
            return result
            
        except Exception as e:
            logger.error(f"  ✗ 错误: {e}")
            return ParseResult(
                original_name=os.path.basename(file_path),
                file_path=file_path,
                file_hash="",
                file_size=0,
                mtime=0,
                error=str(e),
                success=False,
            )
    
    def process_all_files(self) -> Dict[str, ParseResult]:
        """逐个处理所有文件
        
        Returns:
            Dict[str, ParseResult]: 文件路径 -> 解析结果
        """
        file_paths = self.scan_directory()
        results = {}
        
        logger.info(f"\n开始处理 {len(file_paths)} 个文件...\n")
        
        for i, file_path in enumerate(file_paths, 1):
            progress = f"[{i}/{len(file_paths)}]"
            logger.info(f"{progress} 解析: {os.path.basename(file_path)}")
            
            # 解析文件
            result = self.parse_single_file(file_path)
            results[file_path] = result
            
            # 保存 JSON
            if result.success:
                self._save_json(result)
        
        # 汇总结果
        successful = sum(1 for r in results.values() if r.success)
        logger.info(f"\n✓ 处理完成: {successful}/{len(results)} 成功")
        
        return results
    
    def _save_json(self, result: ParseResult):
        """保存单个文件的提取结果 JSON
        
        Args:
            result: 解析结果
        """
        # 生成输出文件名 (基于 hash)
        json_name = f"{result.file_hash}.json"
        json_path = os.path.join(self.output_dir, json_name)
        
        # 构建 JSON 对象
        json_obj = {
            "metadata": {
                "original_name": result.original_name,
                "file_hash": result.file_hash,
                "file_size": result.file_size,
                "processed_time": datetime.now().isoformat(),
            },
            "extraction_result": result.extraction_result,
        }
        
        # 保存文件
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_obj, f, ensure_ascii=False, indent=2)
            logger.debug(f"  保存 JSON: {json_name}")
        except Exception as e:
            logger.error(f"  保存 JSON 失败: {e}")
    
    def get_success_stats(self, results: Dict[str, ParseResult]) -> dict:
        """获取处理统计信息
        
        Args:
            results: 所有处理结果
        
        Returns:
            dict: 统计信息
        """
        successful = [r for r in results.values() if r.success]
        failed = [r for r in results.values() if not r.success]
        
        stats = {
            "total": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(results) * 100 if results else 0,
            "by_type": self._count_by_type(successful),
        }
        
        return stats
    
    def _count_by_type(self, results: List[ParseResult]) -> dict:
        """统计按报告类型分类
        
        Args:
            results: 成功处理的结果列表
        
        Returns:
            dict: 类型统计
        """
        type_count = {}
        for result in results:
            if result.extraction_result:
                raw_data = result.extraction_result.get('raw_data', {})
                report_type = raw_data.get('report_type', 'Unknown')
                type_count[report_type] = type_count.get(report_type, 0) + 1
        
        return type_count
    
    def save_processing_log(self, results: Dict[str, ParseResult]):
        """保存处理日志
        
        Args:
            results: 所有处理结果
        """
        log_path = os.path.join(self.log_dir, "processing.log")
        
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"处理时间: {datetime.now().isoformat()}\n")
            f.write(f"总文件数: {len(results)}\n")
            f.write(f"成功: {sum(1 for r in results.values() if r.success)}\n")
            f.write(f"失败: {sum(1 for r in results.values() if not r.success)}\n\n")
            
            f.write("处理详情:\n")
            f.write("-" * 80 + "\n")
            
            for file_path, result in results.items():
                status = "✓" if result.success else "✗"
                f.write(f"{status} {result.original_name}\n")
                if not result.success:
                    f.write(f"  错误: {result.error}\n")
                else:
                    raw_data = result.extraction_result.get('raw_data', {})
                    report_type = raw_data.get('report_type', 'Unknown')
                    f.write(f"  类型: {report_type}\n")
                    f.write(f"  置信度: {result.extraction_result['confidence']:.2f}\n")
        
        logger.info(f"✓ 日志已保存: {log_path}")
