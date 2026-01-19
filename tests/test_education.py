"""
Phase 4 完整测试套件：科普报告生成与医学文本可视化
测试覆盖：
  - PopularScienceGenerator (10个测试)
  - MedicalTextVisualizer (10个测试)
  - 集成测试 (3个完整工作流)
"""

import pytest
from src.education import (
    PopularScienceGenerator,
    MedicalTextVisualizer,
    create_comprehensive_visualization_report
)


class TestPopularScienceGenerator:
    """测试患者科普版报告生成"""
    
    @pytest.fixture
    def generator(self):
        """初始化生成器"""
        return PopularScienceGenerator()
    
    @pytest.fixture
    def sample_genetic_features(self):
        """示例基因特征"""
        return {
            'driver_genes': [
                {
                    'gene': 'KRAS',
                    'mutation': 'G12C',
                    'actionable': True,
                    'allele_frequency': 45.2
                }
            ],
            'tumor_suppressor_genes': [
                {
                    'gene': 'TP53',
                    'mutation': 'R248Q',
                    'actionable': False
                }
            ],
            'actionable_mutations': ['KRAS-G12C'],
            'risk_profile': '高危'
        }
    
    @pytest.fixture
    def sample_pathology_features(self):
        """示例病理特征"""
        return {
            'cancer_type': 'adenocarcinoma',
            'differentiation': 'moderately_differentiated',
            'special_markers': {
                'claudin18': 'positive',
                'MSI-H': 'negative'
            }
        }
    
    def test_generator_initialization(self, generator):
        """✅ 测试初始化"""
        assert generator is not None
        assert hasattr(generator, 'glossary')
        assert generator.glossary is not None
    
    def test_genetic_education_generation(self, generator, sample_genetic_features):
        """✅ 测试基因科普生成"""
        content = generator.generate_genetic_education(sample_genetic_features)
        
        assert isinstance(content, str)
        assert len(content) > 100
        assert 'KRAS' in content
        assert '科普版' in content or '基因' in content
        assert '高危' in content
    
    def test_kras_mutation_education(self, generator):
        """✅ 测试KRAS突变科普"""
        genetic_features = {
            'driver_genes': [
                {'gene': 'KRAS', 'mutation': 'G12C', 'actionable': True}
            ],
            'tumor_suppressor_genes': [],
            'actionable_mutations': [],
            'risk_profile': '中危'
        }
        
        content = generator.generate_genetic_education(genetic_features)
        
        assert 'KRAS' in content
        assert 'G12C' in content
        assert '靶向' in content or '治疗' in content
    
    def test_brca_mutation_education(self, generator):
        """✅ 测试BRCA突变科普"""
        genetic_features = {
            'driver_genes': [],
            'tumor_suppressor_genes': [
                {'gene': 'BRCA1', 'mutation': 'frameshift'}
            ],
            'actionable_mutations': [],
            'risk_profile': '中危'
        }
        
        content = generator.generate_genetic_education(genetic_features)
        
        assert 'BRCA1' in content
        assert 'PARP' in content or '修复' in content
    
    def test_pathology_education_generation(self, generator, sample_pathology_features):
        """✅ 测试病理科普生成"""
        content = generator.generate_pathology_education(sample_pathology_features)
        
        assert isinstance(content, str)
        assert len(content) > 100
        assert '腺癌' in content or 'adenocarcinoma' in content
    
    def test_claudin18_education(self, generator):
        """✅ 测试claudin18靶点科普"""
        pathology_features = {
            'cancer_type': 'adenocarcinoma',
            'differentiation': 'moderately_differentiated',
            'special_markers': {
                'claudin18': 'positive'
            }
        }
        
        content = generator.generate_pathology_education(pathology_features)
        
        assert 'claudin18' in content
        assert '靶向' in content or '治疗' in content
    
    def test_treatment_education_generation(self, generator):
        """✅ 测试治疗科普生成"""
        treatments = [
            {'type': 'chemotherapy', 'regimen': 'gemcitabine+cisplatin'},
            {'type': 'surgery', 'procedure': 'pancreaticoduodenectomy'}
        ]
        
        content = generator.generate_treatment_education(treatments)
        
        assert isinstance(content, str)
        assert len(content) > 50
        assert ('化疗' in content or 'chemotherapy' in content)
    
    def test_prognosis_education_generation(self, generator, sample_genetic_features, sample_pathology_features):
        """✅ 测试预后科普生成"""
        content = generator.generate_prognosis_education(
            risk_profile='高危',
            genetic_features=sample_genetic_features,
            pathology_features=sample_pathology_features
        )
        
        assert isinstance(content, str)
        assert '预后' in content
        assert '治疗' in content or '积极' in content
    
    def test_comprehensive_education_report(self, generator, sample_genetic_features, sample_pathology_features):
        """✅ 测试完整科普报告生成"""
        treatments = [
            {'type': 'chemotherapy', 'regimen': 'gemcitabine+cisplatin'}
        ]
        
        trials = [
            {
                'trial_name': 'KRAS G12C Study',
                'nct_id': 'NCT0001',
                'brief_title': 'KRAS-G12C 试验',
                'match_score': 95,
                'match_reason': '完全基因匹配'
            }
        ]
        
        report = generator.generate_comprehensive_education_report(
            genetic_features=sample_genetic_features,
            pathology_features=sample_pathology_features,
            treatment_history=treatments,
            matched_trials=trials
        )
        
        assert isinstance(report, str)
        assert len(report) > 500  # 完整报告应该很长
        assert '患者科普版' in report or '科普' in report
        assert 'KRAS' in report


class TestMedicalTextVisualizer:
    """测试医学文本可视化"""
    
    @pytest.fixture
    def visualizer(self):
        """初始化可视化器"""
        return MedicalTextVisualizer()
    
    def test_visualizer_initialization(self, visualizer):
        """✅ 测试初始化"""
        assert visualizer is not None
        assert hasattr(visualizer, 'ICONS')
        assert hasattr(visualizer, 'RISK_LEVELS')
    
    def test_risk_profile_visualization(self, visualizer):
        """✅ 测试风险等级可视化"""
        for risk in ['低危', '中危', '高危', '极高危']:
            content = visualizer.visualize_risk_profile(risk)
            
            assert isinstance(content, str)
            assert len(content) > 10
            assert risk in content
    
    def test_mutation_status_visualization(self, visualizer):
        """✅ 测试突变状态可视化"""
        mutations = [
            {'gene': 'KRAS', 'mutation': 'G12C', 'actionable': True},
            {'gene': 'TP53', 'mutation': 'R248Q', 'actionable': False}
        ]
        
        content = visualizer.visualize_mutation_status(mutations)
        
        assert isinstance(content, str)
        assert 'KRAS' in content
        assert 'TP53' in content
        assert '🎯' in content  # 靶向药图标
    
    def test_treatment_timeline_visualization(self, visualizer):
        """✅ 测试治疗时间线可视化"""
        treatments = [
            {
                'type': 'chemotherapy',
                'date': '2023-02-15',
                'response': 'good'
            },
            {
                'type': 'surgery',
                'date': '2023-09-10',
                'response': 'good'
            }
        ]
        
        content = visualizer.visualize_treatment_timeline(treatments)
        
        assert isinstance(content, str)
        assert '2023-02-15' in content
        assert '2023-09-10' in content
        assert '💊' in content or '🏥' in content
    
    def test_marker_trend_visualization(self, visualizer):
        """✅ 测试标志物趋势可视化"""
        marker_data = {
            'marker_type': 'CA19-9',
            'reference_value': 43,
            'measurements': [
                {'date': '2023-01', 'value': 245.5},
                {'date': '2023-02', 'value': 95.2},
                {'date': '2023-03', 'value': 67.8},
                {'date': '2024-06', 'value': 38.5}
            ]
        }
        
        content = visualizer.visualize_marker_trend(marker_data)
        
        assert isinstance(content, str)
        assert 'CA19-9' in content
        assert '趋势' in content or '下降' in content or '📉' in content
    
    def test_genetic_features_visualization(self, visualizer):
        """✅ 测试基因特征矩阵可视化"""
        genetic_features = {
            'driver_genes': [
                {'gene': 'KRAS', 'mutation': 'G12C'}
            ],
            'tumor_suppressor_genes': [
                {'gene': 'TP53', 'mutation': 'R248Q'}
            ],
            'actionable_mutations': ['KRAS-G12C']
        }
        
        content = visualizer.visualize_genetic_features(genetic_features)
        
        assert isinstance(content, str)
        assert '驱动基因' in content or 'driver' in content
        assert '抑癌基因' in content or 'suppressor' in content
    
    def test_complication_risk_visualization(self, visualizer):
        """✅ 测试并发症风险可视化"""
        complications = [
            {
                'type': '胆管梗阻',
                'risk_level': '中危',
                'prevention': '定期复查B超',
                'monitoring': '监测胆红素'
            }
        ]
        
        content = visualizer.visualize_complication_risk(complications)
        
        assert isinstance(content, str)
        assert '胆管梗阻' in content
        assert '监测' in content or 'monitoring' in content
    
    def test_patient_summary_card(self, visualizer):
        """✅ 测试患者总结卡片"""
        patient_data = {
            'patient_id': 'hash_123',
            'diagnosis_date': '2023-01-15',
            'primary_diagnosis': '胰腺导管腺癌',
            'stage': 'IIIB',
            'genetic_features': {
                'driver_genes': [
                    {'gene': 'KRAS', 'mutation': 'G12C', 'actionable': True}
                ]
            },
            'risk_profile': '高危',
            'latest_treatment': {
                'type': 'chemotherapy',
                'response': 'partial_response'
            }
        }
        
        content = visualizer.create_patient_summary_card(patient_data)
        
        assert isinstance(content, str)
        assert '患者病情速览卡' in content or '病情' in content
        assert 'IIIB' in content
        assert '高危' in content
    
    def test_consultation_checklist(self, visualizer):
        """✅ 测试问诊清单生成"""
        genetic_features = {
            'driver_genes': [
                {'gene': 'KRAS', 'mutation': 'G12C'}
            ]
        }
        
        pathology_features = {
            'cancer_type': 'adenocarcinoma'
        }
        
        content = visualizer.create_consultation_checklist(genetic_features, pathology_features)
        
        assert isinstance(content, str)
        assert '问诊清单' in content or '医生' in content
        assert '[ ]' in content  # 复选框


class TestEducationIntegration:
    """集成测试：完整的科普教育工作流"""
    
    def test_complete_popular_science_workflow(self):
        """✅ 完整科普工作流测试"""
        # 第1步：基因科普
        generator = PopularScienceGenerator()
        genetic_features = {
            'driver_genes': [
                {'gene': 'KRAS', 'mutation': 'G12C', 'actionable': True}
            ],
            'tumor_suppressor_genes': [
                {'gene': 'TP53', 'mutation': 'R248Q'}
            ],
            'actionable_mutations': ['KRAS-G12C'],
            'risk_profile': '高危'
        }
        
        genetic_education = generator.generate_genetic_education(genetic_features)
        assert '科普' in genetic_education or 'KRAS' in genetic_education
        
        # 第2步：病理科普
        pathology_features = {
            'cancer_type': 'adenocarcinoma',
            'differentiation': 'moderately_differentiated',
            'special_markers': {
                'claudin18': 'positive'
            }
        }
        
        pathology_education = generator.generate_pathology_education(pathology_features)
        assert '病理' in pathology_education or '腺癌' in pathology_education
        
        # 第3步：预后评估
        prognosis = generator.generate_prognosis_education(
            risk_profile='高危',
            genetic_features=genetic_features,
            pathology_features=pathology_features
        )
        assert '预后' in prognosis
        
        # 第4步：临床试验科普
        trials = [
            {
                'trial_name': 'KRAS G12C Study',
                'nct_id': 'NCT0001',
                'brief_title': 'KRAS-G12C 试验',
                'match_score': 95
            }
        ]
        
        trial_education = generator.generate_clinical_trial_education(trials)
        assert '临床试验' in trial_education
    
    def test_complete_visualization_workflow(self):
        """✅ 完整可视化工作流测试"""
        visualizer = MedicalTextVisualizer()
        
        # 第1步：风险可视化
        risk_vis = visualizer.visualize_risk_profile('高危', '多个驱动基因')
        assert '高危' in risk_vis
        
        # 第2步：基因可视化
        genetic_features = {
            'driver_genes': [
                {'gene': 'KRAS', 'mutation': 'G12C', 'actionable': True}
            ],
            'tumor_suppressor_genes': [],
            'actionable_mutations': ['KRAS-G12C']
        }
        gene_vis = visualizer.visualize_genetic_features(genetic_features)
        assert '驱动基因' in gene_vis or '可靶向' in gene_vis
        
        # 第3步：时间线可视化
        treatments = [
            {'type': 'chemotherapy', 'date': '2023-02-15', 'response': 'good'},
            {'type': 'surgery', 'date': '2023-09-10', 'response': 'good'}
        ]
        timeline = visualizer.visualize_treatment_timeline(treatments)
        assert '2023-02-15' in timeline
        
        # 第4步：患者卡片
        patient_data = {
            'patient_id': 'hash_123',
            'primary_diagnosis': '胰腺癌',
            'stage': 'IIIB',
            'genetic_features': genetic_features,
            'risk_profile': '高危',
            'latest_treatment': {'type': 'chemotherapy', 'response': 'partial'}
        }
        card = visualizer.create_patient_summary_card(patient_data)
        assert '速览卡' in card or 'IIIB' in card
    
    def test_comprehensive_education_report(self):
        """✅ 完整科普教育报告生成"""
        generator = PopularScienceGenerator()
        
        genetic_features = {
            'driver_genes': [
                {'gene': 'KRAS', 'mutation': 'G12C', 'actionable': True}
            ],
            'tumor_suppressor_genes': [
                {'gene': 'TP53', 'mutation': 'R248Q'}
            ],
            'actionable_mutations': ['KRAS-G12C'],
            'risk_profile': '高危'
        }
        
        pathology_features = {
            'cancer_type': 'adenocarcinoma',
            'differentiation': 'moderately_differentiated',
            'special_markers': {
                'claudin18': 'positive',
                'MSI-H': 'negative'
            }
        }
        
        treatments = [
            {
                'type': 'chemotherapy',
                'regimen': 'gemcitabine+cisplatin',
                'start_date': '2023-02-15',
                'duration': '6个月'
            },
            {
                'type': 'surgery',
                'procedure': 'pancreaticoduodenectomy',
                'date': '2023-09-10'
            }
        ]
        
        trials = [
            {
                'trial_name': 'KRAS G12C Study',
                'nct_id': 'NCT0001',
                'brief_title': 'KRAS-G12C 试验',
                'match_score': 95,
                'match_reason': '完全基因匹配'
            },
            {
                'trial_name': 'Claudin18 Immunotherapy',
                'nct_id': 'NCT0003',
                'brief_title': 'Claudin18 靶向免疫',
                'match_score': 85,
                'match_reason': '病理标志物匹配'
            }
        ]
        
        # 生成完整报告
        report = generator.generate_comprehensive_education_report(
            genetic_features=genetic_features,
            pathology_features=pathology_features,
            treatment_history=treatments,
            matched_trials=trials
        )
        
        # 验证报告完整性
        assert isinstance(report, str)
        assert len(report) > 1000  # 完整报告应该很长
        assert '患者科普版' in report or '科普' in report
        assert 'KRAS' in report
        assert '临床试验' in report or 'trial' in report
        assert '医学方面' in report or '治疗' in report


class TestEducationQualityMetrics:
    """科普教育质量指标测试"""
    
    def test_glossary_completeness(self):
        """✅ 词汇表完整性测试"""
        from src.education.popular_science_generator import GeneticGlossary
        
        glossary = GeneticGlossary()
        
        # 验证基因数量
        assert len(glossary.GENETIC_TERMS) >= 10
        
        # 验证每个基因有完整信息
        for gene, info in glossary.GENETIC_TERMS.items():
            assert 'name' in info
            assert 'function' in info
            assert 'mutation_simple' in info
            assert 'treatment_direction' in info
            assert 'prognosis' in info
    
    def test_visualization_icons_coverage(self):
        """✅ 可视化图标覆盖测试"""
        visualizer = MedicalTextVisualizer()
        
        # 验证至少有基本的风险等级
        assert len(visualizer.RISK_LEVELS) == 4
        
        # 验证每个风险等级有完整信息
        for risk, info in visualizer.RISK_LEVELS.items():
            assert 'color' in info
            assert 'icon' in info
            assert 'description' in info
    
    def test_readability_level(self):
        """✅ 可读性水平测试"""
        generator = PopularScienceGenerator()
        
        genetic_features = {
            'driver_genes': [
                {'gene': 'KRAS', 'mutation': 'G12C', 'actionable': True}
            ],
            'tumor_suppressor_genes': [],
            'actionable_mutations': [],
            'risk_profile': '中危'
        }
        
        content = generator.generate_genetic_education(genetic_features)
        
        # 验证内容包含简单解释
        assert '是什么' in content or '简单' in content or '意思' in content
        # 验证包含患者友好的表达
        assert '治疗' in content or '药物' in content or '意味' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
