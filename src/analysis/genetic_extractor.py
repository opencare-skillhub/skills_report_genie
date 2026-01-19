"""
基因特征提取模块
从基因检测报告自动提取驱动基因、抑癌基因、治疗靶点
参考: GENETIC_PATHOLOGY_GUIDE.md - 第1.1部分
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class GeneticFeatures:
    """基因特征数据类"""
    driver_genes: List[Dict[str, Any]]
    tumor_suppressor_genes: List[Dict[str, Any]]
    treatment_targets: List[str]
    risk_profile: str  # 高危/中危/低危
    trial_keywords: List[str]


class GeneticFeatureExtractor:
    """
    基因特征提取器
    从NGS报告提取突变信息并进行临床分类
    参考: GENETIC_PATHOLOGY_GUIDE.md lines 44-124
    """
    
    def __init__(self):
        """初始化基因特征库"""
        self.gene_db = self._init_gene_db()
    
    def _init_gene_db(self) -> Dict[str, Dict[str, Any]]:
        """
        初始化基因知识库
        参考: GENETIC_PATHOLOGY_GUIDE.md lines 47-70
        """
        return {
            "KRAS": {
                "type": "驱动基因",
                "function": "细胞信号传导",
                "common_mutations": ["G12D", "G12V", "G12C", "G12A", "G12R"],
                "actionable_mutations": ["G12C"],  # 可以用sotorasib
                "treatment_directions": [
                    "KRAS抑制剂（G12C特异性：sotorasib、adagrasib）",
                    "MEK抑制剂",
                    "标准化疗"
                ],
                "prognosis": "KRAS突变患者化疗敏感性较差，预后相对较差",
                "trial_keywords": ["KRAS", "KRAS-G12C", "KRAS-G12D", "KRAS-G12V", "MEK抑制剂"]
            },
            "TP53": {
                "type": "抑癌基因",
                "function": "细胞周期调控、DNA修复",
                "common_mutations": ["R248Q", "R175H", "Y234H", "R282Q", "R248W"],
                "actionable_mutations": [],  # 暂无特异性靶向药
                "treatment_directions": [
                    "标准化疗",
                    "免疫治疗（考虑高TMB）",
                    "DNA修复相关药物（如PARPi）"
                ],
                "prognosis": "TP53突变提示预后较差，治疗响应差异大",
                "trial_keywords": ["TP53", "TP53-mutant", "DNA修复", "PARPi"]
            },
            "BRCA1": {
                "type": "DNA修复基因",
                "function": "同源重组修复",
                "common_mutations": ["frameshift", "nonsense", "splice"],
                "actionable_mutations": ["loss"],  # BRCA1/2缺失/突变
                "treatment_directions": [
                    "PARPi（如olaparib、rucaparib）",
                    "铂类化疗（敏感性高）",
                    "免疫治疗"
                ],
                "prognosis": "BRCA1突变患者预后较差但化疗敏感",
                "trial_keywords": ["BRCA1", "PARP抑制剂", "DNA修复"]
            },
            "BRCA2": {
                "type": "DNA修复基因",
                "function": "同源重组修复",
                "common_mutations": ["frameshift", "nonsense", "splice"],
                "actionable_mutations": ["loss"],
                "treatment_directions": [
                    "PARPi（如olaparib、rucaparib）",
                    "铂类化疗（敏感性高）",
                    "免疫治疗"
                ],
                "prognosis": "BRCA2突变患者预后较差但化疗敏感",
                "trial_keywords": ["BRCA2", "PARP抑制剂", "DNA修复"]
            },
            "CDKN2A": {
                "type": "肿瘤抑制基因",
                "function": "细胞周期G1/S检查点",
                "common_mutations": ["deletion", "frameshift", "nonsense"],
                "actionable_mutations": [],
                "treatment_directions": [
                    "CDK4/6抑制剂（实验性）",
                    "标准化疗"
                ],
                "prognosis": "CDKN2A缺失预后相对较差",
                "trial_keywords": ["CDKN2A", "CDK4/6抑制剂"]
            },
            "SMAD4": {
                "type": "信号转导基因",
                "function": "TGF-β信号转导",
                "common_mutations": ["deletion", "nonsense", "frameshift"],
                "actionable_mutations": [],
                "treatment_directions": [
                    "标准化疗",
                    "免疫治疗（结合其他靶点）"
                ],
                "prognosis": "SMAD4缺失与更差的预后相关，转移风险↑↑",
                "trial_keywords": ["SMAD4", "TGF-β通路"]
            },
            "PTEN": {
                "type": "肿瘤抑制基因",
                "function": "PI3K/AKT通路负调控",
                "common_mutations": ["deletion", "nonsense", "frameshift"],
                "actionable_mutations": [],
                "treatment_directions": [
                    "PI3K/AKT/mTOR抑制剂",
                    "标准化疗"
                ],
                "prognosis": "PTEN缺失提示高侵袭性",
                "trial_keywords": ["PTEN", "PI3K抑制剂", "AKT抑制剂"]
            },
            "PIK3CA": {
                "type": "原癌基因",
                "function": "PI3K/AKT信号激活",
                "common_mutations": ["E542K", "E545K", "H1047R"],
                "actionable_mutations": ["E542K", "E545K", "H1047R"],
                "treatment_directions": [
                    "PI3K抑制剂",
                    "AKT抑制剂",
                    "mTOR抑制剂"
                ],
                "prognosis": "PIK3CA突变激活提示信号通路异常",
                "trial_keywords": ["PIK3CA", "PI3K抑制剂", "AKT抑制剂"]
            },
            "PALB2": {
                "type": "DNA修复基因",
                "function": "BRCA2互作，同源重组修复",
                "common_mutations": ["frameshift", "nonsense"],
                "actionable_mutations": ["loss"],
                "treatment_directions": [
                    "PARPi",
                    "铂类化疗"
                ],
                "prognosis": "PALB2突变可能提示PARPi敏感性",
                "trial_keywords": ["PALB2", "PARP抑制剂"]
            },
            "CHEK2": {
                "type": "DNA修复基因",
                "function": "DNA损伤应答",
                "common_mutations": ["1100delC", "frameshift"],
                "actionable_mutations": [],
                "treatment_directions": [
                    "PARPi（部分敏感）",
                    "标准化疗"
                ],
                "prognosis": "CHEK2突变影响化疗敏感性",
                "trial_keywords": ["CHEK2", "DNA修复"]
            },
            "ERBB2": {
                "type": "原癌基因",
                "function": "受体酪氨酸激酶",
                "common_mutations": ["mutation", "amplification"],
                "actionable_mutations": ["amplification", "mutation"],
                "treatment_directions": [
                    "HER2靶向药（trastuzumab等）",
                    "TKI（如lapatinib）",
                    "HER2靶向双特异性抗体"
                ],
                "prognosis": "ERBB2过表达/扩增提示靶向治疗机会",
                "trial_keywords": ["HER2", "ERBB2", "trastuzumab"]
            },
            "EGFR": {
                "type": "原癌基因",
                "function": "受体酪氨酸激酶",
                "common_mutations": ["L858R", "deletion"],
                "actionable_mutations": ["L858R", "deletion"],
                "treatment_directions": [
                    "EGFR TKI（erlotinib等）",
                    "单克隆抗体（cetuximab）"
                ],
                "prognosis": "EGFR突变可能提示TKI敏感性",
                "trial_keywords": ["EGFR", "TKI"]
            },
            "MET": {
                "type": "原癌基因",
                "function": "受体酪氨酸激酶",
                "common_mutations": ["amplification", "exon14跳过"],
                "actionable_mutations": ["amplification", "exon14"],
                "treatment_directions": [
                    "MET抑制剂（crizotinib、cabozantinib等）",
                    "HGF抗体"
                ],
                "prognosis": "MET异常激活与侵袭性增强相关",
                "trial_keywords": ["MET", "MET抑制剂"]
            },
            "RAS": {
                "type": "驱动基因",
                "function": "细胞信号传导",
                "common_mutations": ["G12", "G13", "Q61"],
                "actionable_mutations": ["G12C"],
                "treatment_directions": [
                    "RAS/MAPK通路抑制剂",
                    "标准化疗"
                ],
                "prognosis": "RAS突变高频率，驱动肿瘤进展",
                "trial_keywords": ["RAS", "RAS-G12C", "MAPK抑制剂"]
            },
            "BRAF": {
                "type": "驱动基因",
                "function": "MAPK信号传导",
                "common_mutations": ["V600E", "V600K"],
                "actionable_mutations": ["V600E", "V600K"],
                "treatment_directions": [
                    "BRAF抑制剂（vemurafenib等）",
                    "BRAF+MEK联合抑制"
                ],
                "prognosis": "BRAF V600E突变可能提示BRAF抑制剂敏感",
                "trial_keywords": ["BRAF", "BRAF-V600E", "BRAF抑制剂"]
            },
        }
    
    def extract_mutations(self, genetic_report: Dict[str, Any]) -> GeneticFeatures:
        """
        从遗传学报告提取突变信息
        
        Args:
            genetic_report: 基因检测报告，应包含：
                - test_type: "NGS" 或其他
                - mutations: 突变列表
                  每个突变应包含:
                    - gene: 基因名称
                    - mutation: 突变描述
                    - classification: "驱动基因"/"抑癌基因"等
                    - allele_frequency: 等位基因频率
        
        Returns:
            GeneticFeatures: 提取的基因特征
        
        Example:
            >>> report = {
            ...     "test_type": "NGS",
            ...     "mutations": [
            ...         {"gene": "KRAS", "mutation": "G12D", "classification": "驱动基因", "allele_frequency": 45.2},
            ...         {"gene": "TP53", "mutation": "R248Q", "classification": "抑癌基因", "allele_frequency": 42.8}
            ...     ]
            ... }
            >>> extractor = GeneticFeatureExtractor()
            >>> features = extractor.extract_mutations(report)
        """
        extracted = {
            "driver_genes": [],
            "tumor_suppressor_genes": [],
            "dna_repair_genes": [],
            "treatment_targets": set(),
            "risk_profile": "",
            "trial_keywords": set()
        }
        
        for mutation in genetic_report.get("mutations", []):
            gene = mutation.get("gene", "").upper()
            mut_desc = mutation.get("mutation", "")
            mutation_type = mutation.get("classification", "")
            allele_freq = mutation.get("allele_frequency", 0)
            
            if gene in self.gene_db:
                gene_info = self.gene_db[gene]
                
                # 分类和收集
                mutation_entry = {
                    "gene": gene,
                    "mutation": mut_desc,
                    "allele_frequency": allele_freq,
                    "type": gene_info["type"],
                    "function": gene_info["function"],
                    "treatment_directions": gene_info["treatment_directions"],
                    "prognosis": gene_info["prognosis"],
                    "is_actionable": mut_desc in gene_info.get("actionable_mutations", [])
                }
                
                # 按基因类型分类
                if gene_info["type"] == "驱动基因":
                    extracted["driver_genes"].append(mutation_entry)
                elif gene_info["type"] == "DNA修复基因":
                    # DNA修复基因（BRCA1/2等）通常作为抑癌基因类别
                    extracted["tumor_suppressor_genes"].append(mutation_entry)
                    extracted["dna_repair_genes"] = extracted.get("dna_repair_genes", [])
                    extracted["dna_repair_genes"].append(mutation_entry)
                else:  # 抑癌基因、肿瘤抑制基因、原癌基因等
                    extracted["tumor_suppressor_genes"].append(mutation_entry)
                
                # 收集治疗方向
                extracted["treatment_targets"].update(gene_info["treatment_directions"])
                
                # 收集临床试验关键词
                extracted["trial_keywords"].update(gene_info["trial_keywords"])
        
        # 判断风险等级
        driver_count = len(extracted["driver_genes"])
        suppressor_count = len(extracted["tumor_suppressor_genes"])
        
        if driver_count >= 2 or (driver_count >= 1 and suppressor_count >= 1):
            extracted["risk_profile"] = "高危"
        elif driver_count >= 1 or suppressor_count >= 1:
            extracted["risk_profile"] = "中危"
        else:
            extracted["risk_profile"] = "低危"
        
        return GeneticFeatures(
            driver_genes=extracted["driver_genes"],
            tumor_suppressor_genes=extracted["tumor_suppressor_genes"],
            treatment_targets=list(extracted["treatment_targets"]),
            risk_profile=extracted["risk_profile"],
            trial_keywords=list(extracted["trial_keywords"])
        )
    
    def identify_actionable_mutations(self, features: GeneticFeatures) -> Dict[str, Any]:
        """
        识别可以进行靶向治疗的突变
        
        Returns:
            可靶向突变列表和对应的治疗方案
        """
        actionable = {
            "mutations": [],
            "targeted_therapies": []
        }
        
        # 检查驱动基因
        for gene_mut in features.driver_genes:
            if gene_mut.get("is_actionable"):
                actionable["mutations"].append({
                    "gene": gene_mut["gene"],
                    "mutation": gene_mut["mutation"],
                    "treatments": gene_mut["treatment_directions"]
                })
                actionable["targeted_therapies"].extend(gene_mut["treatment_directions"])
        
        # 检查肿瘤抑制基因
        for gene_mut in features.tumor_suppressor_genes:
            if gene_mut.get("is_actionable"):
                actionable["mutations"].append({
                    "gene": gene_mut["gene"],
                    "mutation": gene_mut["mutation"],
                    "treatments": gene_mut["treatment_directions"]
                })
                actionable["targeted_therapies"].extend(gene_mut["treatment_directions"])
        
        # 去重
        actionable["targeted_therapies"] = list(set(actionable["targeted_therapies"]))
        
        return actionable
    
    def to_dict(self, features: GeneticFeatures) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(features)
    
    def to_json(self, features: GeneticFeatures) -> str:
        """转换为JSON格式"""
        data = asdict(features)
        return json.dumps(data, ensure_ascii=False, indent=2)
