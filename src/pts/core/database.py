# -*- coding: utf-8 -*-

import sqlite3
import os
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from pathlib import Path

from ..exceptions import PtsError

class Database:
    DB_PATH = "/var/lib/pts/pts.db"
    SCHEMA_VERSION = 1
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or self.DB_PATH
        self._ensure_directory()
        self._initialize_schema()
    
    def _ensure_directory(self) -> None:
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            Path(db_dir).mkdir(parents=True, exist_ok=True)
    
    def _initialize_schema(self) -> None:
        schema = """
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            version TEXT NOT NULL,
            distro TEXT NOT NULL,
            hash_sha256 TEXT NOT NULL,
            install_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, distro)
        );
        
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            manifest_hash TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS snapshot_packages (
            snapshot_id INTEGER NOT NULL,
            package_id INTEGER NOT NULL,
            FOREIGN KEY (snapshot_id) REFERENCES snapshots(id) ON DELETE CASCADE,
            FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE,
            PRIMARY KEY (snapshot_id, package_id)
        );
        
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            package_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL,
            error_message TEXT,
            FOREIGN KEY (package_id) REFERENCES packages(id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_packages_name ON packages(name);
        CREATE INDEX IF NOT EXISTS idx_snapshots_created ON snapshots(created_at);
        CREATE INDEX IF NOT EXISTS idx_operations_timestamp ON operations(timestamp);
        """
        
        try:
            with self.get_connection() as conn:
                conn.executescript(schema)
                # CORREÇÃO: Não usar placeholder '?', usar valor direto
                conn.execute(f"PRAGMA user_version = {self.SCHEMA_VERSION}")
        except sqlite3.Error as e:
            raise PtsError(f"Falha ao inicializar schema do banco: {e}")
    
    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA foreign_keys=ON")
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise PtsError(f"Erro no banco de dados: {e}")
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def transaction(self):
        with self.get_connection() as conn:
            try:
                conn.execute("BEGIN IMMEDIATE")
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise PtsError(f"Transação falhou: {e}")
    
    def execute(self, query: str, params: tuple = ()) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
