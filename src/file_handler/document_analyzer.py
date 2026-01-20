"""文档分析模块 - 使用 LLM 提取结构化数据

支持: PDF, Word, Excel, TXT
功能: 提取关键信息，生成结构化 JSON
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DocumentAnalysisResult:
    """文档分析结果"""
    file_type: str                    # 文件类型
    filename: str                     # 原始文件名
    raw_text: str                     # 原始文本内容
    structured_data: Dict[str, Any]   # 结构化数据
    confidence: float                 # 置信度
    error: Optional[str] = None       # 错误信息


class DocumentAnalyzer:
    """使用LLM分析文档，提取结构化数据"""
    
    def __init__(self):
        """初始化分析器"""
        self._vl_model = None
    
    def _get_llm_model(self):
        """延迟加载LLM模型（SiliconFlow）"""
        if self._vl_model is None:
            try:
                from openai import OpenAI
                
                api_key = os.environ.get('SILICONFLOW_API_KEY')
                
                if not api_key:
                    raise ValueError("未配置 SILICONFLOW_API_KEY")
                
                self._vl_model = OpenAI(
                    api_key=api_key,
                    base_url="https://api.siliconflow.cn/v1"
                )
                logger.info("✓ LLM 模型已初始化 (SiliconFlow Qwen2.5-VL)")
            except Exception as e:
                logger.error(f"❌ LLM 初始化失败: {e}")
                raise
        
        return self._vl_model
    
    def analyze_document(self, file_path: str, raw_text: str, file_type: str) -> DocumentAnalysisResult:
        """
        使用 LLM 分析文档并提取结构化数据
        
        Args:
            file_path: 文件路径
            raw_text: 原始提取的文本
            file_type: 文件类型 (pdf, word, excel, txt)
        
        Returns:
            DocumentAnalysisResult: 分析结果
        """
        filename = os.path.basename(file_path)
        
        try:
            # 如果文本太长，截断（避免 LLM 超时）
            max_length = 2000  # 限制为 2000 字符
            text_preview = raw_text[:max_length] if len(raw_text) > max_length else raw_text
            
            if len(raw_text) > max_length:
                logger.warning(f"文档过长 ({len(raw_text)} 字符)，仅使用前 {max_length} 字符进行分析")
            
            # 构造分析 prompt
            prompt = self._build_analysis_prompt(file_type, text_preview)
            
            # 调用 LLM
            logger.info(f"正在分析文档: {filename}")
            client = self._get_llm_model()
            
            response = client.chat.completions.create(
                model="Qwen/Qwen2.5-VL-32B-Instruct",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的医疗文档分析专家。请提取文档中的关键信息，并按照 JSON 格式输出，确保输出的 JSON 格式正确且包含所有关键字段。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=4096,
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # 清理可能的 Markdown 标记
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # 解析 JSON
            try:
                structured_data = json.loads(response_text)
            except json.JSONDecodeError:
                logger.warning(f"LLM 返回的不是有效 JSON，使用默认结构")
                structured_data = self._parse_text_fallback(raw_text, file_type)
            
            logger.info(f"✓ 文档分析成功: {filename}")
            
            return DocumentAnalysisResult(
                file_type=file_type,
                filename=filename,
                raw_text=raw_text,
                structured_data=structured_data,
                confidence=0.95
            )
        
        except Exception as e:
            logger.error(f"❌ 文档分析失败: {e}")
            # Fallback: 返回基础结构
            structured_data = self._parse_text_fallback(raw_text, file_type)
            
            return DocumentAnalysisResult(
                file_type=file_type,
                filename=filename,
                raw_text=raw_text,
                structured_data=structured_data,
                confidence=0.5,
                error=str(e)
            )
    
    def _build_analysis_prompt(self, file_type: str, text: str) -> str:
        """构建分析 prompt"""
        
        if file_type == "excel":
            return f"""
请分析以下 Excel 表格数据，提取关键信息：

{text}

请按照以下 JSON 格式输出：
{{
    "data_type": "表格数据类型（如：血液指标、化疗记录、随访记录等）",
    "table_name": "表格名称（如果有）",
    "columns": ["列1", "列2", ...],
    "key_metrics": [
        {{
            "name": "指标名称",
            "value": "数值",
            "unit": "单位",
            "reference_range": "参考范围",
            "status": "异常/正常"
        }}
    ],
    "summary": "表格内容简要总结",
    "date": "数据日期（YYYY-MM-DD格式，如有）",
    "source": "数据来源（如：实验室、医院名称等）"
}}

确保输出是有效的 JSON 格式。
"""
        
        elif file_type == "pdf":
            return f"""
请分析以下 PDF 文档内容，提取关键医疗信息：

{text}

请按照以下 JSON 格式输出：
{{
    "document_type": "文档类型（如：病历、检查报告、诊断报告等）",
    "patient_info": {{
        "name": "患者姓名（如有）",
        "age": "年龄（如有）",
        "gender": "性别（如有）",
        "id": "患者ID/医保号（如有）"
    }},
    "report_date": "报告日期（YYYY-MM-DD）",
    "diagnosis": "诊断结论",
    "key_findings": [
        {{
            "category": "分类（如：影像发现、实验室结果等）",
            "finding": "具体发现"
        }}
    ],
    "treatment_plan": "治疗方案（如有）",
    "follow_up": "随访建议（如有）",
    "doctor_name": "医生名称（如有）",
    "hospital": "医院名称（如有）",
    "summary": "文档内容总结"
}}

确保输出是有效的 JSON 格式。
"""
        
        elif file_type == "word":
            return f"""
请分析以下 Word 文档内容，提取关键医疗信息：

{text}

请按照以下 JSON 格式输出：
{{
    "document_type": "文档类型（如：病历、用药方案、康复指导等）",
    "title": "文档标题",
    "main_sections": [
        {{
            "section_name": "章节名称",
            "content": "章节内容要点"
        }}
    ],
    "key_information": {{
        "patient_name": "患者姓名（如有）",
        "disease": "疾病名称",
        "medications": ["药物1", "药物2", ...],
        "precautions": ["注意事项1", "注意事项2", ...]
    }},
    "date": "文档日期（YYYY-MM-DD）",
    "author": "作者/医生（如有）",
    "summary": "文档总结"
}}

确保输出是有效的 JSON 格式。
"""
        
        else:  # txt
            return f"""
请分析以下文本内容，提取关键医疗信息：

{text}

请按照以下 JSON 格式输出：
{{
    "content_type": "内容类型（如：病情说明、用药记录、康复日志等）",
    "main_topics": ["主题1", "主题2", ...],
    "key_information": {{
        "disease": "主要疾病",
        "status": "当前状态",
        "symptoms": ["症状1", "症状2", ...],
        "treatments": ["治疗方法1", "治疗方法2", ...]
    }},
    "timeline": {{
        "start_date": "开始日期（如有）",
        "current_date": "当前日期（如有）"
    }},
    "important_notes": ["重要说明1", "重要说明2", ...],
    "summary": "内容总结"
}}

确保输出是有效的 JSON 格式。
"""
    
    def _parse_text_fallback(self, text: str, file_type: str) -> Dict[str, Any]:
        """文本解析降级方案"""
        return {
            "file_type": file_type,
            "raw_text_preview": text[:500],
            "text_length": len(text),
            "status": "partial_parsing",
            "note": "LLM 解析失败，仅提供原始文本预览",
            "full_text_available": True
        }
