"""文件扫描与分类模块

根据 DEVELOPMENT_PLAN.md § 2.1 实现
- 扫描目录结构
- 解析文件名、路径
- 自动分类至标准目录树
- 生成文件hash用于去重
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# 导入文件分类枚举（独立模块，避免循环导入）
from src.file_handler.file_category import FileCategory

# 内容提取和分类模块
try:
    from src.file_handler.content_extractor import ContentExtractor, ExtractionResult
    from src.file_handler.content_classifier import ContentClassifier, ClassificationResult
    from src.file_handler.file_type_recorder import FileTypeRecorder
    CONTENT_EXTRACTION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  内容提取模块未加载: {e}")
    CONTENT_EXTRACTION_AVAILABLE = False


@dataclass
class ScannedFile:
    """扫描文件信息"""
    
    file_path: str              # 完整路径
    file_name: str              # 文件名
    file_size: int              # 文件大小(字节)
    file_hash: str              # SHA256哈希
    mtime: float                # 修改时间戳
    category: FileCategory      # 分类
    confidence: float           # 分类置信度 (0-1)


class FileScanner:
    """文件扫描与分类器
    
    参考: DEVELOPMENT_PLAN.md § 2.1
    """
    
    # 按优先级排列的分类规则（优先级高的先匹配）
    # 使用列表保证顺序，而不是字典
    CLASSIFICATION_RULES = [
        # 最高优先级1：影像文件（特定格式 + 关键词）
        {
            'extensions': ['dcm', 'nii', 'nii.gz', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'pdf'],
            'keywords': ['CT', 'MRI', '超声', '影像', 'DICOM', 'x光', '放射'],
            'category': FileCategory.IMAGING,
            'confidence': 0.95
        },
        
        # 最高优先级2：检查检测报告
        {
            'extensions': ['xlsx', 'xls', 'csv', 'pdf'],
            'keywords': ['检查', '检验', '报告', '化验', '血液', '标志物', 'CA19', '肿瘤标志物', '基因', 'NGS', '病理', '组织学'],
            'category': FileCategory.LAB_REPORTS,
            'confidence': 0.95
        },
        
        # 中高优先级：处方用药
        {
            'extensions': ['txt', 'doc', 'docx'],
            'keywords': ['处方', '用药', '药物', '给药', '化疗', '吉西他滨', '顺铂', '方案'],
            'category': FileCategory.PRESCRIPTIONS,
            'confidence': 0.9
        },
        
        # 中优先级：并发症管理
        {
            'extensions': ['txt', 'doc', 'docx', 'pdf'],
            'keywords': ['并发症', '感染', '胰漏', '消化不良', '疼痛', '副作用'],
            'category': FileCategory.COMPLICATIONS,
            'confidence': 0.85
        },
        
        # 中优先级：心理支持
        {
            'extensions': ['txt', 'doc', 'docx', 'pdf'],
            'keywords': ['心理', '焦虑', '抑郁', '心理咨询', '心理评估'],
            'category': FileCategory.PSYCHOLOGY,
            'confidence': 0.8
        },
        
        # 中低优先级：营养管理
        {
            'extensions': ['txt', 'doc', 'docx', 'pdf'],
            'keywords': ['营养', '饮食', '进食', '体重', '营养支持'],
            'category': FileCategory.NUTRITION,
            'confidence': 0.8
        },
        
        # 低优先级：病历
        {
            'extensions': ['txt', 'md', 'docx', 'doc', 'pdf'],
            'keywords': ['病历', '病史', '诊断', '临床', '医生意见'],
            'category': FileCategory.MEDICAL_RECORDS,
            'confidence': 0.75
        }
    ]
    
    def __init__(self, base_path: str = ".", use_content_extraction: bool = True):
        """
        初始化文件扫描器
        
        Args:
            base_path: 扫描的基础路径
            use_content_extraction: 是否启用内容提取（默认True）
        """
        self.base_path = base_path
        self.scanned_files: List[ScannedFile] = []
        self.use_content_extraction = use_content_extraction and CONTENT_EXTRACTION_AVAILABLE
        
        # 初始化内容提取组件
        if self.use_content_extraction:
            try:
                self.content_extractor = ContentExtractor()
                self.content_classifier = ContentClassifier()
                self.file_type_recorder = FileTypeRecorder(base_path)
                print("✓ 内容提取功能已启用")
            except Exception as e:
                print(f"⚠️  内容提取初始化失败: {e}")
                self.use_content_extraction = False
        else:
            self.content_extractor = None
            self.content_classifier = None
            self.file_type_recorder = None
            if not CONTENT_EXTRACTION_AVAILABLE:
                print("⚠️  内容提取功能不可用（缺少依赖）")
    
    @staticmethod
    def _calculate_file_hash(file_path: str) -> str:
        """计算文件SHA256哈希
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 十六进制哈希值
        """
        sha256_hash = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                # 按块读取文件（支持大文件）
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"⚠️  计算文件哈希失败 {file_path}: {e}")
            return ""
    
    @staticmethod
    def _get_file_extension(file_path: str) -> str:
        """获取文件扩展名
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 扩展名 (小写，不含点)
        """
        name = os.path.basename(file_path)
        
        # 处理.nii.gz这样的双扩展名
        if name.endswith('.nii.gz'):
            return 'nii.gz'
        
        return os.path.splitext(name)[1].lstrip('.').lower()
    
    def _classify_file(self, file_path: str, file_name: str) -> Tuple[FileCategory, float]:
        """根据文件内容和文件名分类文件
        
        优先使用内容提取进行分类，如果不可用则回退到文件名分类
        
        Args:
            file_path: 完整文件路径
            file_name: 文件名
            
        Returns:
            Tuple: (分类, 置信度)
        """
        # 如果启用了内容提取，优先使用
        if self.use_content_extraction:
            try:
                # 1. 提取文件内容
                extraction_result = self.content_extractor.extract(file_path)
                
                # 2. 基于内容分类
                if extraction_result.text and not extraction_result.error:
                    classification_result = self.content_classifier.classify(
                        extraction_result.text,
                        file_name
                    )
                    
                    # 记录分类结果
                    if self.file_type_recorder:
                        self.file_type_recorder.record(
                            file_name,
                            classification_result,
                            extraction_result.extraction_method.value
                        )
                    
                    return (classification_result.category, classification_result.confidence)
                else:
                    # 内容提取失败，回退到文件名分类
                    print(f"⚠️  内容提取失败 {file_name}: {extraction_result.error}")
                    return self._classify_by_filename(file_path, file_name)
                    
            except Exception as e:
                print(f"⚠️  分类失败 {file_name}: {e}")
                return self._classify_by_filename(file_path, file_name)
        else:
            # 内容提取不可用，使用文件名分类
            return self._classify_by_filename(file_path, file_name)
    
    def _classify_by_filename(self, file_path: str, file_name: str) -> Tuple[FileCategory, float]:
        """根据文件名和扩展名分类文件（原有逻辑）
        
        按优先级规则进行分类，优先级高的规则先匹配
        
        Args:
            file_path: 完整文件路径
            file_name: 文件名
            
        Returns:
            Tuple: (分类, 置信度)
        """
        extension = self._get_file_extension(file_path)
        file_name_lower = file_name.lower()
        
        keyword_match_result = None
        extension_only_result = None
        
        # 按优先级遍历分类规则
        for rule in self.CLASSIFICATION_RULES:
            extensions = rule['extensions']
            
            # 检查扩展名是否匹配
            if extension not in extensions:
                continue
            
            # 检查关键词匹配
            keywords = rule.get('keywords', [])
            keyword_matches = sum(
                1 for kw in keywords 
                if kw.lower() in file_name_lower
            )
            
            if keyword_matches > 0:
                # 关键词匹配，直接返回（优先级最高）
                score = rule['confidence'] * min(1.0, keyword_matches / max(1, len(keywords)))
                return (rule['category'], score)
            
            # 没有关键词匹配，但扩展名匹配
            # 只保存第一个（最高优先级的）扩展名匹配结果
            if extension_only_result is None:
                score = rule['confidence'] * 0.5
                extension_only_result = (rule['category'], score)
        
        # 返回扩展名匹配的结果（如果有的话）
        if extension_only_result is not None:
            return extension_only_result
        
        # 如果没有找到匹配，标记为待确认
        return FileCategory.UNCONFIRMED, 0.0
    
    def scan_directory(self, directory: str = None) -> List[ScannedFile]:
        """扫描目录并分类所有文件
        
        Args:
            directory: 要扫描的目录，默认为初始化时的base_path
            
        Returns:
            List[ScannedFile]: 扫描文件列表
        """
        if directory is None:
            directory = self.base_path
        
        if not os.path.isdir(directory):
            print(f"❌ 目录不存在: {directory}")
            return []
        
        self.scanned_files = []
        
        for root, dirs, files in os.walk(directory):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                
                # 跳过隐藏文件和系统文件
                if file_name.startswith('.') or file_name.startswith('~'):
                    continue
                
                try:
                    # 获取文件信息
                    file_size = os.path.getsize(file_path)
                    mtime = os.path.getmtime(file_path)
                    file_hash = self._calculate_file_hash(file_path)
                    
                    # 分类文件
                    category, confidence = self._classify_file(file_path, file_name)
                    
                    # 创建扫描文件对象
                    scanned = ScannedFile(
                        file_path=file_path,
                        file_name=file_name,
                        file_size=file_size,
                        file_hash=file_hash,
                        mtime=mtime,
                        category=category,
                        confidence=confidence
                    )
                    
                    self.scanned_files.append(scanned)
                    
                except Exception as e:
                    print(f"⚠️  扫描文件失败 {file_path}: {e}")
                    continue
        
        # 保存文件类型记录
        if self.use_content_extraction and self.file_type_recorder:
            self.file_type_recorder.save()
            self.file_type_recorder.print_summary()
        
        return self.scanned_files
    
    def get_summary(self) -> Dict[str, int]:
        """获取分类统计摘要
        
        Returns:
            Dict: 各分类的文件数量
        """
        summary = {}
        
        for scanned in self.scanned_files:
            category_name = scanned.category.value
            summary[category_name] = summary.get(category_name, 0) + 1
        
        return summary
    
    def get_unconfirmed_files(self) -> List[ScannedFile]:
        """获取所有待确认的文件
        
        Returns:
            List[ScannedFile]: 待确认文件列表
        """
        return [
            f for f in self.scanned_files 
            if f.category == FileCategory.UNCONFIRMED
        ]
    
    def get_by_category(self, category: FileCategory) -> List[ScannedFile]:
        """按分类获取文件
        
        Args:
            category: 文件分类
            
        Returns:
            List[ScannedFile]: 该分类的文件列表
        """
        return [f for f in self.scanned_files if f.category == category]
