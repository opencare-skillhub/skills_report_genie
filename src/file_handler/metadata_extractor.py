"""元数据提取模块

用于从文本内容中提取关键元数据（如日期、患者姓名等）
"""

import re
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MetadataExtractor:
    """元数据提取器"""
    
    @staticmethod
    def extract_date(text: str) -> Optional[str]:
        """
        从文本中提取日期 (YYYY-MM-DD格式)
        
        Args:
            text: 提取的文本内容
            
        Returns:
            str: 格式化的日期字符串，如果未找到则返回None
        """
        # 常见的日期格式正则
        date_patterns = [
            # 2023-06-27, 2023.06.27, 2023/06/27
            r'(\d{4})[./-](\d{1,2})[./-](\d{1,2})',
            # 23.03.31 (两位年份)
            r'(?<!\d)(\d{2})[./-](\d{1,2})[./-](\d{1,2})',
            # 2023年06月27日
            r'(\d{4})年(\d{1,2})月(\d{1,2})日'
        ]
        
        for pattern in date_patterns:
            matches = re.search(pattern, text)
            if matches:
                try:
                    year, month, day = matches.groups()
                    
                    # 处理两位年份
                    if len(year) == 2:
                        year = "20" + year
                        
                    # 验证日期有效性
                    dt = datetime(int(year), int(month), int(day))
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
                    
        return None

    @staticmethod
    def extract_patient_name(text: str) -> Optional[str]:
        """
        提取患者姓名（简单示例）
        """
        keywords = ["姓名", "患者"]
        for kw in keywords:
            pattern = f"{kw}[：:]\s*([\u4e00-\u9fa5]{{2,4}})"
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None
