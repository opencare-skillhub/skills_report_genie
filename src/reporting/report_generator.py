"""医学报告生成器

集成所有Phase 2-4的模块，从患者数据生成完整的医学报告包：
- 病情报告_完整版.md (医学专业版)
- 患者科普版.md (科普教育版)
- 医学可视化报告.md (可视化版本)
- 问诊清单.md (结构化问题清单)
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

from src.agents.popular_science_agent import PopularScienceAgent
from src.agents.visualization_agent import VisualizationAgent
from src.analysis.pathology_extractor import PathologyFeatureExtractor
from src.analysis.marker_analyzer import MarkerAnalyzer
from src.analysis.risk_stratifier import RiskStratifier
from src.analysis.genetic_extractor import GeneticFeatureExtractor

logger = logging.getLogger(__name__)


class ReportGenerator:
    """医学报告生成器"""
    
    def __init__(self, api_key: Optional[str] = None, output_dir: str = "."):
        """初始化报告生成器
        
        Args:
            api_key: Claude API密钥
            output_dir: 报告输出目录
        """
        self.api_key = api_key
        self.output_dir = output_dir
        
        # 初始化各个模块
        self.science_agent = PopularScienceAgent(api_key=api_key)
        self.viz_agent = VisualizationAgent(api_key=api_key)
        self.pathology_extractor = PathologyFeatureExtractor()
        self.marker_analyzer = MarkerAnalyzer()
        self.risk_stratifier = RiskStratifier()
        self.genetic_extractor = GeneticFeatureExtractor()
        
        logger.info("✓ ReportGenerator 初始化完成")
    
    def generate_all_reports(self, patient_data: Dict) -> Dict[str, str]:
        """生成所有报告
        
        Args:
            patient_data: 患者结构化数据（来自JsonAggregator）
        
        Returns:
            Dict[str, str]: {报告名称: 报告内容}
        """
        reports = {}
        
        try:
            # 1. 生成完整的医学专业版
            logger.info("📝 生成医学专业版报告...")
            reports['完整版'] = self._generate_professional_report(patient_data)
            
            # 2. 生成科普版
            logger.info("🎓 生成患者科普版...")
            reports['科普版'] = self._generate_popular_science_report(patient_data)
            
            # 3. 生成医学可视化报告
            logger.info("📊 生成医学可视化报告...")
            reports['可视化'] = self._generate_visualization_report(patient_data)
            
            # 4. 生成问诊清单
            logger.info("❓ 生成问诊清单...")
            reports['问诊清单'] = self._generate_consultation_checklist(patient_data)
            
            logger.info("✓ 所有报告生成完成")
            
        except Exception as e:
            logger.error(f"❌ 报告生成失败: {e}")
            raise
        
        return reports
    
    def _generate_professional_report(self, patient_data: Dict) -> str:
        """生成医学专业版报告"""
        
        report_parts = []
        
        # 标题
        report_parts.append(f"# 患者病情分析报告")
        report_parts.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_parts.append(f"**版本**: 医学专业版\n")
        
        # 1. 患者基本信息
        report_parts.append(self._section_patient_info(patient_data))
        
        # 2. 病理分析
        if patient_data.get('pathology'):
            report_parts.append(self._section_pathology(patient_data['pathology']))
        
        # 3. 肿瘤标志物分析
        if patient_data.get('markers'):
            report_parts.append(self._section_markers(patient_data['markers']))
        
        # 4. 基因特征分析
        if patient_data.get('genetics'):
            report_parts.append(self._section_genetics(patient_data['genetics']))
        
        # 5. 风险评估
        if patient_data.get('pathology'):
            report_parts.append(self._section_risk_assessment(patient_data))
        
        # 6. 临床试验匹配
        if patient_data.get('clinical_trials'):
            report_parts.append(self._section_clinical_trials(patient_data['clinical_trials']))
        
        # 7. 建议和总结
        report_parts.append(self._section_recommendations(patient_data))
        
        return "\n".join(report_parts)
    
    def _generate_popular_science_report(self, patient_data: Dict) -> str:
        """生成科普版报告"""
        
        try:
            report_parts = []
            
            # 标题
            report_parts.append("# 患者病情科普版说明")
            report_parts.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # 基因科普
            if patient_data.get('genetics'):
                logger.debug("  生成基因科普...")
                genetic_edu = self.science_agent.generate_genetic_education(
                    patient_data['genetics']
                )
                report_parts.append("## 基因检测结果说明\n")
                report_parts.append(genetic_edu)
            
            # 病理科普
            if patient_data.get('pathology'):
                logger.debug("  生成病理科普...")
                pathology_edu = self.science_agent.generate_pathology_education(
                    patient_data['pathology']
                )
                report_parts.append("\n## 病理检查结果说明\n")
                report_parts.append(pathology_edu)
            
            # 治疗科普
            if patient_data.get('treatment_history'):
                logger.debug("  生成治疗科普...")
                treatment_edu = self.science_agent.generate_treatment_education(
                    patient_data['treatment_history']
                )
                report_parts.append("\n## 治疗方案说明\n")
                report_parts.append(treatment_edu)
            
            # 预后科普
            if patient_data.get('risk_profile'):
                logger.debug("  生成预后科普...")
                prognosis_edu = self.science_agent.generate_prognosis_education(
                    patient_data.get('risk_profile', {}),
                    patient_data.get('genetics', {}),
                    patient_data.get('pathology', {})
                )
                report_parts.append("\n## 预后评估说明\n")
                report_parts.append(prognosis_edu)
            
            # 自我管理建议
            logger.debug("  生成自我管理建议...")
            self_care = self.science_agent.generate_patient_self_care(
                patient_data.get('risk_profile', {}),
                patient_data.get('complications', []),
                patient_data.get('genetics', {})
            )
            report_parts.append("\n## 患者自我管理建议\n")
            report_parts.append(self_care)
            
            return "\n".join(report_parts)
            
        except Exception as e:
            logger.warning(f"⚠️ 科普版生成失败，返回基础版本: {e}")
            return f"# 患者科普版\n\n生成失败: {e}"
    
    def _generate_visualization_report(self, patient_data: Dict) -> str:
        """生成医学可视化报告"""
        
        try:
            report_parts = []
            
            # 标题
            report_parts.append("# 医学信息可视化报告")
            report_parts.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # 患者速览卡
            logger.debug("  生成患者速览卡...")
            summary_card = self.viz_agent.design_patient_summary_card(patient_data)
            report_parts.append("## 患者病情速览卡\n")
            report_parts.append(summary_card)
            
            # 风险等级可视化
            if patient_data.get('risk_profile'):
                logger.debug("  生成风险可视化...")
                risk_viz = self.viz_agent.design_risk_profile_visualization(
                    patient_data['risk_profile']
                )
                report_parts.append("\n## 风险等级可视化\n")
                report_parts.append(risk_viz)
            
            # 基因特征表格
            if patient_data.get('genetics'):
                logger.debug("  生成基因特征表...")
                genetic_table = self.viz_agent.design_genetic_features_table(
                    patient_data['genetics']
                )
                report_parts.append("\n## 基因特征一览\n")
                report_parts.append(genetic_table)
            
            # 治疗时间线
            if patient_data.get('treatment_history'):
                logger.debug("  生成治疗时间线...")
                timeline = self.viz_agent.design_treatment_timeline(
                    patient_data['treatment_history']
                )
                report_parts.append("\n## 治疗时间线\n")
                report_parts.append(timeline)
            
            # 标志物趋势
            if patient_data.get('markers'):
                logger.debug("  生成标志物趋势...")
                marker_trend = self.viz_agent.design_marker_trend_narrative(
                    patient_data['markers']
                )
                report_parts.append("\n## 肿瘤标志物趋势\n")
                report_parts.append(marker_trend)
            
            return "\n".join(report_parts)
            
        except Exception as e:
            logger.warning(f"⚠️ 可视化报告生成失败: {e}")
            return f"# 医学可视化报告\n\n生成失败: {e}"
    
    def _generate_consultation_checklist(self, patient_data: Dict) -> str:
        """生成问诊清单"""
        
        try:
            report_parts = []
            
            # 标题
            report_parts.append("# 医生问诊清单")
            report_parts.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # 生成问诊清单
            logger.debug("  生成问诊清单...")
            checklist = self.viz_agent.design_consultation_checklist(
                patient_data.get('genetics', {}),
                patient_data.get('pathology', {}),
                patient_data.get('markers', {}),
                patient_data.get('treatment_history', [])
            )
            report_parts.append(checklist)
            
            return "\n".join(report_parts)
            
        except Exception as e:
            logger.warning(f"⚠️ 问诊清单生成失败: {e}")
            return f"# 医生问诊清单\n\n生成失败: {e}"
    
    def _section_patient_info(self, patient_data: Dict) -> str:
        """患者基本信息章节"""
        
        section = ["## 1. 患者基本信息\n"]
        
        metadata = patient_data.get('metadata', {})
        section.append(f"**患者姓名**: {metadata.get('patient_name', 'N/A')}")
        section.append(f"**年龄**: {metadata.get('age', 'N/A')}")
        section.append(f"**性别**: {metadata.get('gender', 'N/A')}")
        section.append(f"**就诊日期**: {metadata.get('visit_date', 'N/A')}")
        
        return "\n".join(section) + "\n"
    
    def _section_pathology(self, pathology_data: Dict) -> str:
        """病理分析章节"""
        
        section = ["## 2. 病理分析\n"]
        
        section.append(f"**肿瘤类型**: {pathology_data.get('cancer_type', 'N/A')}")
        section.append(f"**分化程度**: {pathology_data.get('differentiation_grade', 'N/A')}")
        
        if pathology_data.get('special_markers'):
            section.append("\n**特殊标志物**:")
            for marker, value in pathology_data['special_markers'].items():
                section.append(f"- {marker}: {value}")
        
        return "\n".join(section) + "\n"
    
    def _section_markers(self, markers_data: Dict) -> str:
        """肿瘤标志物章节"""
        
        section = ["## 3. 肿瘤标志物分析\n"]
        
        if markers_data.get('markers'):
            section.append("| 标志物 | 数值 | 参考范围 | 状态 |")
            section.append("|--------|------|---------|------|")
            
            for marker in markers_data['markers']:
                name = marker.get('name', 'N/A')
                value = marker.get('value', 'N/A')
                ref_range = marker.get('reference_range', 'N/A')
                status = marker.get('status', 'N/A')
                section.append(f"| {name} | {value} | {ref_range} | {status} |")
        
        if markers_data.get('analysis'):
            section.append(f"\n**分析**: {markers_data['analysis']}")
        
        return "\n".join(section) + "\n"
    
    def _section_genetics(self, genetics_data: Dict) -> str:
        """基因特征章节"""
        
        section = ["## 4. 基因特征分析\n"]
        
        if genetics_data.get('driver_genes'):
            section.append("**驱动基因**:")
            for gene in genetics_data['driver_genes']:
                section.append(f"- {gene.get('gene', 'N/A')}: {gene.get('mutation', 'N/A')}")
        
        if genetics_data.get('tumor_suppressor_genes'):
            section.append("\n**抑癌基因**:")
            for gene in genetics_data['tumor_suppressor_genes']:
                section.append(f"- {gene.get('gene', 'N/A')}: {gene.get('mutation', 'N/A')}")
        
        if genetics_data.get('actionable_mutations'):
            section.append("\n**可靶向突变**:")
            for mut in genetics_data['actionable_mutations']:
                section.append(f"- {mut.get('mutation', 'N/A')}: {mut.get('treatment', 'N/A')}")
        
        section.append(f"\n**风险等级**: {genetics_data.get('risk_profile', 'N/A')}")
        
        return "\n".join(section) + "\n"
    
    def _section_risk_assessment(self, patient_data: Dict) -> str:
        """风险评估章节"""
        
        section = ["## 5. 风险评估\n"]
        
        risk = patient_data.get('risk_profile', {})
        section.append(f"**风险等级**: {risk.get('risk_level', 'N/A')}")
        section.append(f"**风险评分**: {risk.get('risk_score', 'N/A')}")
        section.append(f"**治疗强度**: {risk.get('treatment_intensity', 'N/A')}")
        
        if risk.get('treatment_recommendations'):
            section.append("\n**推荐治疗方案**:")
            for rec in risk['treatment_recommendations']:
                section.append(f"- {rec}")
        
        return "\n".join(section) + "\n"
    
    def _section_clinical_trials(self, trials_data: list) -> str:
        """临床试验章节"""
        
        section = ["## 6. 匹配的临床试验\n"]
        
        if trials_data:
            section.append("| 试验ID | 试验名称 | 匹配等级 | 状态 |")
            section.append("|--------|---------|---------|------|")
            
            for trial in trials_data[:10]:  # 显示前10个
                trial_id = trial.get('trial_id', 'N/A')
                name = trial.get('trial_name', 'N/A')[:30]
                match = trial.get('match_level', 'N/A')
                status = trial.get('status', 'N/A')
                section.append(f"| {trial_id} | {name} | {match} | {status} |")
        else:
            section.append("未找到匹配的临床试验。")
        
        return "\n".join(section) + "\n"
    
    def _section_recommendations(self, patient_data: Dict) -> str:
        """建议和总结"""
        
        section = ["## 7. 医学建议和总结\n"]
        
        section.append("### 关键建议")
        section.append("- 定期复查肿瘤标志物")
        section.append("- 遵医嘱进行治疗")
        section.append("- 关注临床试验机会")
        section.append("- 加强营养和心理支持")
        
        section.append("\n### 后续随访计划")
        section.append("- 3个月后复查肿瘤标志物")
        section.append("- 6个月进行影像学评估")
        section.append("- 根据治疗反应调整方案")
        
        return "\n".join(section) + "\n"
    
    def save_reports(self, reports: Dict[str, str], 
                    patient_name: str = "patient") -> Dict[str, str]:
        """保存所有报告
        
        Args:
            reports: 报告字典
            patient_name: 患者名称（用于文件名）
        
        Returns:
            Dict[str, str]: {报告名称: 文件路径}
        """
        
        reports_dir = os.path.join(self.output_dir, "_reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        saved_paths = {}
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        for report_type, content in reports.items():
            filename = f"病情报告_{report_type}_{timestamp}.md"
            filepath = os.path.join(reports_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            saved_paths[report_type] = filepath
            logger.info(f"✓ 报告已保存: {filename}")
        
        return saved_paths
