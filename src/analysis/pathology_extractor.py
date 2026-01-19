"""
病理特征提取模块
从病理报告中自动提取癌肿类型、分化程度、标志物信息
参考: GENETIC_PATHOLOGY_GUIDE.md - 第1.2部分
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class PathologyFeatures:
    """病理特征数据类"""
    cancer_type: Optional[Dict[str, Any]]
    differentiation_grade: Optional[Dict[str, Any]]
    treatment_considerations: List[str]
    trial_keywords: List[str]
    multi_marker_analysis: Optional[Dict[str, Any]]
    risk_stratification: Optional[Dict[str, Any]]


class PathologyFeatureExtractor:
    """
    病理特征提取器
    从原始病理报告提取关键特征用于临床决策
    """
    
    def __init__(self):
        """初始化病理特征库"""
        self.pathology_db = self._init_pathology_db()
        self.grade_db = self._init_grade_db()
        self.marker_db = self._init_marker_db()
    
    def _init_pathology_db(self) -> Dict[str, Dict[str, Any]]:
        """
        初始化胰腺肿瘤分类库（基于WHO分类和免疫表达谱）
        参考: GENETIC_PATHOLOGY_GUIDE.md lines 152-251
        """
        return {
            # ===== 外分泌肿瘤 =====
            "pancreatic_ductal_adenocarcinoma": {
                "chinese_name": "胰腺导管腺癌",
                "category": "外分泌肿瘤",
                "characteristics": "起源于胰管上皮，是最常见的胰腺癌类型（>85%）",
                "immunophenotype": "CK7+, CK8+, CK13+, CK18+, CK19+, CEA+, S100P+, MUC1+, MUC3+, MUC5/6+, CA19-9+, CA125+, claudin-4+",
                "chemotherapy_sensitivity": "中等敏感，对吉西他滨+顺铂有一定敏感性",
                "prognosis": "预后差，5年生存率<10%，与TNM分期和分化程度密切相关",
                "special_consideration": "需重点监测CA19-9和CA50，多指标联合判断；关注特殊标志物表达用于靶向治疗",
                "key_markers": ["CA19-9", "CA50", "CA125", "CK19", "S100P", "claudin18", "HER2"],
                "treatment_options": ["吉西他滨+顺铂化疗", "FOLFIRINOX方案", "靶向治疗(claudin18/HER2等)", "免疫治疗"]
            },
            "serous_cystadenocarcinoma": {
                "chinese_name": "浆液性囊腺癌",
                "category": "外分泌肿瘤",
                "characteristics": "起源于浆液性囊泡，罕见(<5%)",
                "immunophenotype": "CK7+, CK8+, CK18+, CK19+, EMA+, CK20-, CA19.9-",
                "chemotherapy_sensitivity": "相对较敏感",
                "prognosis": "预后相对较好，多数为低度恶性",
                "special_consideration": "通常发现时为早期，预后优于导管腺癌",
                "key_markers": ["CK7", "CK19"],
                "treatment_options": ["手术切除", "辅助化疗"]
            },
            "mucinous_cystic_neoplasm": {
                "chinese_name": "粘液性囊性肿瘤（伴异型增生）",
                "category": "外分泌肿瘤",
                "characteristics": "囊性肿瘤，可从低级别异型增生进展至癌",
                "immunophenotype": "CK7+, CK8+, CK18+, CK19+, EMA+, S100P+, CEA+, CA19.9+, CK20-",
                "chemotherapy_sensitivity": "中等敏感",
                "prognosis": "预后取决于分化程度，高级别异型增生患者预后差",
                "special_consideration": "需监测CA19-9和CEA；囊内液CEA水平可评估恶变风险",
                "key_markers": ["CA19-9", "CEA", "CK19"],
                "treatment_options": ["手术切除", "辅助化疗（高级别异型增生）"]
            },
            "intraductal_papillary_mucinous_neoplasm": {
                "chinese_name": "导管内乳头状粘液肿瘤（IPMN）",
                "category": "外分泌肿瘤",
                "characteristics": "导管内乳头状病变，具有癌变潜能",
                "immunophenotype": "CK7+, CK8+, CK18+, S100P+, 可表达CK19/CA19.9/CK20/CEA",
                "chemotherapy_sensitivity": "取决于是否发生癌变",
                "prognosis": "预后取决于分化程度和浸润程度",
                "special_consideration": "需定期影像学监测；主型IPMN癌变风险>70%；分支型IPMN癌变风险<15%",
                "key_markers": ["CA19-9", "CK7", "S100P"],
                "treatment_options": ["定期监测", "手术切除（高风险患者）", "辅助化疗（已癌变）"]
            },
            # ===== 内分泌肿瘤 =====
            "pancreatic_neuroendocrine_tumor": {
                "chinese_name": "胰腺神经内分泌肿瘤（NET）",
                "category": "内分泌肿瘤",
                "characteristics": "起源于胰岛细胞，分化程度高",
                "immunophenotype": "CK8+, CK18+, CK19+, CD56+, 嗜铬粒蛋白+, 突触素+",
                "chemotherapy_sensitivity": "G1/G2: 相对低敏感；G3: 敏感性高",
                "prognosis": "取决于分级(G1/G2/G3)和分期，G1预后最好",
                "special_consideration": "需进行WHO 2019分级；分泌功能测定；血清学标志物检测",
                "key_markers": ["CK8", "嗜铬粒蛋白", "突触素", "Ki-67"],
                "treatment_options": ["手术切除", "生长抑素类似物", "化疗(G3)", "靶向治疗(everolimus/sunitinib)"]
            },
            "pancreatic_small_cell_carcinoma": {
                "chinese_name": "胰腺小细胞癌（G3神经内分泌癌）",
                "category": "内分泌肿瘤",
                "characteristics": "高度恶性，神经内分泌分化，Ki-67>20%",
                "immunophenotype": "CD56+, 嗜铬粒蛋白+, 突触素+, CK8/18+, NSE+",
                "chemotherapy_sensitivity": "高度敏感，对铂类和依托泊苷敏感",
                "prognosis": "预后极差，平均生存期<2年",
                "special_consideration": "需尽早化疗；可考虑PD-L1表达状态用于免疫治疗评估",
                "key_markers": ["嗜铬粒蛋白", "Ki-67(>20%)", "CD56"],
                "treatment_options": ["铂类+依托泊苷化疗", "免疫治疗(PD-L1+患者)"]
            },
        }
    
    def _init_grade_db(self) -> Dict[str, Dict[str, Any]]:
        """初始化分化程度库"""
        return {
            "I": {
                "name": "高分化",
                "meaning": "细胞形态接近正常，恶性程度低",
                "clinical_significance": "细胞增殖缓慢，相对预后较好",
                "treatment": "可考虑个体化治疗",
                "clinical_trial_keyword": ""
            },
            "II": {
                "name": "中分化",
                "meaning": "细胞形态中等异型",
                "clinical_significance": "中等恶性程度，预后中等",
                "treatment": "标准治疗方案",
                "clinical_trial_keyword": ""
            },
            "III": {
                "name": "低分化",
                "meaning": "细胞形态高度异型，难以识别原来的细胞类型",
                "clinical_significance": "高度恶性，预后差",
                "treatment": "需强化治疗方案",
                "clinical_trial_keyword": ""
            }
        }
    
    def _init_marker_db(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        初始化标志物库
        参考: GENETIC_PATHOLOGY_GUIDE.md lines 257-330
        """
        return {
            "claudin18": {
                "positive": {
                    "meaning": "claudin18表达增高",
                    "clinical_significance": "胰腺腺癌特异标志物，提示可用靶向治疗",
                    "treatment": "claudin18靶向药物（anetumab ravtansine等）",
                    "clinical_trial_keyword": "claudin18+"
                },
                "negative": {
                    "meaning": "claudin18不表达",
                    "clinical_significance": "标准腺癌表型",
                    "treatment": "标准化疗为主",
                    "clinical_trial_keyword": ""
                }
            },
            "HER2": {
                "positive": {
                    "meaning": "HER2过度表达或基因扩增",
                    "clinical_significance": "靶向治疗标志物",
                    "treatment": "HER2靶向药物（trastuzumab等）",
                    "clinical_trial_keyword": "HER2+"
                },
                "negative": {
                    "meaning": "HER2不表达",
                    "clinical_significance": "无HER2靶向治疗指征",
                    "treatment": "标准化疗",
                    "clinical_trial_keyword": ""
                }
            },
            "MSI": {
                "MSI-H": {
                    "meaning": "微卫星不稳定高表达",
                    "clinical_significance": "免疫治疗敏感标志物",
                    "treatment": "PD-1/PD-L1抑制剂优先考虑",
                    "clinical_trial_keyword": "MSI-H"
                },
                "MSS": {
                    "meaning": "微卫星稳定",
                    "clinical_significance": "免疫不敏感",
                    "treatment": "标准化疗为主",
                    "clinical_trial_keyword": ""
                }
            },
            "S100P": {
                "high": {
                    "meaning": "S100P高表达",
                    "clinical_significance": "高侵袭性和不良预后的标志",
                    "treatment": "强化化疗方案（FOLFIRINOX优先）",
                    "clinical_trial_keyword": "S100P+"
                },
                "low": {
                    "meaning": "S100P低表达",
                    "clinical_significance": "相对预后较好",
                    "treatment": "标准化疗",
                    "clinical_trial_keyword": ""
                }
            },
            "Ki-67": {
                "high": {
                    "meaning": "Ki-67 >30% (高增殖指数)",
                    "clinical_significance": "细胞增殖活性强，恶性程度高，预后差",
                    "treatment": "强化治疗方案（多学科综合治疗）",
                    "clinical_trial_keyword": "Ki-67+high"
                },
                "moderate": {
                    "meaning": "Ki-67 20-30%",
                    "clinical_significance": "中等增殖活性",
                    "treatment": "标准化疗强度",
                    "clinical_trial_keyword": ""
                },
                "low": {
                    "meaning": "Ki-67 <20%",
                    "clinical_significance": "细胞增殖缓慢，相对预后较好",
                    "treatment": "可考虑个体化治疗",
                    "clinical_trial_keyword": ""
                }
            },
            "CA19-9": {
                "elevated": {
                    "meaning": "CA19-9升高",
                    "clinical_significance": "肿瘤标志物升高，需多标志物联合判断",
                    "treatment": "与其他标志物联合分析",
                    "clinical_trial_keyword": "CA19-9+"
                },
                "normal": {
                    "meaning": "CA19-9正常",
                    "clinical_significance": "肿瘤标志物在正常范围",
                    "treatment": "继续常规监测",
                    "clinical_trial_keyword": ""
                }
            },
            "CA50": {
                "elevated": {
                    "meaning": "CA50升高",
                    "clinical_significance": "与CA19-9同升高提示肿瘤进展",
                    "treatment": "多标志物联合判断",
                    "clinical_trial_keyword": "CA50+"
                },
                "normal": {
                    "meaning": "CA50正常",
                    "clinical_significance": "肿瘤标志物在正常范围",
                    "treatment": "继续常规监测",
                    "clinical_trial_keyword": ""
                }
            },
            "CA125": {
                "elevated": {
                    "meaning": "CA125升高",
                    "clinical_significance": "腹膜反应标志物，与CA19-9同升高提示腹膜转移风险",
                    "treatment": "评估腹膜播散状态",
                    "clinical_trial_keyword": "CA125+"
                },
                "normal": {
                    "meaning": "CA125正常",
                    "clinical_significance": "无腹膜反应迹象",
                    "treatment": "继续常规监测",
                    "clinical_trial_keyword": ""
                }
            },
            "E-cadherin": {
                "positive": {
                    "meaning": "E-钙粘蛋白表达正常",
                    "clinical_significance": "细胞黏附完整，侵袭性相对低",
                    "treatment": "相对预后较好",
                    "clinical_trial_keyword": ""
                },
                "negative": {
                    "meaning": "E-钙粘蛋白表达降低/丧失",
                    "clinical_significance": "细胞黏附降低，侵袭性和转移能力增强",
                    "treatment": "高风险患者，需强化治疗",
                    "clinical_trial_keyword": "E-cadherin-"
                }
            },
            "IMP3": {
                "positive": {
                    "meaning": "IMP3表达增高",
                    "clinical_significance": "与侵袭性和预后不良相关，高表达患者预后差",
                    "treatment": "强化治疗方案，考虑靶向/免疫治疗",
                    "clinical_trial_keyword": "IMP3+"
                },
                "negative": {
                    "meaning": "IMP3表达不高",
                    "clinical_significance": "相对预后较好",
                    "treatment": "标准治疗方案",
                    "clinical_trial_keyword": ""
                }
            }
        }
    
    def extract_pathology(self, pathology_report: Dict[str, Any]) -> PathologyFeatures:
        """
        从病理报告提取关键特征
        
        Args:
            pathology_report: 病理检测报告字典，包含：
                - primary_pathology: 主要病理类型
                - differentiation_grade: 分化程度 (I/II/III)
                - special_markers: 特殊标志物字典
        
        Returns:
            PathologyFeatures: 提取的病理特征对象
            
        Example:
            >>> report = {
            ...     "primary_pathology": "pancreatic_ductal_adenocarcinoma",
            ...     "differentiation_grade": "II",
            ...     "special_markers": {"claudin18": "positive", "HER2": "negative", "MSI": "MSS"}
            ... }
            >>> extractor = PathologyFeatureExtractor()
            >>> features = extractor.extract_pathology(report)
        """
        extracted = {
            "cancer_type": None,
            "differentiation_grade": None,
            "treatment_considerations": [],
            "trial_keywords": [],
            "multi_marker_analysis": None,
            "risk_stratification": None
        }
        
        # 提取癌肿类型
        cancer_type_key = pathology_report.get("primary_pathology")
        if cancer_type_key in self.pathology_db:
            extracted["cancer_type"] = self.pathology_db[cancer_type_key]
        
        # 提取分化程度
        grade = pathology_report.get("differentiation_grade")
        if grade in self.grade_db:
            extracted["differentiation_grade"] = self.grade_db[grade]
        
        # 提取特殊标志物
        special_markers = pathology_report.get("special_markers", {})
        for marker, value in special_markers.items():
            if marker in self.marker_db:
                if isinstance(self.marker_db[marker].get(value), dict):
                    marker_info = self.marker_db[marker][value]
                    extracted["treatment_considerations"].append(marker_info["treatment"])
                    if marker_info.get("clinical_trial_keyword"):
                        extracted["trial_keywords"].append(marker_info["clinical_trial_keyword"])
        
        return PathologyFeatures(
            cancer_type=extracted["cancer_type"],
            differentiation_grade=extracted["differentiation_grade"],
            treatment_considerations=extracted["treatment_considerations"],
            trial_keywords=extracted["trial_keywords"],
            multi_marker_analysis=None,  # 由marker_analyzer处理
            risk_stratification=None  # 由risk_stratifier处理
        )
    
    def to_dict(self, features: PathologyFeatures) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(features)
    
    def to_json(self, features: PathologyFeatures) -> str:
        """转换为JSON格式"""
        data = asdict(features)
        return json.dumps(data, ensure_ascii=False, indent=2)
