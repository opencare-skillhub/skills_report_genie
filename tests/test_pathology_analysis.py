"""
Phase 2 病理分析模块单元测试
包括：病理特征提取、多标志物分析、风险分层
"""

import pytest
import json
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analysis.pathology_extractor import PathologyFeatureExtractor, PathologyFeatures
from analysis.marker_analyzer import MarkerAnalyzer, MarkerAnalysisResult
from analysis.risk_stratifier import RiskStratifier, RiskStratificationResult


class TestPathologyFeatureExtractor:
    """病理特征提取器测试"""
    
    @pytest.fixture
    def extractor(self):
        """创建提取器实例"""
        return PathologyFeatureExtractor()
    
    def test_extractor_initialization(self, extractor):
        """测试提取器初始化"""
        assert extractor.pathology_db is not None
        assert len(extractor.pathology_db) > 0
        assert extractor.grade_db is not None
        assert extractor.marker_db is not None
    
    def test_extract_ductal_adenocarcinoma(self, extractor):
        """测试导管腺癌特征提取"""
        report = {
            "primary_pathology": "pancreatic_ductal_adenocarcinoma",
            "differentiation_grade": "II",
            "special_markers": {
                "claudin18": "positive",
                "HER2": "negative",
                "MSI": "MSS"
            }
        }
        
        features = extractor.extract_pathology(report)
        
        assert features.cancer_type is not None
        assert features.cancer_type["chinese_name"] == "胰腺导管腺癌"
        assert features.cancer_type["category"] == "外分泌肿瘤"
        assert features.differentiation_grade is not None
        assert features.differentiation_grade["name"] == "中分化"
        assert len(features.treatment_considerations) > 0
        assert "claudin18+" in features.trial_keywords
    
    def test_extract_neuroendocrine_tumor(self, extractor):
        """测试神经内分泌肿瘤特征提取"""
        report = {
            "primary_pathology": "pancreatic_neuroendocrine_tumor",
            "differentiation_grade": "I",
            "special_markers": {
                "CK8": "positive",
                "Ki-67": "low"
            }
        }
        
        features = extractor.extract_pathology(report)
        
        assert features.cancer_type is not None
        assert features.cancer_type["chinese_name"] == "胰腺神经内分泌肿瘤（NET）"
        assert features.cancer_type["category"] == "内分泌肿瘤"
    
    def test_extract_with_high_risk_markers(self, extractor):
        """测试高危标志物提取"""
        report = {
            "primary_pathology": "pancreatic_ductal_adenocarcinoma",
            "differentiation_grade": "III",
            "special_markers": {
                "E-cadherin": "negative",
                "S100P": "high",
                "IMP3": "positive"
            }
        }
        
        features = extractor.extract_pathology(report)
        
        assert len(features.treatment_considerations) >= 3
        assert "高风险患者，需强化治疗" in features.treatment_considerations[0]
    
    def test_pathology_to_dict(self, extractor):
        """测试特征转换为字典"""
        report = {
            "primary_pathology": "pancreatic_ductal_adenocarcinoma",
            "differentiation_grade": "II",
            "special_markers": {}
        }
        
        features = extractor.extract_pathology(report)
        feature_dict = extractor.to_dict(features)
        
        assert isinstance(feature_dict, dict)
        assert "cancer_type" in feature_dict
        assert "differentiation_grade" in feature_dict
    
    def test_pathology_to_json(self, extractor):
        """测试特征转换为JSON"""
        report = {
            "primary_pathology": "pancreatic_ductal_adenocarcinoma",
            "differentiation_grade": "II",
            "special_markers": {}
        }
        
        features = extractor.extract_pathology(report)
        json_str = extractor.to_json(features)
        
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert "cancer_type" in parsed


class TestMarkerAnalyzer:
    """多标志物分析器测试"""
    
    @pytest.fixture
    def analyzer(self):
        """创建分析器实例"""
        return MarkerAnalyzer()
    
    def test_analyzer_initialization(self, analyzer):
        """测试分析器初始化"""
        assert analyzer.tumor_marker_set is not None
        assert "CA19-9" in analyzer.tumor_marker_set
        assert analyzer.neuroendocrine_marker_set is not None
    
    def test_ca19_9_ca50_co_elevation(self, analyzer):
        """测试CA19-9 + CA50同升高 - 最可信的肿瘤进展信号"""
        markers = {
            "CA19-9": "elevated",
            "CA50": "elevated",
            "CA125": "normal",
            "CA72-4": "normal"
        }
        
        result = analyzer.analyze_multi_markers(markers)
        
        assert result.confidence_level == 5
        assert "CA19-9" in result.trend_interpretation
        assert "CA50" in result.trend_interpretation
        assert "肿瘤进展" in result.trend_interpretation
        assert len(result.simultaneous_elevation) == 2
    
    def test_peritoneal_metastasis_signal(self, analyzer):
        """测试腹膜转移信号 - CA19-9 + CA125同升高"""
        markers = {
            "CA19-9": "elevated",
            "CA125": "elevated"
        }
        
        result = analyzer.analyze_multi_markers(markers)
        
        assert result.confidence_level == 5
        assert "腹膜转移" in result.trend_interpretation or "腹膜反应" in result.trend_interpretation
        assert len(result.simultaneous_elevation) >= 2
    
    def test_single_marker_elevation(self, analyzer):
        """测试单个标志物升高 - 需要排除炎症"""
        markers = {
            "CA19-9": "elevated",
            "CA50": "normal",
            "CA125": "normal",
            "CA72-4": "normal"
        }
        
        result = analyzer.analyze_multi_markers(markers)
        
        assert result.confidence_level == 2
        assert "炎症反应" in result.clinical_recommendation
        assert "CRP" in result.clinical_recommendation
    
    def test_no_elevation(self, analyzer):
        """测试没有标志物升高"""
        markers = {
            "CA19-9": "normal",
            "CA50": "normal",
            "CA125": "normal"
        }
        
        result = analyzer.analyze_multi_markers(markers)
        
        assert result.confidence_level == 5
        assert "正常范围" in result.trend_interpretation
    
    def test_three_markers_elevation(self, analyzer):
        """测试三个标志物同升高 - 强势进展证据"""
        markers = {
            "CA19-9": "elevated",
            "CA50": "elevated",
            "CA125": "elevated"
        }
        
        result = analyzer.analyze_multi_markers(markers)
        
        assert result.confidence_level == 5
        assert "强势" in result.trend_interpretation or "多指标" in result.trend_interpretation
    
    def test_neuroendocrine_markers_analysis(self, analyzer):
        """测试神经内分泌标志物分析"""
        markers = {
            "SYN": "positive",
            "Cg": "positive",
            "CD56": "positive"
        }
        
        result = analyzer.analyze_neuroendocrine_markers(markers)
        
        assert result["is_neuroendocrine"] is True
        assert len(result["markers_present"]) >= 2
        assert "神经内分泌" in result["interpretation"]
    
    def test_marker_consistency_check(self, analyzer):
        """测试标志物一致性检验"""
        markers = {
            "CK7": "positive",
            "CK20": "positive"
        }
        
        result = analyzer.validate_marker_consistency(markers)
        
        assert result["has_issues"] is True
        assert len(result["warnings"]) > 0
    
    def test_marker_analyzer_to_json(self, analyzer):
        """测试标志物分析结果转换为JSON"""
        markers = {
            "CA19-9": "elevated",
            "CA50": "elevated"
        }
        
        result = analyzer.analyze_multi_markers(markers)
        json_str = analyzer.to_json(result)
        
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert "confidence_level" in parsed


class TestRiskStratifier:
    """风险分层器测试"""
    
    @pytest.fixture
    def stratifier(self):
        """创建分层器实例"""
        return RiskStratifier()
    
    def test_stratifier_initialization(self, stratifier):
        """测试分层器初始化"""
        assert stratifier.cancer_type_scores is not None
        assert stratifier.grade_scores is not None
        assert stratifier.marker_scores is not None
    
    def test_high_risk_pdac_with_low_grade(self, stratifier):
        """测试导管腺癌+中分化 - 高危"""
        cancer_type = {
            "chinese_name": "胰腺导管腺癌",
            "category": "外分泌肿瘤"
        }
        grade = {
            "name": "中分化",
            "grade_key": "II"
        }
        markers = {
            "Ki-67": "high",
            "E-cadherin": "negative"
        }
        
        result = stratifier.stratify_risk(cancer_type, grade, markers)
        
        assert result.score >= 100
        assert result.level in ["高危", "极高危"]
        assert len(result.factors) > 0
    
    def test_extremely_high_risk(self, stratifier):
        """测试极高危评分"""
        cancer_type = {
            "chinese_name": "胰腺导管腺癌",
            "category": "外分泌肿瘤"
        }
        grade = {
            "name": "低分化",
            "grade_key": "III"
        }
        markers = {
            "S100P": "high",
            "Ki-67": "high",
            "E-cadherin": "negative",
            "IMP3": "positive"
        }
        
        result = stratifier.stratify_risk(cancer_type, grade, markers)
        
        assert result.score >= 130
        assert result.level == "极高危"
        assert "FOLFIRINOX" in result.treatment_intensity
    
    def test_low_risk_neuroendocrine(self, stratifier):
        """测试中危评分 - G1神经内分泌肿瘤"""
        cancer_type = {
            "chinese_name": "胰腺神经内分泌肿瘤（NET）",
            "category": "内分泌肿瘤"
        }
        grade = {
            "name": "高分化",
            "grade_key": "I"
        }
        markers = {
            "Ki-67": "low",
            "SYN": "positive"
        }
        
        result = stratifier.stratify_risk(cancer_type, grade, markers)
        
        # G1 NET基础分80，加上高分化0，得80，属于中危范围
        assert result.level in ["低危", "中危"]
        assert result.score >= 70
    
    def test_treatment_recommendations_extreme_high_risk(self, stratifier):
        """测试极高危治疗建议"""
        cancer_type = {
            "chinese_name": "胰腺导管腺癌"
        }
        markers = {
            "claudin18": "positive",
            "HER2": "positive"
        }
        
        recommendations = stratifier.generate_treatment_recommendations(
            "极高危",
            cancer_type,
            markers
        )
        
        assert len(recommendations) > 0
        assert any("FOLFIRINOX" in rec for rec in recommendations)
        assert any("多学科" in rec for rec in recommendations)
    
    def test_targetable_markers_recommendations(self, stratifier):
        """测试可靶向标志物的建议"""
        cancer_type = {"chinese_name": "胰腺导管腺癌"}
        markers = {
            "claudin18": "positive",
            "HER2": "positive",
            "MSI": "MSI-H"
        }
        
        recommendations = stratifier.generate_treatment_recommendations(
            "高危",
            cancer_type,
            markers
        )
        
        assert any("claudin18" in rec for rec in recommendations)
        assert any("HER2" in rec for rec in recommendations)
        assert any("MSI" in rec for rec in recommendations)
    
    def test_g3_net_emergency_warning(self, stratifier):
        """测试G3 NET紧急治疗警告"""
        cancer_type = {"chinese_name": "胰腺小细胞癌"}
        markers = {
            "Ki-67": "very_high",
            "Cg": "positive"
        }
        
        recommendations = stratifier.generate_treatment_recommendations(
            "极高危",
            cancer_type,
            markers
        )
        
        assert any("紧急" in rec for rec in recommendations)
        assert any("化疗" in rec for rec in recommendations)
    
    def test_risk_stratifier_to_dict(self, stratifier):
        """测试风险分层结果转换为字典"""
        cancer_type = {"chinese_name": "胰腺导管腺癌"}
        result = stratifier.stratify_risk(cancer_type, None, {})
        
        result_dict = stratifier.to_dict(result)
        
        assert isinstance(result_dict, dict)
        assert "level" in result_dict
        assert "score" in result_dict


class TestIntegration:
    """集成测试 - 测试完整的病理分析流程"""
    
    def test_complete_analysis_workflow(self):
        """测试完整的分析流程"""
        # 初始化各模块
        extractor = PathologyFeatureExtractor()
        analyzer = MarkerAnalyzer()
        stratifier = RiskStratifier()
        
        # 模拟患者病理报告
        pathology_report = {
            "primary_pathology": "pancreatic_ductal_adenocarcinoma",
            "differentiation_grade": "II",
            "special_markers": {
                "claudin18": "positive",
                "HER2": "negative",
                "Ki-67": "high",
                "CA19-9": "elevated",
                "CA50": "elevated",
                "E-cadherin": "negative"
            }
        }
        
        # 第1步：提取病理特征
        pathology_features = extractor.extract_pathology(pathology_report)
        assert pathology_features.cancer_type is not None
        
        # 第2步：多标志物分析
        markers = pathology_report["special_markers"]
        marker_analysis = analyzer.analyze_multi_markers(markers)
        assert marker_analysis.confidence_level > 2
        
        # 第3步：风险分层
        risk_result = stratifier.stratify_risk(
            pathology_features.cancer_type,
            pathology_features.differentiation_grade,
            markers
        )
        assert risk_result.level in ["极高危", "高危", "中危", "低危"]
        
        # 第4步：生成治疗建议
        recommendations = stratifier.generate_treatment_recommendations(
            risk_result.level,
            pathology_features.cancer_type,
            markers
        )
        assert len(recommendations) > 0
        
        # 验证结果完整性
        print("\n=== 完整分析流程验证 ===")
        print(f"病理类型: {pathology_features.cancer_type['chinese_name']}")
        print(f"分化程度: {pathology_features.differentiation_grade['name']}")
        print(f"标志物解释: {marker_analysis.trend_interpretation}")
        print(f"风险等级: {risk_result.level} (得分: {risk_result.score})")
        print(f"治疗强度: {risk_result.treatment_intensity}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
