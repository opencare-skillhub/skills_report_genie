"""数据库模块测试

测试数据库初始化、连接管理、CRUD操作
"""

import pytest
import sqlite3
import os
import tempfile
from pathlib import Path

# 添加src到路径
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.db_initializer import DatabaseInitializer
from src.database.db_manager import DatabaseManager


class TestDatabaseInitializer:
    """测试数据库初始化器"""
    
    @pytest.fixture
    def temp_db_path(self):
        """创建临时数据库路径"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, 'test.db')
            yield db_path
    
    def test_initialize_creates_database(self, temp_db_path):
        """测试初始化创建数据库文件"""
        initializer = DatabaseInitializer(temp_db_path)
        initializer.initialize()
        
        assert os.path.exists(temp_db_path)
        print(f"✓ 数据库文件创建成功: {temp_db_path}")
    
    def test_all_tables_created(self, temp_db_path):
        """测试所有表都被创建"""
        initializer = DatabaseInitializer(temp_db_path)
        initializer.initialize()
        
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # 查询所有表
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'patients', 'file_index', 'genetic_reports', 'pathology_reports',
            'markers_history', 'clinical_trials_cache', 'processing_log', 'sys_params'
        ]
        
        for table in expected_tables:
            assert table in tables, f"表 {table} 未被创建"
        
        conn.close()
        print(f"✓ 所有{len(expected_tables)}个表创建成功")
    
    def test_indexes_created(self, temp_db_path):
        """测试所有索引都被创建"""
        initializer = DatabaseInitializer(temp_db_path)
        initializer.initialize()
        
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # 查询所有索引
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        
        # 至少应该有索引
        assert len(indexes) > 0, "未创建任何索引"
        print(f"✓ 创建了 {len(indexes)} 个索引")
        
        conn.close()
    
    def test_sys_params_initialized(self, temp_db_path):
        """测试系统参数初始化"""
        initializer = DatabaseInitializer(temp_db_path)
        initializer.initialize()
        
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM sys_params")
        count = cursor.fetchone()[0]
        
        assert count == 5, f"期望5个系统参数，实际{count}个"
        
        # 验证关键参数
        cursor.execute("SELECT param_value FROM sys_params WHERE param_key = 'db_version'")
        version = cursor.fetchone()[0]
        assert version == '1.0'
        
        conn.close()
        print(f"✓ 系统参数初始化成功 (共{count}个参数)")


class TestDatabaseManager:
    """测试数据库连接管理器"""
    
    @pytest.fixture
    def temp_db_path(self):
        """创建临时数据库路径"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, 'test.db')
            # 初始化数据库
            initializer = DatabaseInitializer(db_path)
            initializer.initialize()
            yield db_path
    
    def test_singleton_pattern(self, temp_db_path):
        """测试单例模式"""
        # 重置单例
        DatabaseManager._instance = None
        DatabaseManager._connection = None
        
        manager1 = DatabaseManager(temp_db_path)
        manager2 = DatabaseManager(temp_db_path)
        
        assert manager1 is manager2, "单例模式失败"
        print("✓ 单例模式验证成功")
    
    def test_get_connection(self, temp_db_path):
        """测试获取连接"""
        # 重置单例
        DatabaseManager._instance = None
        DatabaseManager._connection = None
        
        manager = DatabaseManager(temp_db_path)
        conn = manager.get_connection()
        
        assert isinstance(conn, sqlite3.Connection)
        print("✓ 获取数据库连接成功")
    
    def test_execute_query(self, temp_db_path):
        """测试执行查询"""
        # 重置单例
        DatabaseManager._instance = None
        DatabaseManager._connection = None
        
        manager = DatabaseManager(temp_db_path)
        cursor = manager.execute("SELECT COUNT(*) FROM sys_params")
        result = cursor.fetchone()
        
        assert result[0] == 5, "查询系统参数失败"
        print("✓ 执行查询成功")
    
    def test_fetch_one(self, temp_db_path):
        """测试获取单条记录"""
        # 重置单例
        DatabaseManager._instance = None
        DatabaseManager._connection = None
        
        manager = DatabaseManager(temp_db_path)
        result = manager.fetch_one(
            "SELECT param_key, param_value FROM sys_params WHERE param_key = ?",
            ("db_version",)
        )
        
        assert result is not None
        assert result['param_key'] == 'db_version'
        assert result['param_value'] == '1.0'
        print(f"✓ 获取单条记录成功: {result}")
    
    def test_fetch_all(self, temp_db_path):
        """测试获取所有记录"""
        # 重置单例
        DatabaseManager._instance = None
        DatabaseManager._connection = None
        
        manager = DatabaseManager(temp_db_path)
        results = manager.fetch_all("SELECT param_key FROM sys_params")
        
        assert len(results) == 5, f"期望5条记录，实际{len(results)}条"
        print(f"✓ 获取所有记录成功 (共{len(results)}条)")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
