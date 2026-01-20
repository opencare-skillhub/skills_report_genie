"""内容分类器模块

基于提取的内容进行智能分类
参考: DEVELOPMENT_PLAN.md § 2.0.2
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import re
from src.file_handler.file_category import FileCategory


@dataclass
class ClassificationResult:
    """分类结果"""
    category: FileCategory      # 分类类别
    confidence: float           # 置信度 (0-1)
    reasoning: str              # 分类理由
    keywords_found: List[str]   # 找到的关键词
    method: str                 # 分类方法 (content/filename/hybrid)


class ContentClassifier:
    """基于内容的智能分类器
    
    综合文件内容和文件名进行分类
    内容权重 0.8，文件名权重 0.2
    """
    
    # 基于内容的分类规则
    CONTENT_CLASSIFICATION_RULES = {
        FileCategory.LAB_REPORTS: {
            "keywords": [
                # 检验报告关键词
                "检验报告", "化验单", "血液检查", "肿瘤标志物",
                "CA19-9", "CA50", "CA125", "CA72-4", "CEA",
                "白细胞", "血红蛋白", "血小板", "中性粒细胞",
                "肝功能", "肾功能", "电解质", "血糖",
                "ALT", "AST", "TBIL", "DBIL", "ALP",
                "肌酐", "尿素氮", "尿酸",
                "检测结果", "参考范围", "检验日期"
            ],
            "weight": 1.0,
            "min_keywords": 2  # 至少匹配2个关键词
        },
        FileCategory.IMAGING: {
            "keywords": [
                # 影像报告关键词
                "影像报告", "CT", "MRI", "超声", "B超", "X光", "X线",
                "增强扫描", "平扫", "DICOM", "放射科",
                "病灶", "肿块", "占位", "转移", "淋巴结",
                "胰腺", "肝脏", "脾脏", "肾脏",
                "增强期", "动脉期", "静脉期", "延迟期",
                "影像学表现", "影像诊断", "CT值", "信号强度"
            ],
            "weight": 1.0,
            "min_keywords": 2
        },
        FileCategory.MEDICAL_RECORDS: {
            "keywords": [
                # 病历关键词
                "病历", "病史", "主诉", "现病史", "既往史", "家族史",
                "诊断", "医嘱", "查房记录", "出院小结", "入院记录",
                "体格检查", "专科检查", "初步诊断", "诊疗计划",
                "病程记录", "医生签名", "主治医师"
            ],
            "weight": 0.9,
            "min_keywords": 2
        },
        FileCategory.PRESCRIPTIONS: {
            "keywords": [
                # 处方用药关键词
                "处方", "用药", "药物", "给药", "化疗", "放疗",
                "吉西他滨", "顺铂", "奥沙利铂", "卡培他滨",
                "化疗方案", "FOLFIRINOX", "AG方案", "GP方案",
                "用法用量", "静脉滴注", "口服", "注射",
                "药品名称", "规格", "剂量"
            ],
            "weight": 0.95,
            "min_keywords": 2
        },
        FileCategory.COMPLICATIONS: {
            "keywords": [
                # 并发症关键词
                "并发症", "感染", "胰漏", "消化不良", "疼痛", "副作用",
                "胆管梗阻", "肠梗阻", "门脉高压", "血栓",
                "胃底静脉曲张", "腹水", "黄疸", "发热",
                "恶心", "呕吐", "腹泻", "便秘"
            ],
            "weight": 0.85,
            "min_keywords": 2
        },
        FileCategory.PSYCHOLOGY: {
            "keywords": [
                # 心理支持关键词
                "心理", "焦虑", "抑郁", "心理咨询", "心理评估",
                "情绪", "心理状态", "心理健康", "心理治疗",
                "焦虑量表", "抑郁量表", "心理干预"
            ],
            "weight": 0.8,
            "min_keywords": 2
        },
        FileCategory.NUTRITION: {
            "keywords": [
                # 营养管理关键词
                "营养", "饮食", "进食", "体重", "营养支持",
                "营养评估", "营养不良", "营养状况",
                "蛋白质", "热量", "膳食", "食谱",
                "肠内营养", "肠外营养", "营养师"
            ],
            "weight": 0.8,
            "min_keywords": 2
        }
    }
    
    def __init__(self):
        """初始化分类器"""
        pass
    
    def classify(self, content: str, filename: str) -> ClassificationResult:
        """
        综合内容和文件名进行分类
        
        Args:
            content: 提取的文本内容
            filename: 文件名（辅助判断）
            
        Returns:
            ClassificationResult: 分类结果
        """
        # 1. 基于内容分类
        content_result = self._classify_by_content(content)
        
        # 2. 基于文件名分类（使用scanner的规则）
        filename_result = self._classify_by_filename(filename)
        
        # 3. 综合判断（内容权重0.8，文件名权重0.2）
        if content_result and filename_result:
            # 如果两者分类一致，提高置信度
            if content_result.category == filename_result.category:
                combined_confidence = content_result.confidence * 0.8 + filename_result.confidence * 0.2
                combined_confidence = min(0.98, combined_confidence + 0.1)  # 一致性加成
                
                return ClassificationResult(
                    category=content_result.category,
                    confidence=combined_confidence,
                    reasoning=f"内容和文件名一致: {content_result.reasoning}",
                    keywords_found=content_result.keywords_found,
                    method="hybrid"
                )
            else:
                # 分类不一致，以内容为主
                combined_confidence = content_result.confidence * 0.8 + filename_result.confidence * 0.2
                return ClassificationResult(
                    category=content_result.category,
                    confidence=combined_confidence,
                    reasoning=f"以内容为主: {content_result.reasoning}",
                    keywords_found=content_result.keywords_found,
                    method="hybrid"
                )
        elif content_result:
            # 只有内容分类结果
            return content_result
        elif filename_result:
            # 只有文件名分类结果
            return filename_result
        else:
            # 都没有，返回待确认
            return ClassificationResult(
                category=FileCategory.UNCONFIRMED,
                confidence=0.0,
                reasoning="无法识别文件类型",
                keywords_found=[],
                method="unknown"
            )
    
    def _classify_by_content(self, content: str) -> Optional[ClassificationResult]:
        """
        基于内容关键词分类
        
        Args:
            content: 文本内容
            
        Returns:
            ClassificationResult or None
        """
        if not content or len(content.strip()) < 10:
            return None
        
        content_lower = content.lower()
        best_match = None
        best_score = 0.0
        best_keywords = []
        
        # 遍历所有分类规则
        for category, rule in self.CONTENT_CLASSIFICATION_RULES.items():
            keywords = rule["keywords"]
            weight = rule["weight"]
            min_keywords = rule.get("min_keywords", 1)
            
            # 统计匹配的关键词
            matched_keywords = []
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    matched_keywords.append(keyword)
            
            # 计算匹配度
            if len(matched_keywords) >= min_keywords:
                # 基础分数：匹配关键词数 / 总关键词数
                base_score = len(matched_keywords) / len(keywords)
                
                # 应用权重
                weighted_score = base_score * weight
                
                # 关键词数量加成
                keyword_bonus = min(0.2, len(matched_keywords) * 0.02)
                final_score = min(0.95, weighted_score + keyword_bonus)
                
                if final_score > best_score:
                    best_score = final_score
                    best_match = category
                    best_keywords = matched_keywords
        
        if best_match:
            return ClassificationResult(
                category=best_match,
                confidence=best_score,
                reasoning=f"检测到{len(best_keywords)}个关键词: {', '.join(best_keywords[:5])}{'...' if len(best_keywords) > 5 else ''}",
                keywords_found=best_keywords,
                method="content"
            )
        
        return None
    
    def _classify_by_filename(self, filename: str) -> Optional[ClassificationResult]:
        """
        基于文件名分类（简化版，使用关键词匹配）
        
        Args:
            filename: 文件名
            
        Returns:
            ClassificationResult or None
        """
        filename_lower = filename.lower()
        
        # 文件名关键词规则（简化）
        filename_rules = {
            FileCategory.LAB_REPORTS: ["检查", "检验", "报告", "化验", "ca19", "ca50", "标志物"],
            FileCategory.IMAGING: ["ct", "mri", "超声", "影像", "x光", "放射"],
            FileCategory.MEDICAL_RECORDS: ["病历", "病史", "诊断", "出院", "入院"],
            FileCategory.PRESCRIPTIONS: ["处方", "用药", "化疗", "方案"],
            FileCategory.COMPLICATIONS: ["并发症", "感染", "胰漏"],
            FileCategory.PSYCHOLOGY: ["心理", "焦虑", "抑郁"],
            FileCategory.NUTRITION: ["营养", "饮食", "体重"]
        }
        
        for category, keywords in filename_rules.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    return ClassificationResult(
                        category=category,
                        confidence=0.6,  # 文件名置信度较低
                        reasoning=f"文件名包含关键词: {keyword}",
                        keywords_found=[keyword],
                        method="filename"
                    )
        
        return None
    
    def _extract_keywords(self, content: str) -> List[str]:
        """
        从内容中提取医疗关键词
        
        Args:
            content: 文本内容
            
        Returns:
            List[str]: 关键词列表
        """
        keywords = []
        content_lower = content.lower()
        
        # 收集所有规则中的关键词
        all_keywords = set()
        for rule in self.CONTENT_CLASSIFICATION_RULES.values():
            all_keywords.update(rule["keywords"])
        
        # 检查哪些关键词出现在内容中
        for keyword in all_keywords:
            if keyword.lower() in content_lower:
                keywords.append(keyword)
        
        return keywords
    
    def _calculate_confidence(self, keywords: List[str], category: FileCategory) -> float:
        """
        计算分类置信度
        
        Args:
            keywords: 匹配的关键词列表
            category: 分类类别
            
        Returns:
            float: 置信度 (0-1)
        """
        if category not in self.CONTENT_CLASSIFICATION_RULES:
            return 0.0
        
        rule = self.CONTENT_CLASSIFICATION_RULES[category]
        total_keywords = len(rule["keywords"])
        matched_keywords = len(keywords)
        
        if matched_keywords == 0:
            return 0.0
        
        # 基础置信度
        base_confidence = matched_keywords / total_keywords
        
        # 应用权重
        weighted_confidence = base_confidence * rule["weight"]
        
        # 关键词数量加成
        keyword_bonus = min(0.2, matched_keywords * 0.02)
        
        return min(0.95, weighted_confidence + keyword_bonus)
