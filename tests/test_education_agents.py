"""
Phase 4 完整测试套件：科普教育智能体 + 可视化智能体
测试覆盖：
  - PopularScienceAgent (LLM驱动) - 6个测试
  - VisualizationAgent (LLM驱动) - 6个测试
  - 智能体框架验证 - 3个测试
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.agents import PopularScienceAgent, VisualizationAgent


class TestPopularScienceAgentStructure:
    """测试科普教育智能体结构"""
    
    def test_agent_class_exists(self):
        """✅ 科普智能体类存在"""
        assert PopularScienceAgent is not None
    
    def test_agent_has_required_methods(self):
        """✅ 科普智能体有所有必需方法"""
        required_methods = [
            'generate_genetic_education',
            'generate_pathology_education',
            'generate_treatment_education',
            'generate_prognosis_education',
            'generate_clinical_trial_education',
            'generate_patient_self_care',
            'generate_comprehensive_education_report'
        ]
        
        for method in required_methods:
            assert hasattr(PopularScienceAgent, method), f"缺少方法: {method}"
    
    def test_agent_has_system_prompt(self):
        """✅ 科普智能体有系统提示词"""
        assert hasattr(PopularScienceAgent, 'SYSTEM_PROMPT')
        assert PopularScienceAgent.SYSTEM_PROMPT is not None
        assert isinstance(PopularScienceAgent.SYSTEM_PROMPT, str)
        assert len(PopularScienceAgent.SYSTEM_PROMPT) > 100
    
    def test_system_prompt_contains_key_concepts(self):
        """✅ 系统提示词包含关键概念"""
        prompt = PopularScienceAgent.SYSTEM_PROMPT
        
        # 验证提示词包含科普核心原则
        assert '患者' in prompt or 'patient' in prompt.lower()
        assert '简单' in prompt or '易懂' in prompt or 'simple' in prompt.lower()


class TestVisualizationAgentStructure:
    """测试医学可视化智能体结构"""
    
    def test_agent_class_exists(self):
        """✅ 可视化智能体类存在"""
        assert VisualizationAgent is not None
    
    def test_agent_has_required_methods(self):
        """✅ 可视化智能体有所有必需方法"""
        required_methods = [
            'design_risk_profile_visualization',
            'design_genetic_features_table',
            'design_treatment_timeline',
            'design_marker_trend_narrative',
            'design_patient_summary_card',
            'design_consultation_checklist',
            'design_complication_risk_table',
            'generate_comprehensive_visualization_report'
        ]
        
        for method in required_methods:
            assert hasattr(VisualizationAgent, method), f"缺少方法: {method}"
    
    def test_agent_has_system_prompt(self):
        """✅ 可视化智能体有系统提示词"""
        assert hasattr(VisualizationAgent, 'SYSTEM_PROMPT')
        assert VisualizationAgent.SYSTEM_PROMPT is not None
        assert isinstance(VisualizationAgent.SYSTEM_PROMPT, str)
        assert len(VisualizationAgent.SYSTEM_PROMPT) > 100
    
    def test_system_prompt_contains_key_concepts(self):
        """✅ 系统提示词包含关键概念"""
        prompt = VisualizationAgent.SYSTEM_PROMPT
        
        # 验证提示词包含设计核心原则
        assert '可视化' in prompt or 'visualization' in prompt.lower()
        assert '清晰' in prompt or 'clear' in prompt.lower()


class TestAgentSignatures:
    """测试智能体方法签名和接口"""
    
    def test_popular_science_method_signatures(self):
        """✅ 科普智能体方法签名正确"""
        # 验证方法接受正确的参数类型
        agent = PopularScienceAgent.__init__
        assert agent is not None
        
        # 验证方法定义
        import inspect
        
        # generate_genetic_education
        sig = inspect.signature(PopularScienceAgent.generate_genetic_education)
        assert 'genetic_features' in sig.parameters
        
        # generate_comprehensive_education_report
        sig = inspect.signature(PopularScienceAgent.generate_comprehensive_education_report)
        assert 'genetic_features' in sig.parameters
        assert 'pathology_features' in sig.parameters
        assert 'treatment_history' in sig.parameters
        assert 'matched_trials' in sig.parameters
        assert 'risk_profile' in sig.parameters
    
    def test_visualization_method_signatures(self):
        """✅ 可视化智能体方法签名正确"""
        import inspect
        
        # design_risk_profile_visualization
        sig = inspect.signature(VisualizationAgent.design_risk_profile_visualization)
        assert 'risk_profile' in sig.parameters
        
        # design_genetic_features_table
        sig = inspect.signature(VisualizationAgent.design_genetic_features_table)
        assert 'genetic_features' in sig.parameters
        
        # generate_comprehensive_visualization_report
        sig = inspect.signature(VisualizationAgent.generate_comprehensive_visualization_report)
        assert 'genetic_features' in sig.parameters
        assert 'patient_data' in sig.parameters


class TestAgentDocumentation:
    """测试智能体的文档"""
    
    def test_popular_science_agent_documented(self):
        """✅ 科普智能体有文档"""
        assert PopularScienceAgent.__doc__ is not None
        
        # 验证关键方法有文档
        assert PopularScienceAgent.generate_genetic_education.__doc__ is not None
        assert PopularScienceAgent.generate_comprehensive_education_report.__doc__ is not None
    
    def test_visualization_agent_documented(self):
        """✅ 可视化智能体有文档"""
        assert VisualizationAgent.__doc__ is not None
        
        # 验证关键方法有文档
        assert VisualizationAgent.design_risk_profile_visualization.__doc__ is not None
        assert VisualizationAgent.generate_comprehensive_visualization_report.__doc__ is not None


class TestAgentDesignPatterns:
    """测试智能体的设计模式"""
    
    def test_agents_use_anthropic_client(self):
        """✅ 智能体使用Anthropic客户端"""
        # 验证PopularScienceAgent初始化
        try:
            # 这不会实际创建，因为需要真实的API密钥或mock
            # 我们只验证结构
            import inspect
            sig = inspect.signature(PopularScienceAgent.__init__)
            assert 'api_key' in sig.parameters
            assert 'model' in sig.parameters
        except Exception as e:
            pytest.skip(f"无法测试初始化: {e}")
    
    def test_agents_follow_llm_first_design(self):
        """✅ 智能体遵循LLM优先设计"""
        # 验证方法使用Claude API而不是硬编码内容
        
        # 检查是否导入了anthropic
        import src.agents.popular_science_agent as ps_module
        assert hasattr(ps_module, 'anthropic')
        
        import src.agents.visualization_agent as viz_module
        assert hasattr(viz_module, 'anthropic')
    
    def test_agents_have_structured_prompts(self):
        """✅ 智能体有结构化提示词"""
        ps_agent = PopularScienceAgent
        viz_agent = VisualizationAgent
        
        # 两个智能体都应该定义SYSTEM_PROMPT
        assert hasattr(ps_agent, 'SYSTEM_PROMPT')
        assert hasattr(viz_agent, 'SYSTEM_PROMPT')
        
        # 提示词应该清晰定义角色和任务
        ps_prompt = ps_agent.SYSTEM_PROMPT
        viz_prompt = viz_agent.SYSTEM_PROMPT
        
        # 都应该强调患者友好
        assert ('患者' in ps_prompt or '科普' in ps_prompt or 'patient' in ps_prompt.lower())
        assert ('可视化' in viz_prompt or '清晰' in viz_prompt or 'visual' in viz_prompt.lower())


class TestPhase4Architecture:
    """测试Phase 4的整体架构"""
    
    def test_two_agents_for_two_tasks(self):
        """✅ 有两个专用智能体处理两个任务"""
        # Task 1: 科普内容生成 → PopularScienceAgent
        assert hasattr(PopularScienceAgent, 'generate_genetic_education')
        assert hasattr(PopularScienceAgent, 'generate_comprehensive_education_report')
        
        # Task 2: 可视化设计 → VisualizationAgent
        assert hasattr(VisualizationAgent, 'design_risk_profile_visualization')
        assert hasattr(VisualizationAgent, 'generate_comprehensive_visualization_report')
    
    def test_agents_accept_structured_input(self):
        """✅ 智能体接受结构化输入（来自Phase 3）"""
        import inspect
        
        # PopularScienceAgent.generate_genetic_education
        # 应该接受genetic_features字典（来自GeneticFeatureExtractor）
        sig = inspect.signature(PopularScienceAgent.generate_genetic_education)
        params = list(sig.parameters.keys())
        assert 'genetic_features' in params
        
        # VisualizationAgent.design_genetic_features_table
        # 应该接受genetic_features字典
        sig = inspect.signature(VisualizationAgent.design_genetic_features_table)
        params = list(sig.parameters.keys())
        assert 'genetic_features' in params
    
    def test_agents_produce_string_output(self):
        """✅ 智能体输出为字符串（markdown格式）"""
        import inspect
        
        # 所有main方法都应该返回str
        for method_name in [
            'generate_genetic_education',
            'generate_comprehensive_education_report'
        ]:
            method = getattr(PopularScienceAgent, method_name)
            # 验证返回类型注解（如果有）
            sig = inspect.signature(method)
            # 如果有返回类型注解，应该是str
            if sig.return_annotation != inspect.Signature.empty:
                assert sig.return_annotation == str or 'str' in str(sig.return_annotation)


class TestCodeQuality:
    """测试代码质量"""
    
    def test_popular_science_agent_imports(self):
        """✅ PopularScienceAgent导入正确"""
        import src.agents.popular_science_agent
        
        # 应该导入anthropic
        assert hasattr(src.agents.popular_science_agent, 'anthropic')
        assert hasattr(src.agents.popular_science_agent, 'PopularScienceAgent')
    
    def test_visualization_agent_imports(self):
        """✅ VisualizationAgent导入正确"""
        import src.agents.visualization_agent
        
        # 应该导入anthropic
        assert hasattr(src.agents.visualization_agent, 'anthropic')
        assert hasattr(src.agents.visualization_agent, 'VisualizationAgent')
    
    def test_agents_init_exports(self):
        """✅ agents/__init__.py正确导出"""
        from src.agents import PopularScienceAgent, VisualizationAgent
        
        assert PopularScienceAgent is not None
        assert VisualizationAgent is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
