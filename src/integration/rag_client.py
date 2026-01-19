"""
小胰宝RAG客户端
集成小胰宝社区助手的RAG能力，进行临床知识查询
"""

import requests
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class InformationSource(Enum):
    """信息来源"""
    LLM = "llm"  # Claude/GPT等
    XIAOYIBAO_RAG = "xiaoyibao_rag"  # 小胰宝RAG
    MCP = "mcp"  # Model Context Protocol
    LOCAL_DB = "local_db"  # 本地数据库


@dataclass
class RAGResponse:
    """RAG查询响应"""
    content: str
    relevance_score: float  # 0-1，相关性评分
    source: str  # 信息来源
    references: List[str]  # 引用文献或来源
    is_confident: bool  # 是否高置信度


@dataclass
class MultiSourceResult:
    """多源查询结果"""
    query: str
    results: List[RAGResponse]
    consensus: Optional[str]  # 多源一致性结论
    conflicts: List[Dict[str, Any]]  # 冲突项（不同来源有不同结论）
    recommended_answer: str  # 推荐答案
    source_attribution: Dict[str, str]  # 信息来源标注


class XiaoyibaoRAGClient:
    """
    小胰宝RAG客户端
    
    支持：
    - 基因相关问题 (KRAS突变, BRCA缺失等)
    - 病理相关问题 (导管腺癌, 标志物等)
    - 胰腺癌治疗 (化疗方案, 靶向治疗等)
    - 临床试验信息
    - 预后评估
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://admin.xiaoyibao.com.cn/v1"
    ):
        """
        初始化RAG客户端
        
        Args:
            api_key: API密钥
            base_url: API基地址
        """
        self.api_key = api_key
        self.base_url = base_url
        self.chat_endpoint = f"{base_url}/chat/completions"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def query(
        self,
        query_text: str,
        chat_id: str = "default",
        detail: bool = True,
        timeout: int = 30
    ) -> RAGResponse:
        """
        查询RAG
        
        Args:
            query_text: 查询文本
            chat_id: 会话ID
            detail: 是否返回详细信息
            timeout: 超时时间（秒）
        
        Returns:
            RAGResponse: RAG查询响应
        
        Examples:
            >>> client = XiaoyibaoRAGClient(api_key="xxx")
            >>> response = client.query("KRAS G12C突变的治疗方案")
        """
        try:
            payload = {
                "chatId": chat_id,
                "stream": False,
                "detail": detail,
                "messages": [
                    {
                        "content": query_text,
                        "role": "user"
                    }
                ]
            }
            
            response = self.session.post(
                self.chat_endpoint,
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # 解析响应
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 提取相关性评分（如果有）
            relevance_score = data.get("relevance_score", 0.8)
            
            # 提取引用
            references = data.get("references", [])
            
            # 判断置信度
            is_confident = relevance_score >= 0.7
            
            return RAGResponse(
                content=content,
                relevance_score=relevance_score,
                source="xiaoyibao_rag",
                references=references,
                is_confident=is_confident
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"RAG查询失败: {e}")
            return RAGResponse(
                content="",
                relevance_score=0,
                source="xiaoyibao_rag",
                references=[],
                is_confident=False
            )
    
    def query_genetic_info(self, gene_name: str, mutation: str) -> RAGResponse:
        """
        查询基因相关信息
        
        Args:
            gene_name: 基因名称 (如 KRAS)
            mutation: 突变描述 (如 G12C)
        
        Returns:
            RAGResponse
        """
        query_text = f"{gene_name} {mutation} 突变的临床特征、治疗方案和预后"
        return self.query(query_text)
    
    def query_pathology_info(self, pathology_type: str, marker: Optional[str] = None) -> RAGResponse:
        """
        查询病理相关信息
        
        Args:
            pathology_type: 病理类型 (如 导管腺癌)
            marker: 标志物 (如 claudin18+)
        
        Returns:
            RAGResponse
        """
        marker_part = f"，{marker}表达" if marker else ""
        query_text = f"胰腺{pathology_type}{marker_part}的临床特征、诊断标准和治疗建议"
        return self.query(query_text)
    
    def query_treatment_options(
        self,
        cancer_type: str,
        genetic_features: Optional[List[str]] = None,
        pathology_features: Optional[List[str]] = None
    ) -> RAGResponse:
        """
        查询治疗方案
        
        Args:
            cancer_type: 癌肿类型
            genetic_features: 基因特征列表
            pathology_features: 病理特征列表
        
        Returns:
            RAGResponse
        """
        features = []
        if genetic_features:
            features.extend(genetic_features)
        if pathology_features:
            features.extend(pathology_features)
        
        feature_text = "、".join(features) if features else ""
        query_text = f"胰腺{cancer_type}"
        if feature_text:
            query_text += f"({feature_text})"
        query_text += "的最新治疗方案、化疗方案、靶向治疗和免疫治疗推荐"
        
        return self.query(query_text)
    
    def query_clinical_trials(
        self,
        cancer_type: str,
        genetic_mutations: Optional[List[str]] = None,
        biomarkers: Optional[List[str]] = None
    ) -> RAGResponse:
        """
        查询相关临床试验
        
        Args:
            cancer_type: 癌肿类型
            genetic_mutations: 基因突变列表
            biomarkers: 生物标志物列表
        
        Returns:
            RAGResponse
        """
        criteria = []
        if genetic_mutations:
            criteria.extend(genetic_mutations)
        if biomarkers:
            criteria.extend(biomarkers)
        
        criteria_text = "、".join(criteria) if criteria else ""
        query_text = f"胰腺{cancer_type}"
        if criteria_text:
            query_text += f"({criteria_text})"
        query_text += "相关的临床试验、招募条件、预期获益"
        
        return self.query(query_text)
    
    def query_prognosis(
        self,
        cancer_type: str,
        risk_factors: Optional[List[str]] = None
    ) -> RAGResponse:
        """
        查询预后信息
        
        Args:
            cancer_type: 癌肿类型
            risk_factors: 风险因素列表
        
        Returns:
            RAGResponse
        """
        risk_text = "、".join(risk_factors) if risk_factors else ""
        query_text = f"胰腺{cancer_type}"
        if risk_text:
            query_text += f"({risk_text})"
        query_text += "的预后、生存期预测、风险评估"
        
        return self.query(query_text)
    
    def batch_query(self, queries: List[str]) -> List[RAGResponse]:
        """
        批量查询
        
        Args:
            queries: 查询文本列表
        
        Returns:
            RAGResponse列表
        """
        results = []
        for query_text in queries:
            result = self.query(query_text)
            results.append(result)
        return results


class MultiSourceAnalyzer:
    """
    多信息源聚合分析器
    
    整合：
    - LLM (Claude)
    - 小胰宝RAG
    - MCP
    - 本地数据库
    """
    
    def __init__(self, rag_client: XiaoyibaoRAGClient):
        """
        初始化多源分析器
        
        Args:
            rag_client: RAG客户端实例
        """
        self.rag_client = rag_client
    
    def analyze_query(
        self,
        query_text: str,
        sources: Optional[List[str]] = None,
        include_local_knowledge: bool = True
    ) -> MultiSourceResult:
        """
        多源分析查询
        
        Args:
            query_text: 查询文本
            sources: 指定查询的信息源列表
                   默认: ["xiaoyibao_rag", "local_db"]
            include_local_knowledge: 是否包含本地知识库
        
        Returns:
            MultiSourceResult: 多源聚合结果
        """
        if sources is None:
            sources = ["xiaoyibao_rag"]
            if include_local_knowledge:
                sources.append("local_db")
        
        results = []
        
        # 查询小胰宝RAG
        if "xiaoyibao_rag" in sources:
            rag_response = self.rag_client.query(query_text)
            results.append(rag_response)
        
        # 查询本地数据库（由其他模块提供）
        if "local_db" in sources:
            local_response = self._query_local_db(query_text)
            if local_response:
                results.append(local_response)
        
        # 聚合分析
        consensus, conflicts = self._analyze_consistency(results)
        recommended_answer = self._generate_recommendation(results, consensus, conflicts)
        
        return MultiSourceResult(
            query=query_text,
            results=results,
            consensus=consensus,
            conflicts=conflicts,
            recommended_answer=recommended_answer,
            source_attribution=self._generate_attribution(results)
        )
    
    def _query_local_db(self, query_text: str) -> Optional[RAGResponse]:
        """
        查询本地数据库
        
        注：实际实现需要与本地数据库集成
        """
        # 占位符，实现由其他模块提供
        return None
    
    def _analyze_consistency(
        self,
        results: List[RAGResponse]
    ) -> tuple[Optional[str], List[Dict[str, Any]]]:
        """
        分析多源结果的一致性
        
        Returns:
            (consensus, conflicts) - 一致性结论和冲突项
        """
        if not results:
            return None, []
        
        if len(results) == 1:
            return results[0].content if results[0].is_confident else None, []
        
        # 简单的一致性检查（实际可用更复杂的NLP）
        # 这里假设如果所有来源的置信度都高，则认为有共识
        high_confidence_results = [r for r in results if r.is_confident]
        
        if len(high_confidence_results) == len(results):
            # 所有来源都高置信 - 可能有共识
            consensus = "多个信息源高度一致" if len(high_confidence_results) > 1 else None
        else:
            consensus = None
        
        # 识别冲突（低置信度结果与高置信度结果）
        conflicts = []
        if high_confidence_results and len(high_confidence_results) < len(results):
            for result in results:
                if not result.is_confident:
                    conflicts.append({
                        "source": result.source,
                        "content": result.content,
                        "confidence": result.relevance_score,
                        "note": "低置信度，与其他来源可能有差异"
                    })
        
        return consensus, conflicts
    
    def _generate_recommendation(
        self,
        results: List[RAGResponse],
        consensus: Optional[str],
        conflicts: List[Dict[str, Any]]
    ) -> str:
        """
        生成推荐答案
        
        优先级：
        1. 多源高置信一致
        2. 小胰宝RAG高置信
        3. 多源综合（标注差异）
        """
        if not results:
            return "无法获得答案"
        
        # 优先级排序：xiaoyibao_rag > local_db > 其他
        sorted_results = sorted(
            results,
            key=lambda x: (
                x.is_confident,  # 置信度优先
                1 if x.source == "xiaoyibao_rag" else 0  # RAG其次
            ),
            reverse=True
        )
        
        recommended = sorted_results[0]
        
        if not conflicts:
            return recommended.content
        else:
            # 有冲突时需要标注
            return f"{recommended.content}\n\n⚠️ 注意：存在其他信息源的不同观点（见下方）"
    
    def _generate_attribution(self, results: List[RAGResponse]) -> Dict[str, str]:
        """
        生成信息来源标注
        """
        attribution = {}
        for result in results:
            source_name = self._get_source_name(result.source)
            confidence = "高" if result.is_confident else "低"
            attribution[result.source] = f"{source_name} (置信度: {confidence})"
        
        return attribution
    
    def _get_source_name(self, source: str) -> str:
        """获取来源名称"""
        source_names = {
            "xiaoyibao_rag": "小胰宝RAG",
            "local_db": "本地知识库",
            "llm": "AI模型",
            "mcp": "MCP协议"
        }
        return source_names.get(source, source)
    
    def format_result(self, result: MultiSourceResult) -> str:
        """
        格式化多源结果为可读文本
        
        Returns:
            格式化后的结果文本
        """
        lines = [f"📋 查询: {result.query}\n"]
        
        # 推荐答案
        lines.append(f"💡 推荐答案:\n{result.recommended_answer}\n")
        
        # 信息来源
        lines.append("📚 信息来源:")
        for source, attribution in result.source_attribution.items():
            lines.append(f"  • {attribution}")
        
        # 冲突项（如有）
        if result.conflicts:
            lines.append("\n⚠️ 不同观点:")
            for i, conflict in enumerate(result.conflicts, 1):
                lines.append(f"  {i}. [{conflict['source']}] 置信度 {conflict['confidence']:.0%}")
                lines.append(f"     {conflict['content']}")
                if conflict.get('note'):
                    lines.append(f"     备注: {conflict['note']}")
        
        # 共识（如有）
        if result.consensus:
            lines.append(f"\n✅ 共识: {result.consensus}")
        
        return "\n".join(lines)


# 工厂函数
def create_xiaoyibao_rag_client(api_key: str) -> XiaoyibaoRAGClient:
    """创建小胰宝RAG客户端"""
    return XiaoyibaoRAGClient(api_key=api_key)


def create_multi_source_analyzer(api_key: str) -> MultiSourceAnalyzer:
    """创建多源分析器"""
    rag_client = create_xiaoyibao_rag_client(api_key)
    return MultiSourceAnalyzer(rag_client)
