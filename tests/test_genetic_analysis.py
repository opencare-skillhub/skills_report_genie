"""
Phase 3 基因分析模块单元测试
包括：基因特征提取、临床试验匹配
"""

import pytest
import json
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analysis.genetic_extractor import GeneticFeatureExtractor, GeneticFeatures
from analysis.trial_matcher import ClinicalTrialMatcher, TrialMatch


class TestGeneticFeatureExtractor:
    """基因特征提取器测试"""
    
    @pytest.fixture
    def extractor(self):
        """创建提取器实例"""
        return GeneticFeatureExtractor()
    
    def test_extractor_initialization(self, extractor):
        """测试提取器初始化"""
        assert extractor.gene_db is not None
        assert len(extractor.gene_db) > 0
        assert "KRAS" in extractor.gene_db
        assert "TP53" in extractor.gene_db
    
    def test_extract_kras_g12c_mutation(self, extractor):
        """测试KRAS G12C突变提取"""
        report = {
            "test_type": "NGS",
            "mutations": [
                {
                    "gene": "KRAS",
                    "mutation": "G12C",
                    "classification": "驱动基因",
                    "allele_frequency": 45.2
                }
            ]
        }
        
        features = extractor.extract_mutations(report)
        
        assert len(features.driver_genes) == 1
        assert features.driver_genes[0]["gene"] == "KRAS"
        assert features.driver_genes[0]["mutation"] == "G12C"
        assert features.driver_genes[0]["is_actionable"] is True
        assert "sotorasib" in features.driver_genes[0]["treatment_directions"][0]
    
    def test_extract_tp53_mutation(self, extractor):
        """测试TP53突变提取"""
        report = {
            "test_type": "NGS",
            "mutations": [
                {
                    "gene": "TP53",
                    "mutation": "R248Q",
                    "classification": "抑癌基因",
                    "allele_frequency": 42.8
                }
            ]
        }
        
        features = extractor.extract_mutations(report)
        
        assert len(features.tumor_suppressor_genes) == 1
        assert features.tumor_suppressor_genes[0]["gene"] == "TP53"
        assert features.tumor_suppressor_genes[0]["type"] == "抑癌基因"
    
    def test_extract_brca1_mutation(self, extractor):
        """测试BRCA1突变提取 (DNA修复基因)"""
        report = {
            "test_type": "NGS",
            "mutations": [
                {
                    "gene": "BRCA1",
                    "mutation": "frameshift",
                    "classification": "DNA修复基因",
                    "allele_frequency": 50.0
                }
            ]
        }
        
        features = extractor.extract_mutations(report)
        
        assert len(features.tumor_suppressor_genes) == 1
        assert features.tumor_suppressor_genes[0]["gene"] == "BRCA1"
        assert "PARPi" in str(features.tumor_suppressor_genes[0]["treatment_directions"])
    
    def test_multiple_mutations_high_risk(self, extractor):
        """测试多个突变 - 高危评分"""
        report = {
            "test_type": "NGS",
            "mutations": [
                {
                    "gene": "KRAS",
                    "mutation": "G12D",
                    "classification": "驱动基因",
                    "allele_frequency": 40.0
                },
                {
                    "gene": "TP53",
                    "mutation": "R175H",
                    "classification": "抑癌基因",
                    "allele_frequency": 38.0
                }
            ]
        }
        
        features = extractor.extract_mutations(report)
        
        assert len(features.driver_genes) == 1
        assert len(features.tumor_suppressor_genes) == 1
        assert features.risk_profile == "高危"
    
    def test_no_mutations(self, extractor):
        """测试无突变 - 低危"""
        report = {
            "test_type": "NGS",
            "mutations": []
        }
        
        features = extractor.extract_mutations(report)
        
        assert len(features.driver_genes) == 0
        assert len(features.tumor_suppressor_genes) == 0
        assert features.risk_profile == "低危"
    
    def test_actionable_mutations_identification(self, extractor):
        """测试可靶向突变识别"""
        report = {
            "test_type": "NGS",
            "mutations": [
                {
                    "gene": "KRAS",
                    "mutation": "G12C",
                    "classification": "驱动基因",
                    "allele_frequency": 45.0
                },
                {
                    "gene": "ERBB2",
                    "mutation": "amplification",
                    "classification": "原癌基因",
                    "allele_frequency": 35.0
                }
            ]
        }
        
        features = extractor.extract_mutations(report)
        actionable = extractor.identify_actionable_mutations(features)
        
        assert len(actionable["mutations"]) > 0
        assert len(actionable["targeted_therapies"]) > 0
    
    def test_trial_keywords_extraction(self, extractor):
        """测试临床试验关键词提取"""
        report = {
            "test_type": "NGS",
            "mutations": [
                {
                    "gene": "KRAS",
                    "mutation": "G12C",
                    "classification": "驱动基因",
                    "allele_frequency": 45.0
                }
            ]
        }
        
        features = extractor.extract_mutations(report)
        
        assert len(features.trial_keywords) > 0
        assert any("KRAS" in kw for kw in features.trial_keywords)
    
    def test_genetic_features_to_json(self, extractor):
        """测试特征转换为JSON"""
        report = {
            "test_type": "NGS",
            "mutations": [
                {
                    "gene": "KRAS",
                    "mutation": "G12C",
                    "classification": "驱动基因",
                    "allele_frequency": 45.0
                }
            ]
        }
        
        features = extractor.extract_mutations(report)
        json_str = extractor.to_json(features)
        
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert "driver_genes" in parsed


class TestClinicalTrialMatcher:
    """临床试验匹配器测试"""
    
    @pytest.fixture
    def matcher(self):
        """创建匹配器实例"""
        return ClinicalTrialMatcher()
    
    def test_matcher_initialization(self, matcher):
        """测试匹配器初始化"""
        assert matcher.mock_trials is not None
        assert len(matcher.mock_trials) > 0
    
    def test_kras_g12c_trial_matching(self, matcher):
        """测试KRAS-G12C试验匹配"""
        # 模拟基因特征
        class MockGeneticFeatures:
            driver_genes = [
                {
                    "gene": "KRAS",
                    "mutation": "G12C",
                    "is_actionable": True
                }
            ]
            tumor_suppressor_genes = []
        
        genetic_features = MockGeneticFeatures()
        
        matches = matcher.match_trials(genetic_features, None, None)
        
        assert len(matches) > 0
        # 应该匹配到KRAS-G12C相关试验
        kras_matches = [m for m in matches if "KRAS" in m.trial_name or "G12C" in m.trial_name]
        assert len(kras_matches) > 0
    
    def test_claudin18_pathology_matching(self, matcher):
        """测试claudin18病理特征匹配"""
        # 模拟病理特征
        class MockPathologyFeatures:
            cancer_type = {
                "chinese_name": "胰腺导管腺癌",
                "category": "外分泌肿瘤"
            }
            trial_keywords = ["claudin18+"]
        
        pathology_features = MockPathologyFeatures()
        
        matches = matcher.match_trials(None, pathology_features, None)
        
        assert len(matches) > 0
        # 应该匹配到claudin18相关试验
        claudin_matches = [m for m in matches if "claudin18" in m.trial_name.lower()]
        assert len(claudin_matches) > 0
    
    def test_dual_matching_perfect_score(self, matcher):
        """测试双维度匹配（完全匹配）"""
        class MockGeneticFeatures:
            driver_genes = [{"gene": "KRAS", "mutation": "G12C", "is_actionable": True}]
            tumor_suppressor_genes = []
        
        class MockPathologyFeatures:
            cancer_type = {
                "chinese_name": "胰腺导管腺癌",
                "category": "外分泌肿瘤"
            }
            trial_keywords = []
        
        genetic_features = MockGeneticFeatures()
        pathology_features = MockPathologyFeatures()
        
        matches = matcher.match_trials(genetic_features, pathology_features, None)
        
        assert len(matches) > 0
        # 检查匹配度
        top_match = matches[0]
        assert top_match.genetic_match or top_match.pathology_match
    
    def test_brca_parp_matching(self, matcher):
        """测试BRCA-PARP抑制剂匹配"""
        class MockGeneticFeatures:
            driver_genes = []
            tumor_suppressor_genes = [
                {"gene": "BRCA1", "mutation": "frameshift", "is_actionable": True}
            ]
        
        genetic_features = MockGeneticFeatures()
        
        matches = matcher.match_trials(genetic_features, None, None)
        
        assert len(matches) > 0
        # 应该匹配到PARP抑制剂试验
        parp_matches = [m for m in matches if "PARP" in m.trial_name or "olaparib" in m.trial_name]
        assert len(parp_matches) > 0
    
    def test_no_matching_trials(self, matcher):
        """测试无匹配情况"""
        class MockGeneticFeatures:
            driver_genes = [{"gene": "UNKNOWN_GENE", "mutation": "X123"}]
            tumor_suppressor_genes = []
        
        genetic_features = MockGeneticFeatures()
        
        matches = matcher.match_trials(genetic_features, None, None)
        
        # 可能没有匹配或有基础匹配
        assert isinstance(matches, list)
    
    def test_match_score_ranking(self, matcher):
        """测试匹配度排序"""
        class MockGeneticFeatures:
            driver_genes = [{"gene": "KRAS", "mutation": "G12C", "is_actionable": True}]
            tumor_suppressor_genes = []
        
        class MockPathologyFeatures:
            cancer_type = {
                "chinese_name": "胰腺导管腺癌",
                "category": "外分泌肿瘤"
            }
            trial_keywords = []
        
        genetic_features = MockGeneticFeatures()
        pathology_features = MockPathologyFeatures()
        
        matches = matcher.match_trials(genetic_features, pathology_features, None)
        
        assert len(matches) > 0
        # 验证排序
        for i in range(len(matches) - 1):
            assert matches[i].match_type >= matches[i+1].match_type
    
    def test_format_trial_recommendations(self, matcher):
        """测试推荐文本格式化"""
        class MockGeneticFeatures:
            driver_genes = [{"gene": "KRAS", "mutation": "G12C", "is_actionable": True}]
            tumor_suppressor_genes = []
        
        genetic_features = MockGeneticFeatures()
        matches = matcher.match_trials(genetic_features, None, None)
        
        formatted = matcher.format_trial_recommendations(matches, top_n=3)
        
        assert isinstance(formatted, str)
        assert "推荐" in formatted or "临床试验" in formatted
        assert len(formatted) > 0
    
    def test_trial_match_to_json(self, matcher):
        """测试匹配结果转换为JSON"""
        class MockGeneticFeatures:
            driver_genes = [{"gene": "KRAS", "mutation": "G12C", "is_actionable": True}]
            tumor_suppressor_genes = []
        
        genetic_features = MockGeneticFeatures()
        matches = matcher.match_trials(genetic_features, None, None)
        
        if matches:
            json_str = matcher.to_json(matches)
            assert isinstance(json_str, str)
            parsed = json.loads(json_str)
            assert isinstance(parsed, list)


class TestIntegration:
    """集成测试 - 完整的基因分析和试验匹配流程"""
    
    def test_complete_genetic_workflow(self):
        """测试完整的基因分析和试验匹配流程"""
        extractor = GeneticFeatureExtractor()
        matcher = ClinicalTrialMatcher()
        
        # 第1步: 提取基因特征
        genetic_report = {
            "test_type": "NGS",
            "mutations": [
                {
                    "gene": "KRAS",
                    "mutation": "G12C",
                    "classification": "驱动基因",
                    "allele_frequency": 45.2
                },
                {
                    "gene": "TP53",
                    "mutation": "R248Q",
                    "classification": "抑癌基因",
                    "allele_frequency": 42.8
                }
            ]
        }
        
        genetic_features = extractor.extract_mutations(genetic_report)
        assert genetic_features.risk_profile == "高危"
        assert len(genetic_features.driver_genes) == 1
        
        # 第2步: 识别可靶向突变
        actionable = extractor.identify_actionable_mutations(genetic_features)
        assert len(actionable["mutations"]) > 0
        
        # 第3步: 匹配临床试验
        matches = matcher.match_trials(genetic_features, None, None)
        assert len(matches) > 0
        
        # 第4步: 生成推荐
        recommendations = matcher.format_trial_recommendations(matches, top_n=5)
        assert len(recommendations) > 0
        
        print("\n=== 完整基因分析工作流 ===")
        print(f"驱动基因: {[g['gene'] for g in genetic_features.driver_genes]}")
        print(f"风险等级: {genetic_features.risk_profile}")
        print(f"可靶向突变: {len(actionable['mutations'])}")
        print(f"匹配的临床试验: {len(matches)}")
        print("\n推荐:\n" + recommendations)
    
    def test_brca_pathway_workflow(self):
        """测试BRCA-PARP通路"""
        extractor = GeneticFeatureExtractor()
        matcher = ClinicalTrialMatcher()
        
        # BRCA1突变
        genetic_report = {
            "test_type": "NGS",
            "mutations": [
                {
                    "gene": "BRCA1",
                    "mutation": "frameshift",
                    "classification": "DNA修复基因",
                    "allele_frequency": 50.0
                }
            ]
        }
        
        genetic_features = extractor.extract_mutations(genetic_report)
        matches = matcher.match_trials(genetic_features, None, None)
        
        assert len(genetic_features.tumor_suppressor_genes) >= 1
        # 检查是否有BRCA/PARP相关试验
        assert any("BRCA" in m.trial_name or "PARP" in m.trial_name or "olaparib" in m.trial_name for m in matches)
        
        print("\n=== BRCA-PARP通路 ===")
        print(f"识别的基因: BRCA1")
        print(f"推荐治疗: PARPi (olaparib, rucaparib)")
        print(f"匹配试验: {len(matches)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
