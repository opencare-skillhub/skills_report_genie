"""JSON验证器测试"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.storage.json_validator import JSONValidator, PatientDataValidator


class TestJSONValidator:
    """基础JSON验证器测试"""
    
    def test_validate_type(self):
        """测试类型验证"""
        assert JSONValidator.validate_type("hello", str)
        assert JSONValidator.validate_type(123, int)
        assert JSONValidator.validate_type({}, dict)
        assert not JSONValidator.validate_type("hello", int)
        print("✓ 类型验证成功")
    
    def test_validate_required_fields(self):
        """测试必需字段验证"""
        obj = {"name": "John", "age": 30}
        
        # 所有字段都存在
        valid, missing = JSONValidator.validate_required_fields(obj, ["name", "age"])
        assert valid
        assert len(missing) == 0
        
        # 缺少字段
        valid, missing = JSONValidator.validate_required_fields(obj, ["name", "age", "email"])
        assert not valid
        assert "email" in missing
        
        print("✓ 必需字段验证成功")
    
    def test_validate_date_format(self):
        """测试日期格式验证"""
        assert JSONValidator.validate_date_format("2024-01-15")
        assert JSONValidator.validate_date_format("2024-12-31")
        assert not JSONValidator.validate_date_format("01-15-2024")
        assert not JSONValidator.validate_date_format("2024/01/15")
        assert not JSONValidator.validate_date_format("invalid")
        print("✓ 日期格式验证成功")
    
    def test_validate_hash_format(self):
        """测试hash格式验证"""
        # 64个十六进制字符
        valid_hash = "a" * 64
        assert JSONValidator.validate_hash_format(valid_hash)
        
        # 62个字符 (太短)
        assert not JSONValidator.validate_hash_format("a" * 62)
        
        # 包含非十六进制字符
        assert not JSONValidator.validate_hash_format("g" * 64)
        
        print("✓ Hash格式验证成功")


class TestPatientDataValidator:
    """患者数据验证器测试"""
    
    def test_validate_patient_master_valid(self):
        """测试有效的patient_master.json"""
        valid_hash = "a" * 64
        data = {
            "patient_id": valid_hash,
            "basic_info": {
                "name_hash": "hash123",
                "gender": "M",
                "age": 65,
                "diagnosis": "pancreatic cancer"
            },
            "disease_timeline": [
                {
                    "date": "2024-01-15",
                    "event_type": "diagnosis",
                    "description": "确诊胰腺癌"
                }
            ]
        }
        
        validator = PatientDataValidator()
        valid, errors = validator.validate_patient_master(data)
        
        assert valid, f"验证失败: {errors}"
        print("✓ 有效的patient_master.json验证通过")
    
    def test_validate_patient_master_missing_fields(self):
        """测试缺失必需字段"""
        data = {
            "patient_id": "a" * 64
            # 缺少 basic_info 和 disease_timeline
        }
        
        validator = PatientDataValidator()
        valid, errors = validator.validate_patient_master(data)
        
        assert not valid
        assert len(errors) > 0
        print(f"✓ 缺失字段检测成功: {errors[0]}")
    
    def test_validate_genetic_report_valid(self):
        """测试有效的genetic_report.json"""
        data = {
            "test_date": "2024-01-15",
            "test_type": "NGS",
            "mutations": [
                {
                    "gene": "KRAS",
                    "mutation": "G12D",
                    "classification": "驱动基因",
                    "allele_frequency": 45.2
                }
            ]
        }
        
        validator = PatientDataValidator()
        valid, errors = validator.validate_genetic_report(data)
        
        assert valid, f"验证失败: {errors}"
        print("✓ 有效的genetic_report.json验证通过")
    
    def test_validate_genetic_report_invalid_date(self):
        """测试无效的日期格式"""
        data = {
            "test_date": "01/15/2024",  # 错误格式
            "test_type": "NGS",
            "mutations": []
        }
        
        validator = PatientDataValidator()
        valid, errors = validator.validate_genetic_report(data)
        
        assert not valid
        assert any("日期格式" in e for e in errors)
        print(f"✓ 日期格式错误检测成功: {[e for e in errors if '日期' in e][0]}")
    
    def test_validate_pathology_report_valid(self):
        """测试有效的pathology_report.json"""
        data = {
            "test_date": "2024-01-15",
            "primary_pathology": "pancreatic_ductal_adenocarcinoma",
            "differentiation_grade": "II",
            "special_markers": {
                "CA19-9": "positive",
                "claudin18": "positive"
            }
        }
        
        validator = PatientDataValidator()
        valid, errors = validator.validate_pathology_report(data)
        
        assert valid, f"验证失败: {errors}"
        print("✓ 有效的pathology_report.json验证通过")
    
    def test_validate_pathology_report_invalid_grade(self):
        """测试无效的分化程度"""
        data = {
            "test_date": "2024-01-15",
            "primary_pathology": "adenocarcinoma",
            "differentiation_grade": "IV"  # 无效值
        }
        
        validator = PatientDataValidator()
        valid, errors = validator.validate_pathology_report(data)
        
        assert not valid
        assert any("differentiation_grade" in e for e in errors)
        print(f"✓ 无效的分化程度检测成功")
    
    def test_validate_tumor_markers_valid(self):
        """测试有效的tumor_markers.json"""
        data = {
            "CA19-9": [
                {"date": "2024-01-15", "value": 245.5, "unit": "U/mL"},
                {"date": "2024-02-15", "value": 195.3, "unit": "U/mL"}
            ],
            "CA50": [
                {"date": "2024-01-15", "value": 128.0, "unit": "U/mL"}
            ]
        }
        
        validator = PatientDataValidator()
        valid, errors = validator.validate_tumor_markers(data)
        
        assert valid, f"验证失败: {errors}"
        print("✓ 有效的tumor_markers.json验证通过")
    
    def test_validate_tumor_markers_invalid_value(self):
        """测试无效的值类型"""
        data = {
            "CA19-9": [
                {"date": "2024-01-15", "value": "高"}  # 应该是数值
            ]
        }
        
        validator = PatientDataValidator()
        valid, errors = validator.validate_tumor_markers(data)
        
        assert not valid
        assert any("必须是数值" in e for e in errors)
        print(f"✓ 无效值类型检测成功")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
