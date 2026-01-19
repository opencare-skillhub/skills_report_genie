"""
患者数据脱敏模块

脱敏规则：
- 删除真实姓名 → [患者]
- 删除身份证号 → [已脱敏]
- 删除电话 → [已脱敏]
- 删除详细地址 → [已脱敏]
- 保留所有医学信息（基因、病理、治疗等）
"""

from typing import Dict, Any, List
import re


class DataSanitizer:
    """患者数据脱敏"""
    
    # 需要脱敏的字段
    SENSITIVE_FIELDS = [
        'patient_name',
        'real_name',
        'id_number',
        'id_card',
        'phone',
        'telephone',
        'mobile',
        'address',
        'detailed_address',
        'hospital_detailed',
        'doctor_name',
        'doctor_phone',
        'contact_person',
        'contact_phone'
    ]
    
    # 脱敏规则：{字段名: 替换值}
    SANITIZE_MAP = {
        'patient_name': '[患者]',
        'real_name': '[患者]',
        'id_number': '[已脱敏]',
        'id_card': '[已脱敏]',
        'phone': '[已脱敏]',
        'telephone': '[已脱敏]',
        'mobile': '[已脱敏]',
        'address': '[已脱敏]',
        'detailed_address': '[已脱敏]',
        'hospital_detailed': '[医院]',
        'doctor_name': '[医生]',
        'doctor_phone': '[已脱敏]',
        'contact_person': '[已脱敏]',
        'contact_phone': '[已脱敏]'
    }
    
    def __init__(self):
        """初始化脱敏器"""
        self.phone_pattern = re.compile(r'1[3-9]\d{9}')  # 中国手机号
        self.id_pattern = re.compile(r'\d{17}[\dXx]')  # 身份证号
    
    def sanitize_report(self, report: Dict) -> Dict:
        """
        脱敏报告数据
        
        Args:
            report: 原始报告字典
            
        Returns:
            dict: 脱敏后的报告
        """
        sanitized = self._deep_copy(report)
        
        # 第一步：按字段脱敏
        for field, replacement in self.SANITIZE_MAP.items():
            if field in sanitized:
                sanitized[field] = replacement
        
        # 第二步：递归遍历嵌套字典和列表
        self._sanitize_nested(sanitized)
        
        # 第三步：清除完全敏感的字段
        fields_to_remove = ['real_name']
        for field in fields_to_remove:
            if field in sanitized:
                del sanitized[field]
        
        # 第四步：处理日期（只保留年月）
        if 'diagnosis_date' in sanitized:
            sanitized['diagnosis_date'] = self._sanitize_date(sanitized['diagnosis_date'])
        
        if 'birth_date' in sanitized:
            sanitized['birth_date'] = self._sanitize_date(sanitized['birth_date'])
        
        return sanitized
    
    def _deep_copy(self, obj: Any) -> Any:
        """深拷贝对象"""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj
    
    def _sanitize_nested(self, obj: Any) -> None:
        """
        递归脱敏嵌套的字典和列表
        
        Args:
            obj: 待脱敏的对象（会原地修改）
        """
        if isinstance(obj, dict):
            for key, value in list(obj.items()):
                if key in self.SANITIZE_MAP:
                    obj[key] = self.SANITIZE_MAP[key]
                elif isinstance(value, (dict, list)):
                    self._sanitize_nested(value)
                elif isinstance(value, str):
                    # 检测并脱敏文本中的敏感信息
                    obj[key] = self._sanitize_text(value)
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, (dict, list)):
                    self._sanitize_nested(item)
                elif isinstance(item, str):
                    obj[i] = self._sanitize_text(item)
    
    def _sanitize_text(self, text: str) -> str:
        """
        脱敏文本中的敏感信息
        
        Args:
            text: 原始文本
            
        Returns:
            str: 脱敏后的文本
        """
        if not isinstance(text, str):
            return text
        
        # 脱敏手机号
        text = self.phone_pattern.sub('[电话已脱敏]', text)
        
        # 脱敏身份证号
        text = self.id_pattern.sub('[身份证已脱敏]', text)
        
        # 脱敏常见的姓名格式（中文2-4字）
        text = re.sub(r'(?<![a-zA-Z0-9])([一-龥]{2,4})(?![a-zA-Z0-9])', '[患者]', text)
        
        return text
    
    def _sanitize_date(self, date_str: str) -> str:
        """
        脱敏日期，只保留年月
        
        Args:
            date_str: 原始日期字符串
            
        Returns:
            str: 脱敏后的日期（YYYY-MM格式）
        """
        if not date_str:
            return date_str
        
        # 提取年月部分
        match = re.search(r'(\d{4})-(\d{2})', date_str)
        if match:
            return f"{match.group(1)}-{match.group(2)}"
        
        return date_str
    
    def sanitize_string(self, text: str) -> str:
        """
        脱敏单个字符串
        
        Args:
            text: 原始字符串
            
        Returns:
            str: 脱敏后的字符串
        """
        return self._sanitize_text(text)
    
    def get_sanitization_report(self, original: Dict, sanitized: Dict) -> Dict:
        """
        生成脱敏报告
        
        Args:
            original: 原始数据
            sanitized: 脱敏后的数据
            
        Returns:
            dict: 脱敏报告（显示哪些字段被修改）
        """
        changes = {}
        
        for key in self.SENSITIVE_FIELDS:
            if key in original and key in sanitized:
                if original[key] != sanitized[key]:
                    changes[key] = {
                        'original_type': type(original[key]).__name__,
                        'sanitized_value': sanitized[key],
                        'status': 'sanitized'
                    }
        
        return {
            'total_sanitized_fields': len(changes),
            'changes': changes,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }


# 使用示例
if __name__ == '__main__':
    sanitizer = DataSanitizer()
    
    # 示例数据
    sample_report = {
        'patient_name': '张三',
        'real_name': '张三',
        'id_number': '110101199003151234',
        'phone': '13812345678',
        'address': '北京市朝阳区某某街道',
        'diagnosis': '胰腺癌',
        'stage': 'IIIB期',
        'doctor_name': '李医生',
        'medical_records': {
            'ca_markers': [
                {'name': 'CA19-9', 'value': 245.5, 'unit': 'U/mL'}
            ]
        }
    }
    
    # 脱敏
    sanitized = sanitizer.sanitize_report(sample_report)
    print("脱敏后的报告:")
    print(sanitized)
    
    # 脱敏报告
    report = sanitizer.get_sanitization_report(sample_report, sanitized)
    print("\n脱敏统计:")
    print(report)
