# -*- coding: utf-8 -*-

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager

class Database:
    DB_PATH = "/var/lib/pts/pts.db"
    
    def __init__(self, db_path=None):
        self.db_path = db_path or self.DB_PATH
        self._ensure_directory()
        self._initialize_schema()
    
    def _ensure_directory(self):
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            Path(db_dir).mkdir(parents=True, exist_ok=True)
    
    def _initialize_schema(self):
        schema = """
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            version TEXT NOT NULL,
            distro TEXT NOT NULL,
            hash_sha256 TEXT NOT NULL,
            install_date DATETIME DEFAULT CURRENT_TIMESTAMP
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
        """
        with self.get_connection() as conn:
            conn.executescript(schema)
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
        finally:
            conn.close()
    
    @contextmanager
    def transaction(self):
        with self.get_connection() as conn:
            try:
                conn.execute("BEGIN IMMEDIATE")
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
