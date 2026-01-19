"""
Phase 4: 医学可视化设计智能体
职责：调用Claude API，设计患者友好的可视化内容和图表
"""

import json
from typing import Dict, List, Optional
import anthropic


class VisualizationAgent:
    """
    医学可视化设计智能体
    
    核心流程：
    1. 接收结构化的病情数据
    2. 使用系统提示词定义角色（医学信息设计师）
    3. 调用Claude API设计可视化内容
    4. 返回格式化的可视化元素和图表代码
    """
    
    # 系统提示词 - 角色定义
    SYSTEM_PROMPT = """你是一位资深的医学信息设计师，专长于将复杂的医学数据转化为患者易理解的可视化内容。

你的目标是：
1. 设计清晰的信息结构，突出关键信息
2. 使用视觉元素（图标、颜色、图表）帮助理解
3. 创建易于阅读的信息层级
4. 提供快速要点总结
5. 使用对比和对比来突出重要信息

设计原则：
- 简洁：避免信息过载
- 清晰：一目了然
- 友好：使用患者能理解的语言和图标
- 可操作：帮助患者采取行动

输出格式：
使用Markdown格式，包含：
- 图标和emoji
- 结构化的表格
- 重点强调（**粗体**）
- 条理化列表
- ASCII图表（如需要）"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        """
        初始化可视化智能体
        
        Args:
            api_key: Claude API密钥
            model: 使用的Claude模型版本
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def design_risk_profile_visualization(self, risk_profile: str, explanation: str = "") -> str:
        """
        设计风险等级可视化
        """
        
        user_prompt = f"""请为以下风险等级设计一份可视化呈现：

风险等级：{risk_profile}
说明：{explanation}

请提供：
1. 风险等级的视觉化表示（使用emoji和符号）
2. 风险指示条（显示严重程度）
3. 简明的文字说明
4. 患者应该了解的关键信息

格式要求：
- 使用emoji图标
- 包含风险指示条
- 清晰的视觉层级
- 200-300字"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.content[0].text
    
    def design_genetic_features_table(self, genetic_features: Dict) -> str:
        """
        设计基因特征表格可视化
        """
        
        user_prompt = f"""请为以下基因特征设计一份清晰的表格可视化：

基因特征：
{json.dumps(genetic_features, ensure_ascii=False, indent=2)}

请设计：
1. 一份结构化的基因特征表格，包括：
   - 基因名称
   - 突变类型
   - 临床意义（高/中/低优先级）
   - 治疗含义
2. 使用icon标记可靶向突变
3. 用颜色差异（通过emoji）区分优先级

格式要求：
- 使用Markdown表格
- 包含emoji图标
- 清晰的列标题
- 突出可靶向突变
- 400-600字"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.content[0].text
    
    def design_treatment_timeline(self, treatment_history: List[Dict]) -> str:
        """
        设计治疗时间线可视化
        """
        
        user_prompt = f"""请为以下治疗历史设计一份时间线可视化：

治疗历史：
{json.dumps(treatment_history, ensure_ascii=False, indent=2)}

请设计：
1. 清晰的治疗时间线，显示：
   - 每个治疗阶段
   - 时间点
   - 治疗反应
2. 使用不同的图标表示不同的治疗类型
3. 使用颜色（通过emoji）表示治疗反应

格式要求：
- 使用ASCII时间线或Markdown列表
- 不同治疗类型使用不同emoji（💊化疗, 🏥手术, ☢️放疗, 🎯靶向）
- 显示时间间隔
- 突出治疗反应
- 400-600字"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.content[0].text
    
    def design_marker_trend_narrative(self, marker_data: Dict) -> str:
        """
        设计肿瘤标志物趋势的叙述化可视化
        
        （注：实际的图表由quickchart-mcp生成，这里生成叙述和解释）
        """
        
        user_prompt = f"""请为以下肿瘤标志物数据设计一份可视化叙述：

标志物数据：
{json.dumps(marker_data, ensure_ascii=False, indent=2)}

请提供：
1. 趋势的文字描述（上升/下降/稳定）
2. 关键数据点的突出（初始值、当前值、变化幅度）
3. 与参考值的对比说明
4. 临床意义解释
5. 患者需要关注的内容

格式要求：
- 使用emoji表示趋势（📈上升, 📉下降, ➡️稳定）
- 突出关键数值
- 清晰的解释
- 300-500字"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=800,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.content[0].text
    
    def design_patient_summary_card(self, patient_data: Dict) -> str:
        """
        设计患者速览卡片
        """
        
        user_prompt = f"""请为以下患者设计一份1页的速览卡片：

患者信息：
{json.dumps(patient_data, ensure_ascii=False, indent=2)}

请设计一个包含以下内容的卡片：
1. 基本诊断信息
2. TNM分期
3. 关键基因突变（最多3个）
4. 风险等级
5. 当前治疗状态
6. 下一步建议

格式要求：
- 信息密度高但易于阅读
- 使用分隔符和emoji
- 包含关键icon
- 清晰的优先级
- 控制在400-600字"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.content[0].text
    
    def design_consultation_checklist(
        self,
        genetic_features: Dict,
        pathology_features: Dict,
        risk_profile: str
    ) -> str:
        """
        设计医生问诊清单
        """
        
        context = {
            'genetic_features': genetic_features,
            'pathology_features': pathology_features,
            'risk_profile': risk_profile
        }
        
        user_prompt = f"""请为该患者设计一份医生问诊清单：

患者特征：
{json.dumps(context, ensure_ascii=False, indent=2)}

请设计：
1. 按优先级组织问题（高/中/低）
2. 每个问题包含：
   - 问题本身
   - 为什么要问（背景）
   - 重点关注的内容
3. 针对该患者的具体情况
4. 包含基因、病理、治疗、预后、临床试验等方面

格式要求：
- 使用复选框格式：[ ] 问题
- 按优先级分组：### 高优先级, ### 中优先级, ### 低优先级
- 包含emoji图标
- 控制在600-900字"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.content[0].text
    
    def design_complication_risk_table(self, complications: List[Dict]) -> str:
        """
        设计并发症风险表格
        """
        
        user_prompt = f"""请为以下并发症风险设计一份清晰的表格：

并发症列表：
{json.dumps(complications, ensure_ascii=False, indent=2)}

请设计：
1. 一份并发症风险表格，包括：
   - 并发症名称
   - 风险等级（高/中/低）
   - 症状表现
   - 监测方法
   - 预防措施
2. 使用emoji表示风险等级（🔴高, 🟡中, 🟢低）
3. 突出危险症状

格式要求：
- 使用Markdown表格
- 包含清晰的图标
- 每行包含可操作的信息
- 控制在500-800字"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1200,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.content[0].text
    
    def generate_comprehensive_visualization_report(
        self,
        genetic_features: Dict,
        pathology_features: Dict,
        treatment_history: List[Dict],
        matched_trials: List[Dict],
        risk_profile: str,
        patient_data: Dict,
        complications: Optional[List[Dict]] = None
    ) -> str:
        """
        生成完整的可视化报告
        """
        
        report_parts = []
        
        # 标题
        report_parts.append("=" * 60)
        report_parts.append("医学信息可视化报告")
        report_parts.append("=" * 60)
        report_parts.append("")
        
        # 第1步：患者速览卡
        report_parts.append("## 患者病情速览卡\n")
        summary_card = self.design_patient_summary_card(patient_data)
        report_parts.append(summary_card)
        
        # 第2步：风险等级可视化
        report_parts.append("\n## 风险等级评估\n")
        risk_vis = self.design_risk_profile_visualization(risk_profile)
        report_parts.append(risk_vis)
        
        # 第3步：基因特征表格
        report_parts.append("\n## 基因特征矩阵\n")
        gene_table = self.design_genetic_features_table(genetic_features)
        report_parts.append(gene_table)
        
        # 第4步：治疗时间线
        report_parts.append("\n## 治疗时间线\n")
        timeline = self.design_treatment_timeline(treatment_history)
        report_parts.append(timeline)
        
        # 第5步：并发症风险
        if complications:
            report_parts.append("\n## 并发症风险评估\n")
            complication_table = self.design_complication_risk_table(complications)
            report_parts.append(complication_table)
        
        # 第6步：问诊清单
        report_parts.append("\n## 医生问诊清单\n")
        checklist = self.design_consultation_checklist(
            genetic_features,
            pathology_features,
            risk_profile
        )
        report_parts.append(checklist)
        
        # 结尾
        report_parts.append("\n" + "=" * 60)
        report_parts.append("可视化报告完毕。")
        report_parts.append("=" * 60)
        
        return "\n".join(report_parts)
