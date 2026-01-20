"""文件分类枚举

独立模块，避免循环导入
"""

from enum import Enum


class FileCategory(Enum):
    """文件分类枚举"""
    
    # 医疗诊疗
    MEDICAL_RECORDS = "医疗诊疗/病历"
    IMAGING = "医疗诊疗/影像"
    LAB_REPORTS = "医疗诊疗/检查检测报告"
    PRESCRIPTIONS = "医疗诊疗/处方用药"
    
    # 营养管理
    NUTRITION = "营养管理"
    
    # 心理支持
    PSYCHOLOGY = "心理支持"
    
    # 并发症管理
    COMPLICATIONS = "并发症管理"
    
    # 待确认
    UNCONFIRMED = "待确认"
