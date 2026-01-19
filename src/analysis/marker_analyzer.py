"""
多标志物分析模块
实现多标志物同趋势分析，支持综合判断肿瘤进展、腹膜转移等
参考: PATHOLOGY_ANALYSIS_BEST_PRACTICES.md - 第1部分
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class MarkerAnalysisResult:
    """多标志物分析结果"""
    simultaneous_elevation: List[str]
    trend_interpretation: str
    clinical_recommendation: str
    confidence_level: int  # 置信度 1-5 星


class MarkerAnalyzer:
    """
    多标志物分析器
    实现多个肿瘤标志物的同趋势分析和临床决策支持
    参考: PATHOLOGY_ANALYSIS_BEST_PRACTICES.md 第1.1-1.2节
    """
    
    def __init__(self):
        """初始化标志物分析规则"""
        self.tumor_marker_set = {
            "CA19-9", "CA50", "CA125", "CA72-4", "CEA"
        }
        self.neuroendocrine_marker_set = {
            "SYN", "Cg", "CD56", "NSE"
        }
    
    def analyze_multi_markers(self, markers: Dict[str, str]) -> MarkerAnalysisResult:
        """
        多标志物同趋势分析
        参考: PATHOLOGY_ANALYSIS_BEST_PRACTICES.md lines 25-40
        
        Args:
            markers: 标志物及其值的字典，例如：
                {
                    "CA19-9": "positive",
                    "CA50": "positive",
                    "CA125": "normal",
                    "E-cadherin": "negative",
                    "Ki-67": "high"
                }
        
        Returns:
            MarkerAnalysisResult: 多标志物分析结果
        
        Example:
            >>> analyzer = MarkerAnalyzer()
            >>> markers = {"CA19-9": "elevated", "CA50": "elevated"}
            >>> result = analyzer.analyze_multi_markers(markers)
            >>> print(result.trend_interpretation)
        """
        analysis = {
            "simultaneous_elevation": [],
            "trend_interpretation": "",
            "clinical_recommendation": "",
            "confidence_level": 1
        }
        
        # 检查多个肿瘤标志物的同时升高
        elevated_markers = [
            m for m, v in markers.items() 
            if m in self.tumor_marker_set and v in ["positive", "elevated", "high"]
        ]
        
        if len(elevated_markers) >= 2:
            analysis["simultaneous_elevation"] = elevated_markers
            analysis["confidence_level"] = min(len(elevated_markers) + 2, 5)
            
            # 关键组合判断 - 参考 PATHOLOGY_ANALYSIS_BEST_PRACTICES.md lines 27-40
            
            # 1. CA19-9 + CA50 同升高 (最可信)
            if "CA19-9" in elevated_markers and "CA50" in elevated_markers:
                analysis["trend_interpretation"] = "CA19-9 + CA50同升高 → 肿瘤进展可能性↑↑（高度可信）"
                analysis["clinical_recommendation"] = "与CA19-9单独升高相比，可靠性大幅提升，需准备治疗方案调整"
                analysis["confidence_level"] = 5
            
            # 2. CA125与其他标志物同升高 (腹膜转移信号)
            if "CA125" in elevated_markers and len(elevated_markers) >= 2:
                if analysis["trend_interpretation"]:
                    analysis["trend_interpretation"] += "\n"
                analysis["trend_interpretation"] += "CA125与其他标志物同升高 → 腹膜转移风险↑↑↑"
                analysis["clinical_recommendation"] += "\n需评估腹膜播散：腹膜穿刺、CA125序列监测"
                analysis["confidence_level"] = 5
            
            # 3. CA72-4同升高 (分化程度下降)
            if "CA72-4" in elevated_markers and len(elevated_markers) >= 2:
                if analysis["trend_interpretation"]:
                    analysis["trend_interpretation"] += "\n"
                analysis["trend_interpretation"] += "CA72-4同升高 → 肿瘤分化程度下降/侵袭性增强"
                analysis["clinical_recommendation"] += "\n考虑使用更强化的治疗方案"
                analysis["confidence_level"] = 4
            
            # 4. 三指标及以上同升高 (最强势进展证据)
            if len(elevated_markers) >= 3:
                analysis["trend_interpretation"] = f"{' + '.join(elevated_markers)}多指标同升高 → 强势肿瘤进展证据"
                analysis["clinical_recommendation"] = "明确的肿瘤进展信号，需立即调整治疗方案，考虑多学科讨论"
                analysis["confidence_level"] = 5
        
        elif len(elevated_markers) == 1:
            # 单个标志物升高 - 需要排除非肿瘤原因
            marker = elevated_markers[0]
            analysis["simultaneous_elevation"] = elevated_markers
            
            if marker == "CA19-9":
                analysis["trend_interpretation"] = "CA19-9单独升高，CA50/CA125/CA72-4正常"
                analysis["clinical_recommendation"] = (
                    "可能为炎症反应（胰炎、胆囊炎），需除外非肿瘤原因，建议：\n"
                    "1) 复查标志物+CRP/降钙素原\n"
                    "2) 影像学评估"
                )
                analysis["confidence_level"] = 2
            else:
                analysis["trend_interpretation"] = f"{marker}单独升高，其他肿瘤标志物正常"
                analysis["clinical_recommendation"] = "需进一步评估，建议复查和影像学检查"
                analysis["confidence_level"] = 2
        
        else:
            # 没有标志物升高
            analysis["trend_interpretation"] = "肿瘤标志物在正常范围"
            analysis["clinical_recommendation"] = "继续常规监测"
            analysis["confidence_level"] = 5
        
        return MarkerAnalysisResult(
            simultaneous_elevation=analysis["simultaneous_elevation"],
            trend_interpretation=analysis["trend_interpretation"],
            clinical_recommendation=analysis["clinical_recommendation"],
            confidence_level=analysis["confidence_level"]
        )
    
    def analyze_neuroendocrine_markers(self, markers: Dict[str, str]) -> Dict[str, Any]:
        """
        神经内分泌标志物分析
        参考: GENETIC_PATHOLOGY_GUIDE.md lines 258-286
        
        Args:
            markers: 标志物及其值的字典
        
        Returns:
            神经内分泌分化分析结果
        """
        analysis = {
            "is_neuroendocrine": False,
            "markers_present": [],
            "interpretation": "",
            "treatment_strategy": ""
        }
        
        # 检查神经内分泌标志物
        ne_markers = [
            m for m, v in markers.items() 
            if m in self.neuroendocrine_marker_set and v in ["positive", "high"]
        ]
        
        if len(ne_markers) >= 1:
            analysis["is_neuroendocrine"] = True
            analysis["markers_present"] = ne_markers
            
            if "SYN" in ne_markers or "Cg" in ne_markers:
                analysis["interpretation"] = "检测到神经内分泌分化标志物，提示可能为神经内分泌肿瘤"
                analysis["treatment_strategy"] = "考虑神经内分泌肿瘤治疗方案：生长抑素类似物、化疗或靶向治疗"
            
            if "CD56" in ne_markers:
                analysis["interpretation"] = "CD56阳性，神经内分泌分化明确"
                analysis["treatment_strategy"] = "按照神经内分泌肿瘤分级治疗"
        
        return analysis
    
    def validate_marker_consistency(self, markers: Dict[str, str]) -> Dict[str, Any]:
        """
        检验标志物表达的一致性
        用于识别可能的检测错误或矛盾表达
        参考: PATHOLOGY_ANALYSIS_BEST_PRACTICES.md 第7.1节
        
        Args:
            markers: 标志物及其值的字典
        
        Returns:
            一致性检验结果
        """
        issues = {
            "has_issues": False,
            "warnings": [],
            "recommendations": []
        }
        
        # 检查矛盾表达
        # CK7+ 通常应该是 CK20-
        if markers.get("CK7") == "positive" and markers.get("CK20") == "positive":
            issues["has_issues"] = True
            issues["warnings"].append("CK7+ 和 CK20+ 同时阳性，这在胰腺癌中较罕见")
            issues["recommendations"].append("建议病理医生复核诊断")
        
        # 极端Ki-67值
        ki67 = markers.get("Ki-67")
        if ki67 == "very_high":  # Ki-67 > 80%
            issues["has_issues"] = True
            issues["warnings"].append("Ki-67极高 (>80%)，需确认是否为小细胞癌或其他高度恶性肿瘤")
            issues["recommendations"].append("建议复核病理诊断和分级")
        
        # 神经内分泌标志物与分化程度不符
        ne_markers = [m for m in self.neuroendocrine_marker_set if markers.get(m) == "positive"]
        if ne_markers:
            if markers.get("CK7") == "negative" or markers.get("CK19") == "negative":
                issues["has_issues"] = True
                issues["warnings"].append("神经内分泌分化标志物阳性，但典型腺癌标志物阴性，组织学分型需确认")
                issues["recommendations"].append("建议与病理医生沟通确认诊断")
        
        return issues
    
    def to_dict(self, result: MarkerAnalysisResult) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(result)
    
    def to_json(self, result: MarkerAnalysisResult) -> str:
        """转换为JSON格式"""
        data = asdict(result)
        return json.dumps(data, ensure_ascii=False, indent=2)
