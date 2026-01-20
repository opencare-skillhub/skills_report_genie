"""文件重命名模块 (v2.0)

根据提取的内容，标准化文件名
命名规则: <date>_<type>_<digest>_<sequence>.<ext>
"""

import os
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class FileRenamer:
    """标准化文件重命名器"""
    
    NAMING_PATTERN = "{date}_{type}_{digest}_{sequence:03d}.{ext}"
    
    # 报告类型映射 (关键词匹配)
    TYPE_MAPPING = {
        # ===== 影像检查 (imaging) =====
        # CT
        "DICOM CT": "CT",
        "CT影像": "CT",
        "CT scan": "CT",
        "CT扫描": "CT",
        "CT": "CT",
        
        # MRI
        "MRI": "MRI",
        "核磁共振": "MRI",
        "磁共振": "MRI",
        
        # 超声
        "超声": "超声",
        "B超": "超声",
        "超声检查": "超声",
        "Ultrasound": "超声",
        
        # X光
        "X光": "X光",
        "X线": "X光",
        "XRay": "X光",
        "胸片": "X光",
        
        # PET-CT
        "PET-CT": "PET-CT",
        "PET": "PET-CT",
        "PET扫描": "PET-CT",
        
        # ===== 检测报告 (lab_reports) =====
        # 血检 - 包含CA199、CEA、白细胞等血液相关指标
        "血液检查": "血检",
        "检验报告": "血检",
        "肿瘤标志物": "血检",
        "血检": "血检",
        "血液": "血检",
        "CA19": "血检",  # CA199、CA19-9等
        "CEA": "血检",
        "AFP": "血检",
        "白细胞": "血检",
        "血红蛋白": "血检",
        "血小板": "血检",
        "肝功能": "血检",
        "肾功能": "血检",
        
        # 病理
        "病理报告": "病理",
        "病理诊断": "病理",
        "病理": "病理",
        "Pathology": "病理",
        "组织学": "病理",
        
        # 遗传/基因 - 关键词: 基因、NGS、DNA、突变等
        "基因检测": "遗传",
        "基因": "遗传",
        "NGS": "遗传",
        "DNA": "遗传",
        "突变": "遗传",
        "Genetic": "遗传",
        "遗传": "遗传",
        "TMB": "遗传",  # Tumor Mutation Burden
        "MSI": "遗传",  # Microsatellite Instability
        
        # ===== 其他分类 =====
        # 病历
        "病历": "病历",
        "病例": "病历",
        "病历记录": "病历",
        "Medical record": "病历",
        "医疗记录": "病历",
        
        # 处方
        "处方": "处方",
        "处方用药": "处方",
        "Prescription": "处方",
        "用药": "处方",
        "药物": "处方",
        "化疗": "处方",
        "放疗": "处方",
        
        # 心理
        "心理": "心理",
        "心理评估": "心理",
        "Psychology": "心理",
        "心理咨询": "心理",
        
        # 营养
        "营养": "营养",
        "营养管理": "营养",
        "Nutrition": "营养",
        "饮食": "营养",
        "进食": "营养",
        
        # 病情说明/医嘱
        "病情说明": "病历",
        "医嘱": "处方",
        "病情介绍": "病历",
    }
    
    def __init__(self, input_dir: str, backup_dir: str):
        """初始化重命名器
        
        Args:
            input_dir: 输入目录
            backup_dir: 备份目录
        """
        self.input_dir = input_dir
        self.backup_dir = backup_dir
        self.mapping = {}  # 原始名 -> 新名
        self.sequence_tracker = {}  # 按日期和类型追踪序列号
        
        os.makedirs(backup_dir, exist_ok=True)
        logger.info("✓ FileRenamer 初始化完成")
    
    def _extract_report_type(self, extraction_result: dict) -> str:
        """提取标准化的报告类型
        
        使用关键词匹配优先于精确匹配，确保识别准确
        
        Args:
            extraction_result: 提取结果
        
        Returns:
            str: 标准化的类型
        """
        raw_data = extraction_result.get('raw_data', {})
        report_type = raw_data.get('report_type', 'Unknown')
        full_text = raw_data.get('full_text', '')
        
        # 首先尝试精确匹配
        if report_type in self.TYPE_MAPPING:
            return self.TYPE_MAPPING[report_type]
        
        # 医学表格特殊识别
        if report_type and '表' in report_type:
            # 检查内容中的肿瘤标志物
            if any(marker in full_text for marker in ['CA199', 'CA-199', 'CEA', 'AFP', '肿瘤标志物']):
                return '血检'  # 肿瘤标志物表
            elif any(marker in full_text for marker in ['HB', 'WBC', '白细胞', '血红蛋白', '血小板']):
                return '血检'  # 血液检查表
        
        # 其次尝试关键词匹配
        combined_text = f"{report_type} {full_text}".lower()
        
        # 优先级顺序很重要 - 更具体的关键词优先
        keyword_priority = [
            # 影像检查
            ("suv=", "CT"),  # SUV是PET-CT的特有指标
            ("ct值", "CT"),
            ("增强扫描", "CT"),
            ("mri", "MRI"),
            ("磁共振", "MRI"),
            ("超声", "超声"),
            ("b超", "超声"),
            ("x光", "X光"),
            ("胸片", "X光"),
            ("影像", "CT"),  # 默认影像为CT
            
            # 检测报告 - 血液指标
            ("ca199", "血检"),
            ("ca19-9", "血检"),
            ("ca50", "血检"),
            ("cea", "血检"),
            ("afp", "血检"),
            ("白细胞", "血检"),
            ("血红蛋白", "血检"),
            ("血小板", "血检"),
            ("肝功能", "血检"),
            ("肾功能", "血检"),
            ("肿瘤标志物", "血检"),
            ("检验", "血检"),
            
            # 遗传/基因
            ("基因", "遗传"),
            ("ngs", "遗传"),
            ("dna", "遗传"),
            ("突变", "遗传"),
            ("tmb", "遗传"),
            ("msi", "遗传"),
            
            # 病理
            ("病理", "病理"),
            ("组织", "病理"),
            
            # 其他
            ("处方", "处方"),
            ("用药", "处方"),
            ("化疗", "处方"),
            ("心理", "心理"),
            ("营养", "营养"),
            ("饮食", "营养"),
        ]
        
        for keyword, std_type in keyword_priority:
            if keyword in combined_text:
                return std_type
        
        # 查询映射表中的所有关键词
        for mapped_keyword, std_type in self.TYPE_MAPPING.items():
            if mapped_keyword.lower() in combined_text:
                return std_type
        
        # 默认返回Unknown（会被后续逻辑拒绝）
        return "Unknown"
    
    def _extract_report_date(self, extraction_result: dict) -> str:
        """提取报告日期
        
        Args:
            extraction_result: 提取结果
        
        Returns:
            str: YYYY-MM-DD 格式的日期
        """
        raw_data = extraction_result.get('raw_data', {})
        report_date = raw_data.get('report_date', '')
        
        # 验证日期格式
        if report_date and len(report_date) == 10:
            try:
                datetime.strptime(report_date, '%Y-%m-%d')
                return report_date
            except ValueError:
                pass
        
        # 默认使用当前日期
        logger.warning(f"  ⚠️  无效的日期格式: {report_date}，使用系统日期")
        return datetime.now().strftime('%Y-%m-%d')
    
    def _generate_digest(self, extraction_result: dict) -> str:
        """从诊断或摘要生成摘要
        
        Args:
            extraction_result: 提取结果
        
        Returns:
            str: 内容摘要 (4-10个字)
        """
        raw_data = extraction_result.get('raw_data', {})
        
        # 优先使用诊断
        diagnosis = raw_data.get('diagnosis', '')
        if diagnosis:
            # 提取前4-10个字
            digest = diagnosis[:8].replace(' ', '').replace('\n', '')
            if len(digest) > 2:
                return digest
        
        # 次优先使用摘要
        summary = raw_data.get('summary', '')
        if summary:
            digest = summary[:8].replace(' ', '').replace('\n', '')
            if len(digest) > 2:
                return digest
        
        # 使用报告类型
        report_type = raw_data.get('report_type', 'Unknown')
        return report_type[:6]
    
    def _get_sequence_number(self, date: str, report_type: str) -> int:
        """获取同日期同类型文件的序列号
        
        Args:
            date: 报告日期 (YYYY-MM-DD)
            report_type: 报告类型
        
        Returns:
            int: 序列号 (从1开始)
        """
        key = f"{date}_{report_type}"
        if key not in self.sequence_tracker:
            self.sequence_tracker[key] = 0
        
        self.sequence_tracker[key] += 1
        return self.sequence_tracker[key]
    
    def _backup_original(self, src_path: str, new_name: str):
        """备份原始文件
        
        Args:
            src_path: 源文件路径
            new_name: 新文件名
        """
        try:
            backup_path = os.path.join(self.backup_dir, os.path.basename(src_path))
            shutil.copy2(src_path, backup_path)
            logger.debug(f"  备份: {backup_path}")
        except Exception as e:
            logger.warning(f"  备份失败: {e}")
    
    def rename_file(self,
                   file_path: str,
                   extraction_result: dict) -> str:
        """重命名单个文件
        
        Args:
            file_path: 原始文件路径
            extraction_result: 提取的结构化数据
        
        Returns:
            str: 新文件名
        """
        try:
            original_name = os.path.basename(file_path)
            
            # 提取各字段
            date = self._extract_report_date(extraction_result)
            report_type = self._extract_report_type(extraction_result)
            digest = self._generate_digest(extraction_result)
            sequence = self._get_sequence_number(date, report_type)
            
            # 获取扩展名
            ext = os.path.splitext(file_path)[1].lstrip('.').lower()
            
            # 生成新名
            new_name = self.NAMING_PATTERN.format(
                date=date,
                type=report_type,
                digest=digest,
                sequence=sequence,
                ext=ext
            )
            
            # 备份原文件
            self._backup_original(file_path, new_name)
            
            # 记录映射
            self.mapping[original_name] = new_name
            
            logger.info(f"  重命名: {original_name} → {new_name}")
            return new_name
            
        except Exception as e:
            logger.error(f"  重命名失败: {e}")
            return os.path.basename(file_path)
    
    def rename_files_in_directory(self,
                                  parse_results: Dict) -> Dict[str, str]:
        """重命名目录中的所有文件
        
        Args:
            parse_results: 所有文件的解析结果
        
        Returns:
            Dict[str, str]: {原始路径: 新文件名}
        """
        files_to_move = {}
        
        logger.info(f"\n开始重命名 {len(parse_results)} 个文件...\n")
        
        for i, (file_path, result) in enumerate(parse_results.items(), 1):
            
            if result.success and result.extraction_result:
                new_name = self.rename_file(
                    file_path,
                    result.extraction_result
                )
                files_to_move[file_path] = new_name
            else:
                logger.warning(f"解析失败，跳过: {os.path.basename(file_path)}")
        
        logger.info(f"\n✓ 重命名完成: {len(files_to_move)}/{len(parse_results)}")
        
        return files_to_move
    
    def save_mapping_log(self, output_path: str):
        """保存文件名映射日志
        
        Args:
            output_path: 输出文件路径
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("文件重命名映射日志\n")
            f.write(f"生成时间: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            
            for original, new in sorted(self.mapping.items()):
                f.write(f"{original} → {new}\n")
            
            f.write(f"\n总计: {len(self.mapping)} 个文件\n")
        
        logger.info(f"✓ 映射日志已保存: {output_path}")
    
    def get_mapping(self) -> Dict[str, str]:
        """获取文件名映射
        
        Returns:
            Dict[str, str]: 映射字典
        """
        return self.mapping.copy()
