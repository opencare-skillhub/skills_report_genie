"""
Phase 4: 科普教育智能体
职责：调用Claude API，将医学术语转换为患者友好的科普内容
"""

import json
from typing import Dict, List, Optional
import anthropic


class PopularScienceAgent:
    """
    科普教育智能体
    
    核心流程：
    1. 接收结构化的病情数据（genetic_features, pathology_features等）
    2. 使用系统提示词定义角色和任务
    3. 调用Claude API生成患者友好的科普内容
    4. 返回格式化的科普报告
    """
    
    # 系统提示词 - 角色定义
    SYSTEM_PROMPT = """你是一位资深的医学科普专家，专长于将复杂的医学概念转化为患者和家属易懂的语言。

你的目标是：
1. 用简单易懂的语言解释医学术语
2. 避免使用复杂的医学专业术语，或用简单语言先解释
3. 使用类比和比喻帮助患者理解
4. 提供积极且现实的预后信息
5. 强调治疗的可能性和希望
6. 包含患者应该了解的关键信息

风格要求：
- 温暖、同情、鼓励
- 清晰、结构化、易于阅读
- 包含emoji图标帮助视觉理解
- 按照优先级组织信息

输出格式：
使用Markdown格式，包括标题、要点、强调等。"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        """
        初始化科普智能体
        
        Args:
            api_key: Claude API密钥（默认从环境变量获取）
            model: 使用的Claude模型版本
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def generate_genetic_education(self, genetic_features: Dict) -> str:
        """
        生成基因科普文本
        
        Args:
            genetic_features: 基因特征字典，包含：
                - driver_genes: 驱动基因列表
                - tumor_suppressor_genes: 抑癌基因列表
                - actionable_mutations: 可靶向突变列表
                - risk_profile: 风险等级
        
        Returns:
            str: 患者友好的基因科普文本
        """
        
        user_prompt = f"""请根据以下基因检测结果，生成一份患者友好的科普说明：

基因检测结果：
{json.dumps(genetic_features, ensure_ascii=False, indent=2)}

请生成一份科普文本，包含：
1. 发现的关键基因突变及其含义
2. 这些突变对治疗有什么影响
3. 对预后的含义
4. 是否有可靶向的突变
5. 后续建议

格式要求：
- 使用## 作为主标题
- 使用### 作为副标题
- 包含相关emoji
- 控制在800-1200字"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.content[0].text
    
    def generate_pathology_education(self, pathology_features: Dict) -> str:
        """
        生成病理科普文本
        """
        
        user_prompt = f"""请根据以下病理检查结果，生成一份患者友好的科普说明：

病理检查结果：
{json.dumps(pathology_features, ensure_ascii=False, indent=2)}

请生成一份科普文本，包含：
1. 肿瘤的病理类型（如腺癌）的含义
2. 分化程度的含义
3. 特殊标志物（如claudin18, MSI-H）的含义及治疗意义
4. 病理检查的临床意义
5. 对预后的影响

格式要求：
- 使用## 作为主标题
- 使用### 作为副标题
- 包含相关emoji
- 控制在600-1000字"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.content[0].text
    
    def generate_treatment_education(self, treatment_history: List[Dict]) -> str:
        """
        生成治疗方案科普文本
        """
        
        user_prompt = f"""请根据以下治疗历史，生成一份患者友好的科普说明：

治疗历史：
{json.dumps(treatment_history, ensure_ascii=False, indent=2)}

请生成一份科普文本，包含：
1. 每种治疗方式的含义（化疗、手术、放疗、靶向、免疫等）
2. 为什么需要这些治疗
3. 治疗可能带来的效果和副反应
4. 患者在治疗期间应该注意什么

格式要求：
- 使用## 作为主标题
- 使用### 作为副标题
- 包含相关emoji
- 控制在700-1100字"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.content[0].text
    
    def generate_prognosis_education(
        self,
        risk_profile: str,
        genetic_features: Dict,
        pathology_features: Dict,
        treatment_response: Optional[str] = None
    ) -> str:
        """
        生成预后科普文本
        """
        
        context = {
            'risk_profile': risk_profile,
            'genetic_features': genetic_features,
            'pathology_features': pathology_features,
            'treatment_response': treatment_response
        }
        
        user_prompt = f"""请根据以下病情信息，生成一份患者友好的预后科普说明：

病情信息：
{json.dumps(context, ensure_ascii=False, indent=2)}

请生成一份科普文本，包含：
1. 预后的定义和含义
2. 影响预后的因素
3. 该患者的预后评估
4. 改善预后的措施
5. 鼓励和希望的信息

特别注意：
- 要平衡现实和希望
- 强调医学的进步和新的治疗选项
- 强调患者的积极作用

格式要求：
- 使用## 作为主标题
- 使用### 作为副标题
- 包含相关emoji
- 控制在700-1100字"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.content[0].text
    
    def generate_clinical_trial_education(
        self,
        matched_trials: List[Dict],
        patient_context: Optional[Dict] = None
    ) -> str:
        """
        生成临床试验科普文本
        """
        
        user_prompt = f"""请根据以下临床试验信息，生成一份患者友好的科普说明：

为患者推荐的临床试验：
{json.dumps(matched_trials[:5], ensure_ascii=False, indent=2)}

患者背景信息：
{json.dumps(patient_context or {}, ensure_ascii=False, indent=2)}

请生成一份科普文本，包含：
1. 什么是临床试验
2. 参加临床试验的优势和风险
3. 为什么这些试验对该患者合适
4. 如何评估是否参加试验
5. 获取更多信息的途径

格式要求：
- 使用## 作为主标题
- 使用### 作为副标题
- 包含相关emoji
- 平衡性：既要说明优势，也要说明需要考虑的因素
- 控制在800-1200字"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1800,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.content[0].text
    
    def generate_patient_self_care(
        self,
        risk_profile: str,
        complications: Optional[List[Dict]] = None
    ) -> str:
        """
        生成患者自我管理建议
        """
        
        context = {
            'risk_profile': risk_profile,
            'complications': complications or []
        }
        
        user_prompt = f"""请根据以下病情信息，生成一份患者自我管理建议：

病情信息：
{json.dumps(context, ensure_ascii=False, indent=2)}

请生成一份建议，包含：
1. 医学方面：定期复诊、检查、监测
2. 营养管理：饮食建议
3. 生活方式：运动、休息、避免
4. 心理健康：情绪管理、支持资源
5. 防并发症：具体预防措施

格式要求：
- 使用## 作为主标题
- 使用### 作为副标题
- 包含相关emoji
- 具体、可操作、鼓励
- 控制在600-1000字"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.content[0].text
    
    def generate_comprehensive_education_report(
        self,
        genetic_features: Dict,
        pathology_features: Dict,
        treatment_history: List[Dict],
        matched_trials: List[Dict],
        risk_profile: str,
        complications: Optional[List[Dict]] = None
    ) -> str:
        """
        生成完整的科普教育报告
        
        这是主要的流程：
        1. 基因科普
        2. 病理科普  
        3. 治疗科普
        4. 预后科普
        5. 临床试验科普
        6. 自我管理建议
        """
        
        report_parts = []
        
        # 标题和前言
        report_parts.append("=" * 60)
        report_parts.append("患者科普版病情报告")
        report_parts.append("=" * 60)
        report_parts.append("")
        report_parts.append("### 📖 如何阅读这份报告")
        report_parts.append("这份报告用简单易懂的语言解释您的医学检查结果。")
        report_parts.append("如果有任何不明白的地方，请咨询您的医生。")
        report_parts.append("")
        
        # 第1步：基因科普
        report_parts.append("\n## 第一部分：基因检测结果\n")
        genetic_content = self.generate_genetic_education(genetic_features)
        report_parts.append(genetic_content)
        
        # 第2步：病理科普
        report_parts.append("\n\n## 第二部分：病理检查结果\n")
        pathology_content = self.generate_pathology_education(pathology_features)
        report_parts.append(pathology_content)
        
        # 第3步：治疗科普
        report_parts.append("\n\n## 第三部分：治疗方案\n")
        treatment_content = self.generate_treatment_education(treatment_history)
        report_parts.append(treatment_content)
        
        # 第4步：预后科普
        report_parts.append("\n\n## 第四部分：预后评估\n")
        prognosis_content = self.generate_prognosis_education(
            risk_profile=risk_profile,
            genetic_features=genetic_features,
            pathology_features=pathology_features
        )
        report_parts.append(prognosis_content)
        
        # 第5步：临床试验科普
        report_parts.append("\n\n## 第五部分：临床试验机会\n")
        trial_content = self.generate_clinical_trial_education(
            matched_trials=matched_trials,
            patient_context={
                'risk_profile': risk_profile,
                'mutations': genetic_features.get('driver_genes', [])
            }
        )
        report_parts.append(trial_content)
        
        # 第6步：自我管理建议
        report_parts.append("\n\n## 第六部分：自我管理建议\n")
        self_care_content = self.generate_patient_self_care(
            risk_profile=risk_profile,
            complications=complications
        )
        report_parts.append(self_care_content)
        
        # 结尾
        report_parts.append("\n\n" + "=" * 60)
        report_parts.append("报告完毕。如有疑问，请咨询您的医疗团队。")
        report_parts.append("=" * 60)
        
        return "\n".join(report_parts)
