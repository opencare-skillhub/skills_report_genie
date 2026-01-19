"""
风险分层模块
根据病理类型、分化程度、标志物进行综合风险评分
参考: PATHOLOGY_ANALYSIS_BEST_PRACTICES.md - 第3部分
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class RiskStratificationResult:
    """风险分层结果"""
    level: str  # 极高危/高危/中危/低危
    score: int  # 风险评分
    factors: List[str]  # 风险因素列表
    treatment_intensity: str  # 治疗强度建议


class RiskStratifier:
    """
    风险分层器
    根据病理学、分子特征进行综合风险评分
    参考: PATHOLOGY_ANALYSIS_BEST_PRACTICES.md 第3章
    """
    
    def __init__(self):
        """初始化风险评分规则"""
        self.cancer_type_scores = self._init_cancer_type_scores()
        self.grade_scores = self._init_grade_scores()
        self.marker_scores = self._init_marker_scores()
    
    def _init_cancer_type_scores(self) -> Dict[str, int]:
        """
        初始化癌肿类型基础分数
        参考: PATHOLOGY_ANALYSIS_BEST_PRACTICES.md lines 109-118
        """
        return {
            "pancreatic_ductal_adenocarcinoma": 100,  # 导管腺癌
            "squamous_cell_carcinoma": 90,  # 鳞癌
            "undifferentiated_carcinoma": 90,  # 未分化癌
            "pancreatic_small_cell_carcinoma": 80,  # 小细胞癌
            "pancreatic_neuroendocrine_tumor": 80,  # 神经内分泌肿瘤
            "serous_cystadenocarcinoma": 50,  # 浆液性囊腺癌
            "mucinous_cystic_neoplasm": 60,  # 粘液性囊肿瘤
            "intraductal_papillary_mucinous_neoplasm": 70,  # IPMN
            "acinar_cell_carcinoma": 50,  # 腺泡细胞癌
        }
    
    def _init_grade_scores(self) -> Dict[str, int]:
        """初始化分化程度评分"""
        return {
            "I": 0,      # 高分化
            "II": 15,    # 中分化
            "III": 30,   # 低分化
        }
    
    def _init_marker_scores(self) -> Dict[str, int]:
        """
        初始化标志物评分
        参考: PATHOLOGY_ANALYSIS_BEST_PRACTICES.md lines 114-117
        """
        return {
            "S100P_high": 20,
            "E-cadherin_negative": 25,
            "IMP3_positive": 20,
            "Ki-67_high": 20,
            "MUC1_positive": 20,
            "claudin18_positive": -10,  # 负分（改善预后）
            "HER2_positive": -5,  # 负分（可靶向治疗）
            "MSI_H": -10,  # 负分（免疫治疗敏感）
        }
    
    def stratify_risk(
        self, 
        cancer_type: Optional[Dict[str, Any]],
        grade: Optional[Dict[str, Any]],
        markers: Dict[str, str]
    ) -> RiskStratificationResult:
        """
        风险分层
        
        Args:
            cancer_type: 癌肿类型信息
            grade: 分化程度信息
            markers: 标志物字典
        
        Returns:
            RiskStratificationResult: 风险分层结果
        
        Example:
            >>> stratifier = RiskStratifier()
            >>> cancer_type = {"chinese_name": "胰腺导管腺癌"}
            >>> grade = {"name": "中分化"}
            >>> markers = {"S100P": "high", "Ki-67": "high"}
            >>> result = stratifier.stratify_risk(cancer_type, grade, markers)
        """
        score = 0
        factors = []
        
        # 1. 基础分数（根据病理类型）
        if cancer_type:
            type_name = cancer_type.get("chinese_name", "")
            # 查找匹配的癌肿类型
            for key, base_score in self.cancer_type_scores.items():
                if key.replace("_", "") in type_name.replace("（", "").replace("）", ""):
                    score += base_score
                    factors.append(f"病理类型：{type_name}")
                    break
            else:
                # 如果没有精确匹配，检查关键词
                if "导管腺癌" in type_name:
                    score += self.cancer_type_scores["pancreatic_ductal_adenocarcinoma"]
                elif "鳞癌" in type_name or "未分化" in type_name:
                    score += 90
                elif "神经内分泌" in type_name or "小细胞" in type_name:
                    score += 80
                else:
                    score += 50
                factors.append(f"病理类型：{type_name}")
        
        # 2. 分化程度调整
        if grade:
            grade_name = grade.get("name", "")
            grade_key = grade.get("grade_key")
            
            if grade_key and grade_key in self.grade_scores:
                grade_score = self.grade_scores[grade_key]
            elif "低分化" in grade_name:
                grade_score = 30
            elif "中分化" in grade_name:
                grade_score = 15
            else:
                grade_score = 0
            
            score += grade_score
            if grade_score > 0:
                factors.append(f"分化程度：{grade_name}")
        
        # 3. 高危标志物评分
        marker_effects = self._score_markers(markers)
        score += marker_effects["total_score"]
        factors.extend(marker_effects["factors"])
        
        # 4. 风险分层
        if score >= 130:
            level = "极高危"
            treatment_intensity = (
                "强化多学科综合治疗：\n"
                "优先考虑新型方案(FOLFIRINOX/mFOLFIRINOX)、靶向治疗、免疫治疗组合"
            )
        elif score >= 100:
            level = "高危"
            treatment_intensity = (
                "积极治疗：\n"
                "标准化疗+靶向治疗(如claudin18+/HER2+)，或新型化疗方案"
            )
        elif score >= 70:
            level = "中危"
            treatment_intensity = (
                "标准治疗：\n"
                "吉西他滨+顺铂或FOLFIRINOX，根据靶点决定是否加靶向治疗"
            )
        else:
            level = "低危"
            treatment_intensity = (
                "个体化治疗：\n"
                "手术优先，必要时辅助化疗"
            )
        
        return RiskStratificationResult(
            level=level,
            score=score,
            factors=factors,
            treatment_intensity=treatment_intensity
        )
    
    def _score_markers(self, markers: Dict[str, str]) -> Dict[str, Any]:
        """
        计算标志物对风险评分的影响
        
        Returns:
            包含总分和因素列表的字典
        """
        total_score = 0
        factors = []
        
        # 高危标志物检查
        if markers.get("S100P") in ["high", "positive"]:
            total_score += 20
            factors.append("S100P高表达")
        
        if markers.get("E-cadherin") == "negative":
            total_score += 25
            factors.append("E-cadherin丧失（高侵袭性）")
        
        if markers.get("IMP3") in ["positive", "high"]:
            total_score += 20
            factors.append("IMP3阳性")
        
        if markers.get("Ki-67") == "high":  # > 30%
            total_score += 20
            factors.append("Ki-67高表达(>30%)")
        elif markers.get("Ki-67") == "moderate":  # 20-30%
            total_score += 10
            factors.append("Ki-67中等水平(20-30%)")
        
        if markers.get("MUC1") in ["high", "positive"]:
            total_score += 20
            factors.append("MUC1高表达")
        
        # 改善预后的标志物（负分）
        if markers.get("claudin18") in ["positive", "high"]:
            total_score -= 10
            factors.append("claudin18阳性（可靶向治疗）")
        
        if markers.get("HER2") in ["positive", "high"]:
            total_score -= 5
            factors.append("HER2阳性（可靶向治疗）")
        
        if markers.get("MSI") == "MSI-H":
            total_score -= 10
            factors.append("MSI-H（免疫治疗敏感）")
        
        # 神经内分泌肿瘤特殊评分
        if markers.get("Ki-67") == "very_high":  # > 20% for NET
            total_score += 30
            factors.append("Ki-67极高（G3 NET，需紧急治疗）")
        
        return {
            "total_score": total_score,
            "factors": factors
        }
    
    def generate_treatment_recommendations(
        self,
        risk_level: str,
        cancer_type: Optional[Dict[str, Any]],
        markers: Dict[str, str]
    ) -> List[str]:
        """
        根据风险等级和标志物生成治疗建议
        
        Args:
            risk_level: 风险等级
            cancer_type: 癌肿类型
            markers: 标志物
        
        Returns:
            治疗建议列表
        """
        recommendations = []
        
        # 基于风险等级的建议
        if risk_level == "极高危":
            recommendations.extend([
                "需进行多学科讨论(MDT)",
                "优先考虑FOLFIRINOX或mFOLFIRINOX方案",
                "评估是否符合临床试验条件",
            ])
        elif risk_level == "高危":
            recommendations.extend([
                "启动积极治疗方案",
                "标准化疗+靶向/免疫治疗",
            ])
        elif risk_level == "中危":
            recommendations.extend([
                "标准化疗方案",
                "定期评估治疗响应",
            ])
        else:
            recommendations.extend([
                "可考虑手术优先",
                "定期监测",
            ])
        
        # 基于特定标志物的建议
        if markers.get("claudin18") in ["positive", "high"]:
            recommendations.append("claudin18阳性：优先考虑claudin18靶向治疗")
        
        if markers.get("HER2") in ["positive", "high"]:
            recommendations.append("HER2阳性：优先考虑HER2靶向治疗")
        
        if markers.get("MSI") == "MSI-H":
            recommendations.append("MSI-H：优先考虑PD-1/PD-L1抑制剂免疫治疗")
        
        if markers.get("E-cadherin") == "negative":
            recommendations.append("E-cadherin丧失：考虑强化治疗方案")
        
        # 神经内分泌肿瘤建议
        if markers.get("SYN") == "positive" or markers.get("Cg") == "positive":
            if markers.get("Ki-67") == "very_high":
                recommendations.append("⚠️ G3神经内分泌癌：需紧急化疗（铂类+依托泊苷）")
            else:
                recommendations.append("神经内分泌肿瘤：考虑生长抑素类似物治疗")
        
        recommendations.append("建议参加相关临床试验")
        
        return recommendations
    
    def to_dict(self, result: RiskStratificationResult) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(result)
    
    def to_json(self, result: RiskStratificationResult) -> str:
        """转换为JSON格式"""
        data = asdict(result)
        return json.dumps(data, ensure_ascii=False, indent=2)
