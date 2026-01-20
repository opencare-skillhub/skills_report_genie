"""内容提取模块

从各种文件格式中提取文本内容
支持：PDF、图片（OCR）、Word、Excel
参考: DEVELOPMENT_PLAN.md § 2.0.2
"""

import os
import re
import math
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# 问题1修复：在任何地方都能正确加载.env
try:
    from dotenv import load_dotenv
    # 向上查找.env（支持从skill子目录调用）
    for candidate in [Path.cwd() / '.env', Path(__file__).parent.parent.parent / '.env']:
        if candidate.exists():
            load_dotenv(str(candidate))
            break
except ImportError:
    pass

# 设置Hugging Face镜像（默认使用国内镜像）
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExtractionMethod(Enum):
    """提取方法枚举"""
    OCR = "ocr"
    TEXT = "text"
    PARSING = "parsing"
    UNKNOWN = "unknown"


@dataclass
class ExtractionResult:
    """内容提取结果"""
    text: str                          # 提取的文本内容
    file_type: str                     # 文件类型
    extraction_method: ExtractionMethod  # 提取方法
    confidence: float                  # 提取置信度
    language: str = "zh"               # 语言
    raw_data: Optional[Dict] = None    # 原始数据
    error: Optional[str] = None        # 错误信息


class ContentExtractor:
    """统一的内容提取接口
    
    支持多种文件格式的内容提取：
    - PDF（文本提取 + OCR fallback）
    - 图片（OCR）
    - Word文档
    - Excel表格
    """
    
    def __init__(self, use_vl_model: bool = True):
        """初始化提取器
        
        Args:
            use_vl_model: 是否使用VL多模态模型（推荐，更快更准确）
        """
        self._ocr_engine = None
        self._vl_model = None
        self.use_vl_model = use_vl_model
        self._init_lazy()
    
    def _init_lazy(self):
        """延迟初始化（避免启动时加载所有库）"""
        pass
    
    def _get_vl_model(self):
        """延迟加载VL多模态模型（使用Google Gemini）"""
        if self._vl_model is None:
            try:
                import google.generativeai as genai
                import os
                
                # 尝试加载.env文件
                try:
                    from dotenv import load_dotenv
                    load_dotenv()
                except ImportError:
                    pass  # python-dotenv未安装，跳过
                
                # 配置Gemini API
                api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
                if not api_key:
                    raise ValueError("未找到GOOGLE_API_KEY或GEMINI_API_KEY环境变量")
                
                genai.configure(api_key=api_key)
                self._vl_model = genai.GenerativeModel('gemini-3-flash-preview')
                logger.info("✓ VL多模态模型已启用（Gemini 3.0 Flash Preview）")
            except ImportError:
                logger.error("❌ google-generativeai未安装，请运行: pip install google-generativeai")
                raise
            except Exception as e:
                logger.error(f"❌ VL模型初始化失败: {e}")
                raise
        return self._vl_model
    
    def _get_ocr_engine(self):
        """延迟加载OCR引擎（备用方案）"""
        if self._ocr_engine is None:
            try:
                from paddleocr import PaddleOCR
                # 初始化OCR引擎（中文+英文）
                self._ocr_engine = PaddleOCR(
                    use_angle_cls=True,
                    lang='ch'
                )
                logger.info("✓ PaddleOCR引擎初始化成功")
            except ImportError:
                logger.error("❌ PaddleOCR未安装，请运行: pip install paddleocr")
                raise
            except Exception as e:
                logger.error(f"❌ OCR引擎初始化失败: {e}")
                raise
        return self._ocr_engine
    
    def extract(self, file_path: str) -> ExtractionResult:
        """
        自动识别文件类型并提取内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            ExtractionResult: 提取结果
        """
        if not os.path.exists(file_path):
            return ExtractionResult(
                text="",
                file_type="unknown",
                extraction_method=ExtractionMethod.UNKNOWN,
                confidence=0.0,
                error=f"文件不存在: {file_path}"
            )
        
        # 获取文件扩展名
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            # 根据扩展名选择提取方法
            if ext == '.pdf':
                return self.extract_pdf(file_path)
            elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic']:
                return self.extract_image(file_path)
            elif ext in ['.doc', '.docx']:
                return self.extract_word(file_path)
            elif ext in ['.xls', '.xlsx']:
                return self.extract_excel(file_path)
            elif ext in ['.txt', '.csv', '.md']:
                return self.extract_text(file_path)
            else:
                return ExtractionResult(
                    text="",
                    file_type=ext,
                    extraction_method=ExtractionMethod.UNKNOWN,
                    confidence=0.0,
                    error=f"不支持的文件类型: {ext}"
                )
        except Exception as e:
            logger.error(f"⚠️  提取失败 {file_path}: {e}")
            return ExtractionResult(
                text="",
                file_type=ext,
                extraction_method=ExtractionMethod.UNKNOWN,
                confidence=0.0,
                error=str(e)
            )
    
    def extract_pdf(self, file_path: str) -> ExtractionResult:
        """
        PDF文本提取（优先级：Pandoc → pymupdf-4o → pypdf → OCR）
        问题2修复：本地优先提取策略
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            ExtractionResult: 提取结果
        """
        # 优先1：Pandoc本地转换
        result = self._extract_pdf_with_pandoc(file_path)
        if result and result.text:
            logger.info(f"✓ Pandoc PDF提取成功")
            return result
        
        # 优先2：pymupdf-4o最佳JSON提取
        result = self._extract_pdf_with_pymupdf4o(file_path)
        if result and result.text:
            logger.info(f"✓ pymupdf-4o PDF提取成功")
            return result
        
        # 备选3：pypdf文本提取
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(file_path)
            text_parts = []
            
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            combined_text = "\n".join(text_parts).strip()
            
            if len(combined_text) > 50:
                logger.info(f"✓ pypdf PDF提取成功")
                return ExtractionResult(
                    text=combined_text,
                    file_type="pdf",
                    extraction_method=ExtractionMethod.TEXT,
                    confidence=0.9,
                    language="zh"
                )
        except ImportError:
            logger.warning("⚠️  pypdf未安装，跳过")
        except Exception as e:
            logger.warning(f"⚠️  pypdf提取失败: {e}")
        
        # 最后降级4：OCR
        logger.info(f"本地提取失败，回退到OCR: {file_path}")
        return self._ocr_pdf(file_path)
    
    def _ocr_pdf(self, file_path: str) -> ExtractionResult:
        """
        对PDF进行OCR识别 (使用PyMuPDF转图片后处理)
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            ExtractionResult: OCR结果
        """
        try:
            import fitz  # PyMuPDF
            from PIL import Image
            
            doc = fitz.open(file_path)
            text_parts = []
            confidence_scores = []
            
            logger.info(f"开始PDF OCR处理: {file_path}, 共 {len(doc)} 页")
            
            for i, page in enumerate(doc):
                # 将PDF页面渲染为图片 (300 DPI)
                pix = page.get_pixmap(dpi=300)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # 识别当前页
                page_result = None
                
                # 优先使用VL模型
                if self.use_vl_model:
                    try:
                        page_result = self._extract_image_with_vl(img)
                    except Exception as e:
                        logger.warning(f"第 {i+1} 页 VL模型识别失败，尝试回退OCR: {e}")
                
                # 如果VL失败或未启用，使用OCR
                if page_result is None:
                    try:
                        page_result = self._extract_image_with_ocr(img)
                    except Exception as e:
                        logger.error(f"第 {i+1} 页 OCR识别失败: {e}")
                        continue
                
                if page_result and page_result.text:
                    text_parts.append(f"--- Page {i+1} ---\n{page_result.text}")
                    confidence_scores.append(page_result.confidence)
            
            combined_text = "\n\n".join(text_parts)
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            return ExtractionResult(
                text=combined_text,
                file_type="pdf",
                extraction_method=ExtractionMethod.OCR,
                confidence=avg_confidence,
                language="zh"
            )
            
        except ImportError:
            logger.error("❌ pymupdf未安装，请运行: pip install pymupdf")
            return ExtractionResult(
                text="",
                file_type="pdf",
                extraction_method=ExtractionMethod.OCR,
                confidence=0.0,
                error="pymupdf未安装"
            )
        except Exception as e:
            logger.error(f"❌ PDF OCR处理失败: {e}")
            return ExtractionResult(
                text="",
                file_type="pdf",
                extraction_method=ExtractionMethod.OCR,
                confidence=0.0,
                error=str(e)
            )
    
    def extract_image(self, file_path: str) -> ExtractionResult:
        """
        图片内容识别（Step-1o-Vision -> Qwen2.5VL -> Gemini -> OCR）
        
        降级顺序（按速度和准确性）：
        1. Step-1o-Vision-turbo (StepFun) - 最快最准
        2. Qwen2.5VL (SiliconFlow) - 高精度
        3. Gemini-3-Flash (Google VL) - 备选方案
        4. PaddleOCR (本地) - 最后方案
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            ExtractionResult: 识别结果
        """
        # 1. 尝试 Step-1o-Vision-turbo (StepFun)
        try:
            step_key = os.environ.get("STEPFUN_API_KEY")
            if step_key:
                return self._extract_image_with_stepfun(file_path)
        except Exception as e:
            logger.warning(f"⚠️  Step-1o-Vision-turbo 识别失败，尝试Qwen2.5VL: {e}")

        # 2. 尝试 Qwen2.5VL (SiliconFlow)
        try:
            sf_key = os.environ.get("SILICONFLOW_API_KEY")
            if sf_key:
                return self._extract_image_with_qwen25vl(file_path)
        except Exception as e:
            logger.warning(f"⚠️  Qwen2.5VL识别失败，尝试Gemini: {e}")

        # 3. 尝试 Gemini (VL模型)
        if self.use_vl_model:
            try:
                return self._extract_image_with_vl(file_path)
            except Exception as e:
                logger.warning(f"⚠️  Gemini识别失败，回退到PaddleOCR: {e}")
                
        # 4. Fallback到本地OCR
        return self._extract_image_with_ocr(file_path)

    def _extract_image_with_stepfun(self, image_input: Any) -> ExtractionResult:
        """
        使用 StepFun 的 step-1o-turbo-vision 模型识别图片内容
        使用 OpenAI SDK 调用 (兼容 StepFun API)
        
        Args:
            image_input: 图片文件路径(str) 或 PIL Image对象
            
        Returns:
            ExtractionResult: 识别结果
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("请安装 openai: pip install openai")
        
        import json
        
        api_key = os.environ.get("STEPFUN_API_KEY")
        base_url = os.environ.get("STEPFUN_BASE_URL", "https://api.stepfun.com/v1")
        model = os.environ.get("STEPFUN_MODEL", "step-1o-turbo-vision")
        
        if not api_key:
            raise ValueError("未配置 STEPFUN_API_KEY")
        
        source_desc = image_input if isinstance(image_input, str) else "memory_image"
        logger.info(f"正在调用 StepFun ({model})...")
        
        # 初始化 OpenAI 客户端（兼容 StepFun API）
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        # 准备系统提示
        system_prompt = "你是由阶跃星辰提供的AI助手。你是一个专业的医疗数据提取专家，能够从医疗报告图片中精准提取和组织结构化信息。请确保提取的信息准确无误，并以指定的JSON格式输出。"
        
        # 准备用户提示
        user_prompt = """请分析这张医疗图片，提取所有内容并按以下JSON格式输出。
        如果图片模糊或无法识别，请在error字段说明。

        JSON格式要求：
        {
            "patient_name": "患者姓名（如有）",
            "report_date": "报告日期（YYYY-MM-DD格式，如有）",
            "report_type": "报告类型（如：血常规、生化、CT影像、病理报告、处方用药等）",
            "summary": "简要总结报告的关键发现（不超过200字）",
            "full_text": "图片中所有可见文字的完整逐字转录",
            "indicators": [
                {
                    "name": "指标名称（如CA19-9）",
                    "value": "数值",
                    "unit": "单位",
                    "reference_range": "参考范围",
                    "is_abnormal": true/false,
                    "arrow": "↑/↓/-"
                }
            ],
            "findings": "影像/病理报告的详细发现描述（非检验报告填此项）",
            "diagnosis": "诊断结论"
        }
        
        请直接输出纯JSON字符串，不要包含Markdown代码块标记。"""
        
        try:
            # 编码图片为base64
            base64_image = self._encode_image_to_base64(image_input)
            
            # 调用 StepFun API（使用 OpenAI SDK）
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    },
                ],
                temperature=0.1,
                max_tokens=4096,
            )
            
            content = response.choices[0].message.content.strip()
            
            # 清理可能的Markdown标记
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            try:
                extracted_data = json.loads(content)
                raw_text = extracted_data.get("full_text", "")
                
                if not raw_text:
                    raw_text = f"报告类型: {extracted_data.get('report_type', '未知')}\n"
                    raw_text += f"诊断: {extracted_data.get('diagnosis', '')}\n"
                
                confidence = 0.98
                
                logger.info(f"✓ StepFun (step-1o-turbo-vision) 识别成功: {source_desc}")
                
                return ExtractionResult(
                    text=raw_text,
                    file_type="image",
                    extraction_method=ExtractionMethod.OCR,
                    confidence=confidence,
                    language="zh",
                    raw_data=extracted_data
                )
                
            except json.JSONDecodeError:
                logger.warning(f"StepFun未返回有效JSON，降级为普通文本: {source_desc}")
                return ExtractionResult(
                    text=content,
                    file_type="image",
                    extraction_method=ExtractionMethod.OCR,
                    confidence=0.7,
                    language="zh",
                    raw_data={"full_text": content}
                )
        
        except Exception as e:
            logger.error(f"StepFun API 调用失败: {e}")
            raise

    def _encode_image_to_base64(self, image_input: Any) -> str:
        """将图片转换为base64字符串"""
        import base64
        from io import BytesIO
        from PIL import Image

        if isinstance(image_input, str):
            with open(image_input, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        elif isinstance(image_input, Image.Image):
            buffered = BytesIO()
            image_input.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
        else:
            raise ValueError(f"不支持的图片类型: {type(image_input)}")

    def _extract_image_with_qwen25vl(self, image_input: Any) -> ExtractionResult:
        """
        问题3修复：使用SiliconFlow的Qwen2.5VL-32B-Instruct模型识别图片内容
        修复Qwen2.5VL PDF转换失败问题 - 使用正确的API调用方法
        
        Args:
            image_input: 图片文件路径(str) 或 PIL Image对象
            
        Returns:
            ExtractionResult: 识别结果
        """
        try:
            from openai import OpenAI
            import json
        except ImportError:
            raise ImportError("请安装 openai: pip install openai")
        
        api_key = os.environ.get("SILICONFLOW_API_KEY")
        base_url = os.environ.get("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
        
        if not api_key:
            raise ValueError("未配置 SILICONFLOW_API_KEY")
        
        source_desc = image_input if isinstance(image_input, str) else "memory_image"
        logger.info(f"正在调用 Qwen2.5VL...")
        
        try:
            # 初始化OpenAI客户端（SiliconFlow兼容）
            client = OpenAI(api_key=api_key, base_url=base_url)
            
            # 编码图片为base64
            base64_image = self._encode_image_to_base64(image_input)
            
            # 医学专用提示词
            user_prompt = """请分析这张医疗图片，提取所有内容并按以下JSON格式输出。
如果图片模糊或无法识别，请在error字段说明。

JSON格式要求：
{
    "patient_name": "患者姓名（如有）",
    "report_date": "报告日期（YYYY-MM-DD格式，如有）",
    "report_type": "报告类型（如：血常规、生化、CT影像、病理报告、处方用药等）",
    "summary": "简要总结报告的关键发现（不超过200字）",
    "full_text": "图片中所有可见文字的完整逐字转录",
    "indicators": [
        {
            "name": "指标名称（如CA19-9）",
            "value": "数值",
            "unit": "单位",
            "reference_range": "参考范围",
            "is_abnormal": true/false,
            "arrow": "↑/↓/-"
        }
    ],
    "findings": "影像/病理报告的详细发现描述（非检验报告填此项）",
    "diagnosis": "诊断结论"
}

请直接输出纯JSON字符串，不要包含Markdown代码块标记。"""
            
            # 调用Qwen2.5VL
            response = client.chat.completions.create(
                model="Qwen/Qwen2.5-VL-32B-Instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                temperature=0.1,
                max_tokens=2048,
            )
            
            content = response.choices[0].message.content.strip()
            
            # 清理Markdown标记
            content = content.replace("```json", "").replace("```", "").strip()
            
            try:
                extracted_data = json.loads(content)
                raw_text = extracted_data.get("full_text", "")
                
                if not raw_text:
                    raw_text = f"报告类型: {extracted_data.get('report_type', '未知')}\n"
                    raw_text += f"诊断: {extracted_data.get('diagnosis', '')}\n"
                
                logger.info(f"✓ Qwen2.5VL识别成功: {source_desc}")
                
                return ExtractionResult(
                    text=raw_text,
                    file_type="image",
                    extraction_method=ExtractionMethod.OCR,
                    confidence=0.92,
                    language="zh",
                    raw_data=extracted_data
                )
                
            except json.JSONDecodeError:
                logger.warning(f"Qwen2.5VL未返回有效JSON，降级为普通文本: {source_desc}")
                return ExtractionResult(
                    text=content,
                    file_type="image",
                    extraction_method=ExtractionMethod.OCR,
                    confidence=0.7,
                    language="zh",
                    raw_data={"full_text": content}
                )
        
        except Exception as e:
            logger.error(f"Qwen2.5VL API调用失败: {e}")
            raise
    
    
    def _extract_image_with_vl(self, image_input: Any) -> ExtractionResult:
        """
        使用VL多模态模型识别图片内容
        
        Args:
            image_input: 图片文件路径(str) 或 PIL Image对象
            
        Returns:
            ExtractionResult: 识别结果
        """
        try:
            from PIL import Image
            
            # 获取VL模型
            model = self._get_vl_model()
            
            # 处理输入
            if isinstance(image_input, str):
                img = Image.open(image_input)
                source_desc = image_input
            else:
                img = image_input
                source_desc = "memory_image"
            
            # 调用Gemini Vision API
            prompt = """
            请分析这张医疗图片，提取所有内容并按以下JSON格式输出。
            如果图片模糊或无法识别，请在error字段说明。

            JSON格式要求：
            {
                "patient_name": "患者姓名（如有）",
                "report_date": "报告日期（YYYY-MM-DD格式，如有）",
                "report_type": "报告类型（如：血常规、生化、CT影像、病理报告、处方等）",
                "summary": "简要总结报告的关键发现（不超过200字）",
                "full_text": "图片中所有可见文字的完整逐字转录",
                "indicators": [  # 仅针对检验/检查报告
                    {
                        "name": "指标名称（如CA19-9）",
                        "value": "数值",
                        "unit": "单位",
                        "reference_range": "参考范围",
                        "is_abnormal": true/false, # 根据参考范围判断
                        "arrow": "↑/↓/-" # 原始报告中的箭头标记
                    }
                ],
                "findings": "影像/病理报告的详细发现描述（非检验报告填此项）",
                "diagnosis": "诊断结论"
            }
            
            请直接输出纯JSON字符串，不要包含Markdown代码块标记（```json）。
            """
            
            response = model.generate_content([prompt, img])
            response_text = response.text.strip()
            
            # 清理可能的Markdown标记
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            import json
            extracted_data = {}
            raw_text = ""
            
            try:
                extracted_data = json.loads(response_text)
                raw_text = extracted_data.get("full_text", "")
                
                # 如果没有full_text，尝试构建一个
                if not raw_text:
                     raw_text = f"报告类型: {extracted_data.get('report_type', '未知')}\n"
                     raw_text += f"诊断: {extracted_data.get('diagnosis', '')}\n"
                     raw_text += f"发现: {extracted_data.get('findings', '')}\n"
            except json.JSONDecodeError:
                logger.warning(f"VL模型未返回有效JSON，降级为普通文本: {source_desc}")
                raw_text = response_text
                extracted_data = {"full_text": raw_text}

            # 计算置信度
            confidence = 0.95 if len(raw_text) > 50 else 0.7
            
            logger.info(f"✓ VL模型识别成功: {source_desc} ({len(raw_text)} 字符)")
            
            return ExtractionResult(
                text=raw_text,
                file_type="image",
                extraction_method=ExtractionMethod.OCR,  # 虽然用的是VL，但本质也是文字识别
                confidence=confidence,
                language="zh",
                raw_data=extracted_data
            )
            
        except Exception as e:
            logger.error(f"⚠️  VL模型识别失败 {source_desc}: {e}")
            raise
    
    def _extract_image_with_ocr(self, image_input: Any) -> ExtractionResult:
        """
        使用OCR识别图片（备用方案）
        支持 PaddleOCR (标准版) 和 PaddleX (新版) 的输出格式
        """
        try:
            import numpy as np
            from PIL import Image
            
            # 获取OCR引擎
            ocr = self._get_ocr_engine()
            
            # 准备OCR输入
            ocr_input = None
            source_desc = "unknown"
            
            if isinstance(image_input, str):
                source_desc = image_input
                # HEIC格式需要转换
                if image_input.lower().endswith('.heic'):
                    image_input = self._convert_heic_to_jpg(image_input)
                    source_desc = image_input
                ocr_input = image_input
            elif isinstance(image_input, Image.Image):
                source_desc = "memory_image"
                # PIL Image 转 numpy array
                ocr_input = np.array(image_input)
            else:
                raise ValueError(f"不支持的图像输入类型: {type(image_input)}")
            
            # 执行OCR
            # 注意: PaddleOCR.ocr() 的参数行为可能随版本变化
            result = ocr.ocr(ocr_input)
            
            # 提取文本
            text_parts = []
            
            # Debug
            # logger.info(f"OCR raw result type: {type(result)}")
            
            # Case 1: 标准 PaddleOCR 列表格式 [[[[x,y],...], ("text", score)], ...]
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
                 for line in result[0]:
                    if isinstance(line, list) and len(line) >= 2:
                        # line[1] 是 ("text", score) 元组
                        text_parts.append(line[1][0])
            
            # Case 2: PaddleX OCRResult 对象列表
            elif isinstance(result, list) and len(result) > 0 and hasattr(result[0], 'rec_text'):
                # 如果是 PaddleX 的 OCRResult 对象，通常包含 rec_text 属性
                 for res in result:
                     if hasattr(res, 'rec_text'):
                         text_parts.append(res.rec_text)
            
            # Case 3: PaddleX Structure Result (General Layout Analysis)
            elif isinstance(result, list) and len(result) > 0:
                 # 尝试泛化处理，打印第一个元素的属性以辅助调试（如果还是失败）
                 first_item = result[0]
                 # logger.info(f"Unknown OCR result item structure: {type(first_item)}, dir: {dir(first_item)}")
                 
                 # 尝试通过字符串转换获取内容
                 if hasattr(first_item, '__str__'):
                     text_content = str(first_item)
                     # 简单的清理逻辑，视具体输出格式而定
                     text_parts.append(text_content)
            
            combined_text = "\n".join(text_parts).strip()
            
            # 如果依然为空且结果不为空，尝试直接从 repr 获取信息
            if not combined_text and result:
                 combined_text = str(result)
            
            # 计算置信度
            confidence = min(0.95, 0.5 + len(combined_text) / 1000)
            
            return ExtractionResult(
                text=combined_text,
                file_type="image",
                extraction_method=ExtractionMethod.OCR,
                confidence=confidence,
                language="zh"
            )
            
        except Exception as e:
            logger.error(f"⚠️  OCR识别失败 {source_desc}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return ExtractionResult(
                text="",
                file_type="image",
                extraction_method=ExtractionMethod.OCR,
                confidence=0.0,
                error=str(e)
            )
    
    def _convert_heic_to_jpg(self, heic_path: str) -> str:
        """
        将HEIC格式转换为JPG
        
        Args:
            heic_path: HEIC文件路径
            
        Returns:
            str: 转换后的JPG文件路径
        """
        try:
            from PIL import Image
            import pillow_heif
            
            # 注册HEIF格式
            pillow_heif.register_heif_opener()
            
            # 打开HEIC文件
            img = Image.open(heic_path)
            
            # 生成JPG路径
            jpg_path = heic_path.rsplit('.', 1)[0] + '_converted.jpg'
            
            # 转换为RGB并保存
            img.convert('RGB').save(jpg_path, 'JPEG')
            
            logger.info(f"✓ HEIC转换成功: {jpg_path}")
            return jpg_path
            
        except ImportError:
            logger.warning("pillow-heif未安装，跳过HEIC转换")
            return heic_path
        except Exception as e:
            logger.error(f"⚠️  HEIC转换失败: {e}")
            return heic_path
    
    def extract_word(self, file_path: str) -> ExtractionResult:
        """
        Word文档解析
        
        Args:
            file_path: Word文件路径
            
        Returns:
            ExtractionResult: 提取结果
        """
        try:
            from docx import Document
            
            doc = Document(file_path)
            text_parts = []
            
            # 提取段落文本
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)
            
            # 提取表格文本
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text.strip())
                    if row_text:
                        text_parts.append(" | ".join(row_text))
            
            combined_text = "\n".join(text_parts)
            
            return ExtractionResult(
                text=combined_text,
                file_type="word",
                extraction_method=ExtractionMethod.PARSING,
                confidence=0.95,
                language="zh"
            )
            
        except ImportError:
            logger.error("❌ python-docx未安装，请运行: pip install python-docx")
            return ExtractionResult(
                text="",
                file_type="word",
                extraction_method=ExtractionMethod.UNKNOWN,
                confidence=0.0,
                error="python-docx未安装"
            )
        except Exception as e:
            logger.error(f"⚠️  Word解析失败 {file_path}: {e}")
            return ExtractionResult(
                text="",
                file_type="word",
                extraction_method=ExtractionMethod.PARSING,
                confidence=0.0,
                error=str(e)
            )
    
    def extract_excel(self, file_path: str) -> ExtractionResult:
        """
        Excel数据读取
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            ExtractionResult: 提取结果
        """
        try:
            from openpyxl import load_workbook
            
            wb = load_workbook(file_path, data_only=True)
            text_parts = []
            raw_data = {}
            
            # 遍历所有工作表
            for sheet_name in wb.sheetnames:
                sheet = wb[sheet_name]
                sheet_data = []
                
                # 读取所有行
                for row in sheet.iter_rows(values_only=True):
                    # 过滤空行
                    row_values = [str(cell) if cell is not None else "" for cell in row]
                    if any(row_values):
                        sheet_data.append(row_values)
                        text_parts.append(" | ".join(row_values))
                
                raw_data[sheet_name] = sheet_data
            
            combined_text = "\n".join(text_parts)
            
            return ExtractionResult(
                text=combined_text,
                file_type="excel",
                extraction_method=ExtractionMethod.PARSING,
                confidence=0.95,
                language="zh",
                raw_data=raw_data
            )
            
        except ImportError:
            logger.error("❌ openpyxl未安装，请运行: pip install openpyxl")
            return ExtractionResult(
                text="",
                file_type="excel",
                extraction_method=ExtractionMethod.PARSING,
                confidence=0.0,
                error="openpyxl未安装"
            )
        except Exception as e:
            logger.error(f"⚠️  Excel解析失败 {file_path}: {e}")
            return ExtractionResult(
                text="",
                file_type="excel",
                extraction_method=ExtractionMethod.PARSING,
                confidence=0.0,
                error=str(e)
            )
    
    def extract_text(self, file_path: str) -> ExtractionResult:
        """
        纯文本文件读取 (TXT, CSV等)
        
        Args:
            file_path: 文本文件路径
            
        Returns:
            ExtractionResult: 提取结果
        """
        try:
            # 尝试多种编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            text = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text = f.read()
                    break
                except (UnicodeDecodeError, LookupError):
                    continue
            
            if text is None:
                # 最后尝试二进制读取
                with open(file_path, 'rb') as f:
                    text = f.read().decode('utf-8', errors='ignore')
            
            return ExtractionResult(
                text=text.strip(),
                file_type="text",
                extraction_method=ExtractionMethod.TEXT,
                confidence=0.9,
                language="zh"
            )
            
        except Exception as e:
             logger.error(f"⚠️  文本文件解析失败 {file_path}: {e}")
             return ExtractionResult(
                 text="",
                 file_type="text",
                 extraction_method=ExtractionMethod.TEXT,
                 confidence=0.0,
                 error=str(e)
             )
    
    def _extract_pdf_with_pandoc(self, file_path: str) -> Optional[ExtractionResult]:
        """问题2修复：使用Pandoc本地转换PDF为Markdown/text"""
        try:
            import subprocess
            # 检查pandoc是否可用
            subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
            # 使用pandoc转换为纯文本
            result = subprocess.run(
                ['pandoc', file_path, '-t', 'plain'],
                capture_output=True, text=True, check=True
            )
            if result.stdout:
                return ExtractionResult(
                    text=result.stdout.strip(),
                    file_type="pdf",
                    extraction_method=ExtractionMethod.TEXT,
                    confidence=0.95,
                    language="zh"
                )
        except (FileNotFoundError, subprocess.CalledProcessError, Exception) as e:
            logger.debug(f"Pandoc不可用或失败: {e}")
        return None
    
    def _extract_pdf_with_pymupdf4o(self, file_path: str) -> Optional[ExtractionResult]:
        """问题2修复：使用pymupdf-4o进行最佳PDF JSON提取"""
        try:
            import pymupdf4llm
            
            # pymupdf4llm专为LLM优化，最佳JSON提取
            md_text = pymupdf4llm.to_markdown(file_path)
            if md_text:
                # 转换markdown为纯文本
                text = md_text.replace('# ', '').replace('## ', '').replace('### ', '')
                text = '\n'.join([line for line in text.split('\n') if line.strip()])
                return ExtractionResult(
                    text=text,
                    file_type="pdf",
                    extraction_method=ExtractionMethod.TEXT,
                    confidence=0.93,
                    language="zh"
                )
        except (ImportError, Exception) as e:
            logger.debug(f"pymupdf4llm不可用或失败: {e}")
        return None
