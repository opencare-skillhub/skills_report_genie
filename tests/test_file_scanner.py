"""文件扫描器测试"""

import pytest
import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.file_handler.scanner import FileScanner, FileCategory


class TestFileScanner:
    """文件扫描器测试"""
    
    @pytest.fixture
    def test_dir(self):
        """创建测试目录结构"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试文件
            test_files = {
                '病历_20240115.txt': '门诊病历内容',
                'CT扫描报告.pdf': 'CT影像报告',
                '血液检查_CA19-9.xlsx': '肿瘤标志物',
                '化疗方案.docx': '吉西他滨+顺铂方案',
                '营养建议.pdf': '营养管理建议',
                '心理评估.txt': '心理咨询记录',
                '并发症记录.pdf': '胰漏和感染',
                '未分类文件.xyz': '文件内容'
            }
            
            for file_name, content in test_files.items():
                file_path = os.path.join(tmpdir, file_name)
                with open(file_path, 'w') as f:
                    f.write(content)
            
            yield tmpdir
    
    def test_scan_directory(self, test_dir):
        """测试扫描目录"""
        scanner = FileScanner(test_dir)
        scanned = scanner.scan_directory()
        
        assert len(scanned) == 8, f"期望8个文件，实际{len(scanned)}个"
        print(f"✓ 扫描成功: 找到 {len(scanned)} 个文件")
    
    def test_file_hash_generation(self, test_dir):
        """测试文件哈希生成"""
        scanner = FileScanner(test_dir)
        scanned = scanner.scan_directory()
        
        for file in scanned:
            assert file.file_hash != "", f"文件 {file.file_name} 的哈希为空"
            assert len(file.file_hash) == 64, f"哈希长度不正确: {file.file_name}"
        
        print(f"✓ 所有 {len(scanned)} 个文件的哈希生成成功")
    
    def test_file_classification(self, test_dir):
        """测试文件分类"""
        scanner = FileScanner(test_dir)
        scanned = scanner.scan_directory()
        
        # 验证分类
        categories = {f.file_name: f.category for f in scanned}
        
        assert categories['病历_20240115.txt'] == FileCategory.MEDICAL_RECORDS
        assert categories['CT扫描报告.pdf'] == FileCategory.IMAGING
        assert categories['血液检查_CA19-9.xlsx'] == FileCategory.LAB_REPORTS
        assert categories['化疗方案.docx'] == FileCategory.PRESCRIPTIONS
        assert categories['营养建议.pdf'] == FileCategory.NUTRITION
        assert categories['心理评估.txt'] == FileCategory.PSYCHOLOGY
        assert categories['并发症记录.pdf'] == FileCategory.COMPLICATIONS
        assert categories['未分类文件.xyz'] == FileCategory.UNCONFIRMED
        
        print("✓ 所有文件分类成功")
    
    def test_get_summary(self, test_dir):
        """测试分类统计"""
        scanner = FileScanner(test_dir)
        scanner.scan_directory()
        summary = scanner.get_summary()
        
        # 应该有8个不同的分类
        assert len(summary) == 8, f"期望8种分类，实际{len(summary)}种"
        print(f"✓ 分类统计: {summary}")
    
    def test_get_unconfirmed_files(self, test_dir):
        """测试获取待确认文件"""
        scanner = FileScanner(test_dir)
        scanner.scan_directory()
        unconfirmed = scanner.get_unconfirmed_files()
        
        assert len(unconfirmed) == 1, "应该有1个待确认文件"
        assert unconfirmed[0].file_name == '未分类文件.xyz'
        print(f"✓ 待确认文件: {[f.file_name for f in unconfirmed]}")
    
    def test_get_by_category(self, test_dir):
        """测试按分类获取文件"""
        scanner = FileScanner(test_dir)
        scanner.scan_directory()
        
        medical_records = scanner.get_by_category(FileCategory.MEDICAL_RECORDS)
        assert len(medical_records) == 1
        assert medical_records[0].file_name == '病历_20240115.txt'
        
        imaging = scanner.get_by_category(FileCategory.IMAGING)
        assert len(imaging) == 1
        assert imaging[0].file_name == 'CT扫描报告.pdf'
        
        print(f"✓ 按分类筛选成功")
    
    def test_file_metadata(self, test_dir):
        """测试文件元数据"""
        scanner = FileScanner(test_dir)
        scanned = scanner.scan_directory()
        
        for file in scanned:
            assert file.file_path.startswith(test_dir)
            assert file.file_size > 0
            assert file.mtime > 0
            assert 0 <= file.confidence <= 1
        
        print(f"✓ 文件元数据完整")
    
    def test_duplicate_detection(self, test_dir):
        """测试重复文件检测"""
        # 创建相同内容的两个文件
        file1_path = os.path.join(test_dir, 'file1.txt')
        file2_path = os.path.join(test_dir, 'file2.txt')
        
        content = "相同的内容"
        with open(file1_path, 'w') as f:
            f.write(content)
        with open(file2_path, 'w') as f:
            f.write(content)
        
        scanner = FileScanner(test_dir)
        scanned = scanner.scan_directory()
        
        # 查找这两个文件
        file_hashes = {f.file_name: f.file_hash for f in scanned 
                      if f.file_name in ['file1.txt', 'file2.txt']}
        
        # 哈希应该相同
        assert file_hashes['file1.txt'] == file_hashes['file2.txt']
        print(f"✓ 重复文件检测成功 (哈希: {file_hashes['file1.txt'][:16]}...)")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
