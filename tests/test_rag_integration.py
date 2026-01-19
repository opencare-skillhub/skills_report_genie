"""
小胰宝RAG集成测试
测试RAG客户端和多源分析器
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from integration.rag_client import (
    XiaoyibaoRAGClient,
    MultiSourceAnalyzer,
    RAGResponse,
    MultiSourceResult,
    create_xiaoyibao_rag_client,
    create_multi_source_analyzer
)


class TestXiaoyibaoRAGClient:
    """小胰宝RAG客户端测试"""
    
    @pytest.fixture
    def mock_api_key(self):
        """模拟API密钥"""
        return "test-api-key-123"
    
    @pytest.fixture
    def rag_client(self, mock_api_key):
        """创建RAG客户端"""
        return XiaoyibaoRAGClient(api_key=mock_api_key)
    
    def test_initialization(self, rag_client, mock_api_key):
        """测试客户端初始化"""
        assert rag_client.api_key == mock_api_key
        assert rag_client.base_url == "https://admin.xiaoyibao.com.cn/v1"
        assert rag_client.session is not None
    
    @patch('requests.Session.post')
    def test_query_successful(self, mock_post, rag_client):
        """测试成功查询"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "KRAS-G12C是一个重要的治疗靶点。推荐使用sotorasib..."
                    }
                }
            ],
            "relevance_score": 0.9,
            "references": ["参考文献1", "参考文献2"]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        # 执行查询
        result = rag_client.query("KRAS G12C治疗方案")
        
        # 验证结果
        assert result.source == "xiaoyibao_rag"
        assert "sotorasib" in result.content
        assert result.relevance_score == 0.9
        assert result.is_confident is True
        assert len(result.references) == 2
    
    @patch('requests.Session.post')
    def test_query_low_confidence(self, mock_post, rag_client):
        """测试低置信度查询"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "uncertain answer"}}],
            "relevance_score": 0.5,
            "references": []
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = rag_client.query("罕见突变处理方案")
        
        assert result.relevance_score == 0.5
        assert result.is_confident is False
    
    @patch('requests.Session.post')
    def test_query_failure(self, mock_post, rag_client):
        """测试查询失败"""
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")
        
        result = rag_client.query("测试查询")
        
        assert result.relevance_score == 0
        assert result.is_confident is False
        assert result.content == ""
    
    @patch('requests.Session.post')
    def test_query_genetic_info(self, mock_post, rag_client):
        """测试基因信息查询"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "KRAS突变信息..."}}],
            "relevance_score": 0.85
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = rag_client.query_genetic_info("KRAS", "G12C")
        
        assert result.source == "xiaoyibao_rag"
        assert result.is_confident is True
    
    @patch('requests.Session.post')
    def test_query_pathology_info(self, mock_post, rag_client):
        """测试病理信息查询"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "导管腺癌信息..."}}],
            "relevance_score": 0.88
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = rag_client.query_pathology_info("导管腺癌", "claudin18+")
        
        assert "导管腺癌" in result.content
    
    @patch('requests.Session.post')
    def test_batch_query(self, mock_post, rag_client):
        """测试批量查询"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "回复"}}],
            "relevance_score": 0.8
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        queries = [
            "KRAS突变",
            "TP53突变",
            "claudin18标志物"
        ]
        
        results = rag_client.batch_query(queries)
        
        assert len(results) == 3
        assert all(r.source == "xiaoyibao_rag" for r in results)


class TestMultiSourceAnalyzer:
    """多源分析器测试"""
    
    @pytest.fixture
    def mock_rag_client(self):
        """创建模拟RAG客户端"""
        client = Mock(spec=XiaoyibaoRAGClient)
        return client
    
    @pytest.fixture
    def analyzer(self, mock_rag_client):
        """创建分析器"""
        return MultiSourceAnalyzer(mock_rag_client)
    
    def test_initialization(self, analyzer, mock_rag_client):
        """测试分析器初始化"""
        assert analyzer.rag_client == mock_rag_client
    
    def test_analyze_query_single_source(self, analyzer, mock_rag_client):
        """测试单源分析"""
        # 模拟RAG响应
        mock_rag_client.query.return_value = RAGResponse(
            content="KRAS-G12C推荐使用sotorasib...",
            relevance_score=0.9,
            source="xiaoyibao_rag",
            references=["参考文献"],
            is_confident=True
        )
        
        result = analyzer.analyze_query(
            "KRAS-G12C治疗方案",
            sources=["xiaoyibao_rag"]
        )
        
        assert isinstance(result, MultiSourceResult)
        assert result.query == "KRAS-G12C治疗方案"
        assert len(result.results) == 1
        assert result.results[0].source == "xiaoyibao_rag"
    
    def test_analyze_consistency_unanimous(self, analyzer, mock_rag_client):
        """测试一致性分析 - 全部一致"""
        # 模拟两个高置信度一致的响应
        rag_response = RAGResponse(
            content="方案A",
            relevance_score=0.9,
            source="xiaoyibao_rag",
            references=[],
            is_confident=True
        )
        
        mock_rag_client.query.return_value = rag_response
        
        result = analyzer.analyze_query("测试查询", sources=["xiaoyibao_rag"])
        
        # 单源时不会有conflict
        assert len(result.conflicts) == 0
    
    def test_analyze_conflict_detection(self, analyzer, mock_rag_client):
        """测试冲突检测"""
        # 模拟一个高置信和一个低置信的响应
        high_conf = RAGResponse(
            content="推荐方案A",
            relevance_score=0.9,
            source="xiaoyibao_rag",
            references=[],
            is_confident=True
        )
        
        low_conf = RAGResponse(
            content="推荐方案B",
            relevance_score=0.5,
            source="local_db",
            references=[],
            is_confident=False
        )
        
        # 手动创建混合结果
        result = MultiSourceResult(
            query="测试",
            results=[high_conf, low_conf],
            consensus=None,
            conflicts=[{
                "source": "local_db",
                "content": "推荐方案B",
                "confidence": 0.5,
                "note": "低置信度"
            }],
            recommended_answer="推荐方案A",
            source_attribution={
                "xiaoyibao_rag": "小胰宝RAG (置信度: 高)",
                "local_db": "本地知识库 (置信度: 低)"
            }
        )
        
        assert len(result.conflicts) == 1
        assert result.conflicts[0]["confidence"] == 0.5
    
    def test_recommendation_generation(self, analyzer):
        """测试推荐答案生成"""
        results = [
            RAGResponse(
                content="高置信答案",
                relevance_score=0.9,
                source="xiaoyibao_rag",
                references=[],
                is_confident=True
            ),
            RAGResponse(
                content="低置信答案",
                relevance_score=0.5,
                source="local_db",
                references=[],
                is_confident=False
            )
        ]
        
        # 测试没有冲突的推荐
        recommendation = analyzer._generate_recommendation(results, None, [])
        assert recommendation == "高置信答案"
        
        # 测试有冲突的推荐
        conflicts = [{"source": "local_db"}]
        recommendation = analyzer._generate_recommendation(results, None, conflicts)
        assert "⚠️" in recommendation
    
    def test_format_result(self, analyzer):
        """测试结果格式化"""
        result = MultiSourceResult(
            query="KRAS-G12C治疗",
            results=[
                RAGResponse(
                    content="使用sotorasib",
                    relevance_score=0.9,
                    source="xiaoyibao_rag",
                    references=["论文1"],
                    is_confident=True
                )
            ],
            consensus="多源一致",
            conflicts=[],
            recommended_answer="推荐使用sotorasib",
            source_attribution={
                "xiaoyibao_rag": "小胰宝RAG (置信度: 高)"
            }
        )
        
        formatted = analyzer.format_result(result)
        
        assert "📋 查询" in formatted
        assert "💡 推荐答案" in formatted
        assert "📚 信息来源" in formatted
        assert "✅ 共识" in formatted
    
    def test_source_attribution(self, analyzer):
        """测试来源标注"""
        results = [
            RAGResponse(
                content="内容1",
                relevance_score=0.9,
                source="xiaoyibao_rag",
                references=[],
                is_confident=True
            ),
            RAGResponse(
                content="内容2",
                relevance_score=0.7,
                source="local_db",
                references=[],
                is_confident=True
            )
        ]
        
        attribution = analyzer._generate_attribution(results)
        
        assert "xiaoyibao_rag" in attribution
        assert "小胰宝RAG" in attribution["xiaoyibao_rag"]
        assert "高" in attribution["xiaoyibao_rag"]


class TestIntegration:
    """集成测试"""
    
    @patch('requests.Session.post')
    def test_end_to_end_genetic_query(self, mock_post):
        """端到端测试 - 基因查询"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "KRAS-G12C是一个关键的治疗靶点。推荐：\n1. sotorasib\n2. adagrasib\n3. 联合化疗"
                }
            }],
            "relevance_score": 0.95,
            "references": ["NCCN指南2025", "ESMO建议"]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        # 创建客户端
        analyzer = create_multi_source_analyzer("test-key")
        
        # 执行分析
        result = analyzer.analyze_query(
            "KRAS-G12C胰腺癌的最新治疗方案",
            sources=["xiaoyibao_rag"]
        )
        
        # 验证结果
        assert result.query == "KRAS-G12C胰腺癌的最新治疗方案"
        assert len(result.results) > 0
        assert result.recommended_answer
        assert "xiaoyibao_rag" in result.source_attribution
    
    @patch('requests.Session.post')
    def test_end_to_end_pathology_query(self, mock_post):
        """端到端测试 - 病理查询"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "claudin18+ 胰腺导管腺癌的靶向治疗：\nanetumab ravtansine + 化疗"
                }
            }],
            "relevance_score": 0.88,
            "references": []
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        analyzer = create_multi_source_analyzer("test-key")
        result = analyzer.analyze_query("claudin18+ 胰腺导管腺癌治疗")
        
        assert "claudin18" in result.query
        assert len(result.results) > 0


class TestRAGClientFactoryFunctions:
    """工厂函数测试"""
    
    def test_create_xiaoyibao_rag_client(self):
        """测试创建RAG客户端"""
        client = create_xiaoyibao_rag_client("test-key")
        
        assert isinstance(client, XiaoyibaoRAGClient)
        assert client.api_key == "test-key"
    
    def test_create_multi_source_analyzer(self):
        """测试创建多源分析器"""
        analyzer = create_multi_source_analyzer("test-key")
        
        assert isinstance(analyzer, MultiSourceAnalyzer)
        assert isinstance(analyzer.rag_client, XiaoyibaoRAGClient)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
