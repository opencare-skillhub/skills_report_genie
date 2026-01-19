"""数据库初始化模块

根据 SQLITE_DEPLOYMENT.md § 4.3 实现
- 创建所有表结构
- 创建索引
- 初始化系统参数
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional


class DatabaseInitializer:
    """SQLite数据库初始化器"""
    
    def __init__(self, db_path: str = "patient_case/skill.db"):
        """
        初始化数据库初始化器
        
        Args:
            db_path: 数据库文件路径，默认为 patient_case/skill.db
        """
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)
        self.connection: Optional[sqlite3.Connection] = None
    
    def initialize(self):
        """执行完整的数据库初始化流程"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self._create_tables()
            self._create_indexes()
            self._init_sys_params()
            self.connection.commit()
            print(f"✅ 数据库初始化成功: {self.db_path}")
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            print(f"❌ 数据库初始化失败: {e}")
            raise
        finally:
            if self.connection:
                self.connection.close()
    
    def _create_tables(self):
        """创建所有表结构"""
        cursor = self.connection.cursor()
        
        # 1. 患者基本信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                patient_id_method TEXT DEFAULT 'hash',
                name_hash TEXT UNIQUE,
                basic_info JSON,
                disease_timeline JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. 文件索引表 (用于去重和增量识别)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_index (
                file_hash TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                mtime REAL,
                status TEXT CHECK(status IN ('pending', 'processed', 'failed')),
                error_msg TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 3. 基因检测报告表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS genetic_reports (
                report_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                test_date TEXT,
                test_type TEXT,
                raw_content JSON,
                extracted_features JSON,
                version TEXT,
                source_file TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
            )
        ''')
        
        # 4. 病理检测报告表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pathology_reports (
                report_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                test_date TEXT,
                specimen_id TEXT,
                raw_content JSON,
                cancer_type TEXT,
                differentiation_grade TEXT,
                extracted_features JSON,
                risk_level TEXT,
                version TEXT,
                source_file TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
            )
        ''')
        
        # 5. 肿瘤标志物历史表 (用于趋势分析)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS markers_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                marker_type TEXT NOT NULL,
                date TEXT,
                value REAL,
                unit TEXT,
                source_file TEXT,
                imputed INTEGER DEFAULT 0,
                confidence TEXT DEFAULT 'high',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
            )
        ''')
        
        # 6. 临床试验缓存表 (避免重复查询)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clinical_trials_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                trial_id TEXT,
                trial_name TEXT,
                match_score REAL,
                match_reason TEXT,
                trial_status TEXT,
                trial_location TEXT,
                contact_info TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
            )
        ''')
        
        # 7. 处理日志表 (审计追踪)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                import_id TEXT,
                file_hash TEXT,
                step TEXT,
                status TEXT CHECK(status IN ('success', 'failure', 'warning')),
                error_msg TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (file_hash) REFERENCES file_index(file_hash)
            )
        ''')
        
        # 8. 系统参数表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sys_params (
                param_key TEXT PRIMARY KEY,
                param_value TEXT,
                param_type TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.connection.commit()
    
    def _create_indexes(self):
        """创建所有索引"""
        cursor = self.connection.cursor()
        
        # 患者表索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patient_created ON patients(created_at)')
        
        # 文件索引表索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_status ON file_index(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_path ON file_index(file_path)')
        
        # 基因检测报告索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_genetic_patient ON genetic_reports(patient_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_genetic_date ON genetic_reports(test_date)')
        
        # 病理检测报告索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pathology_patient ON pathology_reports(patient_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pathology_date ON pathology_reports(test_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pathology_cancer_type ON pathology_reports(cancer_type)')
        
        # 肿瘤标志物索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_marker_patient ON markers_history(patient_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_marker_type ON markers_history(marker_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_marker_date ON markers_history(date)')
        
        # 处理日志索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_log_patient ON processing_log(patient_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_log_import ON processing_log(import_id)')
        
        self.connection.commit()
    
    def _init_sys_params(self):
        """初始化系统参数"""
        cursor = self.connection.cursor()
        
        params = [
            ('db_version', '1.0', 'string', '数据库schema版本'),
            ('db_created_at', datetime.now().isoformat(), 'string', '数据库创建时间'),
            ('last_maintenance', datetime.now().isoformat(), 'string', '最后维护时间'),
            ('enable_privacy_mode', '1', 'integer', '是否启用隐私模式'),
            ('default_patient_id_method', 'hash', 'string', '患者ID生成方法'),
        ]
        
        for param_key, param_value, param_type, description in params:
            cursor.execute('''
                INSERT OR REPLACE INTO sys_params 
                (param_key, param_value, param_type, description) 
                VALUES (?, ?, ?, ?)
            ''', (param_key, param_value, param_type, description))
        
        self.connection.commit()
