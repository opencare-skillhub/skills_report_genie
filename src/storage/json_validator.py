"""JSON数据验证器

根据 JSON_STORAGE_GUIDE.md 实现
验证患者病历的JSON结构完整性
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re


class JSONValidator:
    """基础JSON验证器"""
    
    @staticmethod
    def validate_type(data: Any, expected_type: type) -> bool:
        """验证数据类型
        
        Args:
            data: 待验证数据
            expected_type: 期望类型
            
        Returns:
            bool: 类型是否匹配
        """
        return isinstance(data, expected_type)
    
    @staticmethod
    def validate_required_fields(obj: Dict, required_fields: List[str]) -> Tuple[bool, List[str]]:
        """验证必需字段
        
        Args:
            obj: 对象字典
            required_fields: 必需字段列表
            
        Returns:
            Tuple: (是否通过, 缺失字段列表)
        """
        missing = [f for f in required_fields if f not in obj]
        return len(missing) == 0, missing
    
    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """验证日期格式 (YYYY-MM-DD)
        
        Args:
            date_str: 日期字符串
            
        Returns:
            bool: 日期格式是否正确
        """
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_hash_format(patient_id: str) -> bool:
        """验证患者ID hash格式
        
        Args:
            patient_id: 患者ID
            
        Returns:
            bool: hash格式是否正确
        """
        # hash应该是64个十六进制字符（SHA256）
        return bool(re.match(r'^[a-f0-9]{64}$', patient_id.lower()))


class PatientDataValidator:
    """患者数据验证器
    
    根据 JSON_STORAGE_GUIDE.md 的数据模型进行验证
    """
    
    def validate_patient_master(self, data: Dict) -> Tuple[bool, List[str]]:
        """验证 patient_master.json
        
        Args:
            data: patient_master.json 数据
            
        Returns:
            Tuple: (通过验证, 错误列表)
        """
        errors = []
        
        # 验证必需字段
        required_fields = ['patient_id', 'basic_info', 'disease_timeline']
        valid, missing = JSONValidator.validate_required_fields(data, required_fields)
        if not valid:
            errors.extend([f"缺失必需字段: {f}" for f in missing])
        
        # 验证 patient_id
        if 'patient_id' in data and not JSONValidator.validate_hash_format(data['patient_id']):
            errors.append("患者ID不是有效的hash格式")
        
        # 验证 basic_info 结构
        if 'basic_info' in data:
            basic_info = data['basic_info']
            if not isinstance(basic_info, dict):
                errors.append("basic_info 必须是字典")
            else:
                required_basic = ['name_hash', 'gender', 'age', 'diagnosis']
                valid, missing = JSONValidator.validate_required_fields(basic_info, required_basic)
                if not valid:
                    errors.extend([f"basic_info缺失字段: {f}" for f in missing])
        
        # 验证 disease_timeline 结构
        if 'disease_timeline' in data:
            timeline = data['disease_timeline']
            if not isinstance(timeline, list):
                errors.append("disease_timeline 必须是数组")
            else:
                for i, event in enumerate(timeline):
                    if not isinstance(event, dict):
                        errors.append(f"disease_timeline[{i}] 必须是字典")
                    else:
                        if 'date' in event and not JSONValidator.validate_date_format(event['date']):
                            errors.append(f"disease_timeline[{i}].date 日期格式错误")
        
        return len(errors) == 0, errors
    
    def validate_genetic_report(self, data: Dict) -> Tuple[bool, List[str]]:
        """验证 genetic_report.json
        
        Args:
            data: genetic_report.json 数据
            
        Returns:
            Tuple: (通过验证, 错误列表)
        """
        errors = []
        
        # 验证必需字段
        required_fields = ['test_date', 'test_type', 'mutations']
        valid, missing = JSONValidator.validate_required_fields(data, required_fields)
        if not valid:
            errors.extend([f"缺失必需字段: {f}" for f in missing])
        
        # 验证test_date格式
        if 'test_date' in data and not JSONValidator.validate_date_format(data['test_date']):
            errors.append("test_date 日期格式错误 (应为YYYY-MM-DD)")
        
        # 验证test_type
        valid_types = ['NGS', 'PCR', 'WES', 'WGS', 'Panel']
        if 'test_type' in data and data['test_type'] not in valid_types:
            errors.append(f"test_type 无效，应为: {','.join(valid_types)}")
        
        # 验证mutations结构
        if 'mutations' in data:
            mutations = data['mutations']
            if not isinstance(mutations, list):
                errors.append("mutations 必须是数组")
            else:
                for i, mutation in enumerate(mutations):
                    if not isinstance(mutation, dict):
                        errors.append(f"mutations[{i}] 必须是字典")
                    else:
                        mutation_required = ['gene', 'mutation', 'classification']
                        valid, missing = JSONValidator.validate_required_fields(mutation, mutation_required)
                        if not valid:
                            errors.extend([f"mutations[{i}] 缺失字段: {f}" for f in missing])
        
        return len(errors) == 0, errors
    
    def validate_pathology_report(self, data: Dict) -> Tuple[bool, List[str]]:
        """验证 pathology_report.json
        
        Args:
            data: pathology_report.json 数据
            
        Returns:
            Tuple: (通过验证, 错误列表)
        """
        errors = []
        
        # 验证必需字段
        required_fields = ['test_date', 'primary_pathology', 'differentiation_grade']
        valid, missing = JSONValidator.validate_required_fields(data, required_fields)
        if not valid:
            errors.extend([f"缺失必需字段: {f}" for f in missing])
        
        # 验证test_date格式
        if 'test_date' in data and not JSONValidator.validate_date_format(data['test_date']):
            errors.append("test_date 日期格式错误 (应为YYYY-MM-DD)")
        
        # 验证分化程度
        valid_grades = ['I', 'II', 'III']
        if 'differentiation_grade' in data and data['differentiation_grade'] not in valid_grades:
            errors.append(f"differentiation_grade 无效，应为: {','.join(valid_grades)}")
        
        # 验证special_markers如果存在
        if 'special_markers' in data:
            markers = data['special_markers']
            if not isinstance(markers, dict):
                errors.append("special_markers 必须是字典")
        
        return len(errors) == 0, errors
    
    def validate_tumor_markers(self, data: Dict) -> Tuple[bool, List[str]]:
        """验证 tumor_markers.json
        
        Args:
            data: tumor_markers.json 数据
            
        Returns:
            Tuple: (通过验证, 错误列表)
        """
        errors = []
        
        marker_types = ['CA19-9', 'CA50', 'CA125', 'CA72-4', 'CEA']
        
        for marker_type in marker_types:
            if marker_type not in data:
                continue
            
            marker_data = data[marker_type]
            if not isinstance(marker_data, list):
                errors.append(f"{marker_type} 必须是数组")
                continue
            
            for i, record in enumerate(marker_data):
                if not isinstance(record, dict):
                    errors.append(f"{marker_type}[{i}] 必须是字典")
                    continue
                
                # 验证必需字段
                required = ['date', 'value']
                valid, missing = JSONValidator.validate_required_fields(record, required)
                if not valid:
                    errors.extend([f"{marker_type}[{i}] 缺失字段: {f}" for f in missing])
                
                # 验证date格式
                if 'date' in record and not JSONValidator.validate_date_format(record['date']):
                    errors.append(f"{marker_type}[{i}].date 日期格式错误")
                
                # 验证value是数值
                if 'value' in record and not isinstance(record['value'], (int, float)):
                    errors.append(f"{marker_type}[{i}].value 必须是数值")
        
        return len(errors) == 0, errors
