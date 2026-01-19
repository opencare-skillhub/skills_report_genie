"""数据库连接管理器

单例模式管理SQLite连接
自动重连机制
"""

import sqlite3
import os
from typing import Optional, List, Any, Tuple


class DatabaseManager:
    """单例模式的数据库连接管理器
    
    参考: SQLITE_DEPLOYMENT.md § 4.3
    """
    
    _instance: Optional['DatabaseManager'] = None
    _connection: Optional[sqlite3.Connection] = None
    
    def __new__(cls, db_path: str = "patient_case/skill.db"):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: str = "patient_case/skill.db"):
        if self._initialized:
            return
        
        self.db_path = db_path
        self._ensure_initialized()
        self._initialized = True
    
    def _ensure_initialized(self):
        """确保数据库已初始化"""
        if not os.path.exists(self.db_path):
            from .db_initializer import DatabaseInitializer
            initializer = DatabaseInitializer(self.db_path)
            initializer.initialize()
    
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接（自动重连）
        
        Returns:
            sqlite3.Connection: 数据库连接对象
        """
        try:
            if self._connection is None:
                self._connection = sqlite3.connect(self.db_path)
                self._connection.row_factory = sqlite3.Row
            # 测试连接
            self._connection.execute("SELECT 1")
            return self._connection
        except sqlite3.OperationalError as e:
            # 连接失败，重新连接
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
            return self._connection
    
    def execute(self, sql: str, params: Tuple = None) -> sqlite3.Cursor:
        """执行查询
        
        Args:
            sql: SQL语句
            params: 参数元组
            
        Returns:
            sqlite3.Cursor: 游标对象
        """
        cursor = self.get_connection().cursor()
        if params:
            return cursor.execute(sql, params)
        else:
            return cursor.execute(sql)
    
    def fetch_one(self, sql: str, params: Tuple = None) -> Optional[dict]:
        """获取单条记录
        
        Args:
            sql: SQL语句
            params: 参数元组
            
        Returns:
            dict or None: 记录字典或None
        """
        cursor = self.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def fetch_all(self, sql: str, params: Tuple = None) -> List[dict]:
        """获取所有记录
        
        Args:
            sql: SQL语句
            params: 参数元组
            
        Returns:
            List[dict]: 记录字典列表
        """
        cursor = self.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def commit(self):
        """提交事务"""
        if self._connection:
            self._connection.commit()
    
    def rollback(self):
        """回滚事务"""
        if self._connection:
            self._connection.rollback()
    
    def close(self):
        """关闭连接"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def __del__(self):
        """析构函数 - 关闭连接"""
        self.close()
