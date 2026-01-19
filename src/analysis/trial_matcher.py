"""
临床试验匹配模块
基于基因特征和病理特征进行双维度智能匹配
参考: GENETIC_PATHOLOGY_GUIDE.md - 第2部分
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json


class MatchType(Enum):
    """匹配类型"""
    PERFECT = 5  # 完全匹配（基因+病理+标志物）
    DUAL = 4     # 双靶点匹配（≥2个靶点）
    SINGLE = 3   # 单靶点匹配
    TYPE = 2     # 肿瘤类型匹配
    NONE = 1     # 无匹配


@dataclass
class TrialMatch:
    """临床试验匹配结果"""
    trial_name: str
    trial_id: str
    match_type: int  # 1-5，5为完全匹配
    genetic_match: bool
    pathology_match: bool
    marker_match: bool
    matched_keywords: List[str]
    match_score: float  # 0-100
    rationale: str  # 匹配理由


class ClinicalTrialMatcher:
    """
    临床试验匹配器
    基于基因+病理特征进行智能匹配
    参考: GENETIC_PATHOLOGY_GUIDE.md 第2部分
    """
    
    def __init__(self):
        """初始化匹配规则"""
        self.mock_trials = self._init_mock_trials()
    
    def _init_mock_trials(self) -> List[Dict[str, Any]]:
        """
        初始化模拟临床试验数据库
        实际部署时将由API.clinicaltrials.gov替代
        """
        return [
            # KRAS-G12C特异性试验
            {
                "trial_id": "NCT0001",
                "trial_name": "KRAS-G12C突变胰腺癌一线治疗 (sotorasib)",
                "condition": "胰腺癌",
                "genetic_keywords": ["KRAS-G12C", "KRAS"],
                "pathology_keywords": ["adenocarcinoma", "ductal"],
                "marker_keywords": [],
                "status": "RECRUITING"
            },
            {
                "trial_id": "NCT0002",
                "trial_name": "KRAS-G12C突变实体瘤 (adagrasib)",
                "condition": "实体瘤",
                "genetic_keywords": ["KRAS-G12C"],
                "pathology_keywords": [],
                "marker_keywords": [],
                "status": "RECRUITING"
            },
            # claudin18靶向试验
            {
                "trial_id": "NCT0003",
                "trial_name": "claudin18.2阳性胰腺癌 (anetumab ravtansine)",
                "condition": "胰腺癌",
                "genetic_keywords": [],
                "pathology_keywords": ["claudin18+"],
                "marker_keywords": ["claudin18"],
                "status": "RECRUITING"
            },
            # HER2靶向试验
            {
                "trial_id": "NCT0004",
                "trial_name": "HER2阳性胰腺癌 (trastuzumab)",
                "condition": "胰腺癌",
                "genetic_keywords": ["HER2"],
                "pathology_keywords": ["HER2+"],
                "marker_keywords": ["HER2"],
                "status": "RECRUITING"
            },
            # PARP抑制剂试验（BRCA/PALB2突变）
            {
                "trial_id": "NCT0005",
                "trial_name": "BRCA1/2突变胰腺癌 (olaparib)",
                "condition": "胰腺癌",
                "genetic_keywords": ["BRCA1", "BRCA2", "PALB2"],
                "pathology_keywords": ["adenocarcinoma"],
                "marker_keywords": [],
                "status": "RECRUITING"
            },
            # MSI-H免疫治疗试验
            {
                "trial_id": "NCT0006",
                "trial_name": "MSI-H胰腺癌免疫治疗 (pembrolizumab)",
                "condition": "胰腺癌",
                "genetic_keywords": [],
                "pathology_keywords": ["MSI-H"],
                "marker_keywords": ["MSI-H"],
                "status": "RECRUITING"
            },
            # 通用化疗试验
            {
                "trial_id": "NCT0007",
                "trial_name": "转移性胰腺癌 (FOLFIRINOX)",
                "condition": "胰腺癌",
                "genetic_keywords": [],
                "pathology_keywords": ["adenocarcinoma"],
                "marker_keywords": [],
                "status": "RECRUITING"
            },
            # 神经内分泌肿瘤试验
            {
                "trial_id": "NCT0008",
                "trial_name": "胰腺神经内分泌肿瘤 (somatostatin analogue)",
                "condition": "胰腺神经内分泌肿瘤",
                "genetic_keywords": [],
                "pathology_keywords": ["NET", "neuroendocrine"],
                "marker_keywords": ["SYN+", "Cg+"],
                "status": "RECRUITING"
            },
            # PIK3CA靶向试验
            {
                "trial_id": "NCT0009",
                "trial_name": "PIK3CA突变肿瘤 (alpelisib)",
                "condition": "实体瘤",
                "genetic_keywords": ["PIK3CA"],
                "pathology_keywords": [],
                "marker_keywords": [],
                "status": "RECRUITING"
            },
            # MET靶向试验
            {
                "trial_id": "NCT0010",
                "trial_name": "MET异常激活肿瘤 (cabozantinib)",
                "condition": "实体瘤",
                "genetic_keywords": ["MET"],
                "pathology_keywords": [],
                "marker_keywords": [],
                "status": "RECRUITING"
            },
        ]
    
    def match_trials(
        self,
        genetic_features: Optional[Any],
        pathology_features: Optional[Any],
        marker_analysis: Optional[Any]
    ) -> List[TrialMatch]:
        """
        匹配临床试验
        
        Args:
            genetic_features: 基因特征（GeneticFeatures）
            pathology_features: 病理特征（PathologyFeatures）
            marker_analysis: 标志物分析结果（MarkerAnalysisResult）
        
        Returns:
            按匹配度排序的临床试验列表
        """
        matches: List[TrialMatch] = []
        
        # 提取关键词
        genetic_keywords = self._extract_genetic_keywords(genetic_features)
        pathology_keywords = self._extract_pathology_keywords(pathology_features)
        marker_keywords = self._extract_marker_keywords(pathology_features, marker_analysis)
        
        # 逐个试验匹配
        for trial in self.mock_trials:
            match_result = self._match_single_trial(
                trial,
                genetic_keywords,
                pathology_keywords,
                marker_keywords,
                genetic_features,
                pathology_features
            )
            
            if match_result and match_result.match_score > 0:
                matches.append(match_result)
        
        # 按匹配度降序排序
        matches.sort(key=lambda x: (x.match_type, -x.match_score), reverse=True)
        
        return matches
    
    def _extract_genetic_keywords(self, genetic_features: Optional[Any]) -> List[str]:
        """提取基因关键词"""
        if not genetic_features:
            return []
        
        keywords = []
        
        # 提取驱动基因突变
        for driver in getattr(genetic_features, 'driver_genes', []):
            gene = driver.get('gene', '')
            mutation = driver.get('mutation', '')
            if gene:
                keywords.append(gene)
                if mutation and mutation in ['G12C', 'G12D', 'G12V']:
                    keywords.append(f"KRAS-{mutation}")
                # 其他基因的特定突变
                if gene == 'BRAF' and mutation in ['V600E', 'V600K']:
                    keywords.append(f"BRAF-{mutation}")
        
        # 提取肿瘤抑制基因（DNA修复基因优先级高）
        for suppressor in getattr(genetic_features, 'tumor_suppressor_genes', []):
            gene = suppressor.get('gene', '')
            if gene and gene in ['BRCA1', 'BRCA2', 'PALB2']:
                keywords.append(gene)
        
        return list(set(keywords))
    
    def _extract_pathology_keywords(self, pathology_features: Optional[Any]) -> List[str]:
        """提取病理关键词"""
        if not pathology_features:
            return []
        
        keywords = []
        
        # 癌肿类型
        cancer_type = getattr(pathology_features, 'cancer_type', None)
        if cancer_type:
            chinese_name = cancer_type.get('chinese_name', '')
            if '导管腺癌' in chinese_name or 'ductal' in chinese_name.lower():
                keywords.extend(['adenocarcinoma', 'ductal'])
            elif '神经内分泌' in chinese_name or 'NET' in chinese_name:
                keywords.extend(['neuroendocrine', 'NET'])
            
            # 通用匹配词
            keywords.append('pancreatic_cancer')
        
        # 从trial_keywords获取
        trial_kw = getattr(pathology_features, 'trial_keywords', [])
        keywords.extend(trial_kw)
        
        return list(set(keywords))
    
    def _extract_marker_keywords(
        self,
        pathology_features: Optional[Any],
        marker_analysis: Optional[Any]
    ) -> List[str]:
        """提取标志物关键词"""
        keywords = []
        
        # 从病理特征的trial_keywords
        if pathology_features:
            keywords.extend(getattr(pathology_features, 'trial_keywords', []))
        
        # 从标志物分析
        if marker_analysis:
            # 检查是否有特定标志物
            pass  # 标志物信息已在pathology_features的trial_keywords中
        
        return list(set(keywords))
    
    def _match_single_trial(
        self,
        trial: Dict[str, Any],
        genetic_keywords: List[str],
        pathology_keywords: List[str],
        marker_keywords: List[str],
        genetic_features: Optional[Any],
        pathology_features: Optional[Any]
    ) -> Optional[TrialMatch]:
        """
        匹配单个试验
        
        Returns:
            TrialMatch对象或None
        """
        matched_keywords = []
        genetic_match = False
        pathology_match = False
        marker_match = False
        
        # 检查基因匹配
        trial_genetic_kw = trial.get('genetic_keywords', [])
        for kw in genetic_keywords:
            if kw in trial_genetic_kw or any(kw.upper() in tk.upper() for tk in trial_genetic_kw):
                genetic_match = True
                matched_keywords.append(f"基因:{kw}")
        
        # 检查病理匹配
        trial_pathology_kw = trial.get('pathology_keywords', [])
        for kw in pathology_keywords:
            if kw in trial_pathology_kw or any(kw.lower() in tk.lower() for tk in trial_pathology_kw):
                pathology_match = True
                matched_keywords.append(f"病理:{kw}")
        
        # 检查标志物匹配
        trial_marker_kw = trial.get('marker_keywords', [])
        for kw in marker_keywords:
            if kw in trial_marker_kw or any(kw.lower() in tk.lower() for tk in trial_marker_kw):
                marker_match = True
                matched_keywords.append(f"标志物:{kw}")
        
        # 计算匹配度
        match_count = sum([genetic_match, pathology_match, marker_match])
        
        if match_count == 0:
            return None
        
        # 确定匹配类型和评分
        if genetic_match and pathology_match and marker_match:
            match_type = MatchType.PERFECT.value  # 5
            match_score = 100
            rationale = "完全匹配：基因+病理+标志物"
        elif match_count >= 2:
            match_type = MatchType.DUAL.value  # 4
            match_score = 85
            rationale = "双维度匹配：结合基因和病理特征"
        elif genetic_match:
            match_type = MatchType.SINGLE.value  # 3
            match_score = 70
            rationale = "基因靶点匹配"
        elif pathology_match or marker_match:
            match_type = MatchType.SINGLE.value  # 3
            match_score = 65
            rationale = "病理/标志物匹配"
        else:
            match_type = MatchType.TYPE.value  # 2
            match_score = 50
            rationale = "肿瘤类型匹配"
        
        return TrialMatch(
            trial_name=trial.get('trial_name', ''),
            trial_id=trial.get('trial_id', ''),
            match_type=match_type,
            genetic_match=genetic_match,
            pathology_match=pathology_match,
            marker_match=marker_match,
            matched_keywords=matched_keywords,
            match_score=match_score,
            rationale=rationale
        )
    
    def format_trial_recommendations(self, matches: List[TrialMatch], top_n: int = 5) -> str:
        """
        格式化试验推荐为易读文本
        
        Args:
            matches: 匹配结果列表
            top_n: 只显示前N个
        
        Returns:
            格式化后的推荐文本
        """
        if not matches:
            return "暂无匹配的临床试验"
        
        lines = [f"🔬 为您推荐的临床试验 (共{len(matches)}个)\n"]
        
        for i, match in enumerate(matches[:top_n], 1):
            lines.append(f"{i}. {match.trial_name}")
            lines.append(f"   试验ID: {match.trial_id}")
            lines.append(f"   匹配度: {'⭐' * match.match_type}")
            lines.append(f"   匹配理由: {match.rationale}")
            if match.matched_keywords:
                lines.append(f"   匹配标签: {', '.join(match.matched_keywords)}")
            lines.append("")
        
        if len(matches) > top_n:
            lines.append(f"... 还有 {len(matches) - top_n} 个匹配试验")
        
        return "\n".join(lines)
    
    def to_dict(self, match: TrialMatch) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(match)
    
    def to_json(self, matches: List[TrialMatch]) -> str:
        """转换为JSON"""
        data = [asdict(m) for m in matches]
        return json.dumps(data, ensure_ascii=False, indent=2)
