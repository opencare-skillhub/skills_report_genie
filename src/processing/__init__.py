"""处理流程模块 (v2.0)

核心流程：扫描 → 解析 → 重命名 → 汇总JSON → 分类移动
"""

from src.processing.file_processor import FileProcessor, ParseResult
from src.processing.file_renamer import FileRenamer
from src.processing.json_aggregator import JsonAggregator
from src.processing.file_organizer import FileOrganizer
from src.processing.process_coordinator import ProcessCoordinator

__all__ = [
    'FileProcessor',
    'ParseResult',
    'FileRenamer',
    'JsonAggregator',
    'FileOrganizer',
    'ProcessCoordinator',
]
