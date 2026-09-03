# -*- coding: utf-8 -*-

"""
Testes unitários para o gerenciador de banco de dados
"""

import pytest
import tempfile
import os
from src.pts.core.database import Database
from src.pts.exceptions import PtsError

class TestDatabase:
    def test_initialization(self):
        """Testa inicialização do banco de dados"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = Database(db_path)
            assert db.db_path == db_path
            assert os.path.exists(db_path)
            
            # Verifica se as tabelas foram criadas
            tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'")
            table_names = [t['name'] for t in tables]
            assert 'packages' in table_names
            assert 'snapshots' in table_names
            assert 'snapshot_packages' in table_names
            assert 'operations' in table_names
            
        finally:
            os.unlink(db_path)
    
    def test_transaction_success(self):
        """Testa transação com sucesso"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = Database(db_path)
            
            with db.transaction() as conn:
                conn.execute(
                    "INSERT INTO packages (name, version, distro, hash_sha256) VALUES (?, ?, ?, ?)",
                    ('nginx', '1.24.0', 'ubuntu', 'abc123')
                )
            
            # Verifica se o dado foi inserido
            result = db.execute_one("SELECT * FROM packages WHERE name = ?", ('nginx',))
            assert result is not None
            assert result['name'] == 'nginx'
            assert result['version'] == '1.24.0'
            
        finally:
            os.unlink(db_path)
    
    def test_transaction_rollback(self):
        """Testa rollback automático em caso de erro"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = Database(db_path)
            
            # Insere um registro inicial
            with db.transaction() as conn:
                conn.execute(
                    "INSERT INTO packages (name, version, distro, hash_sha256) VALUES (?, ?, ?, ?)",
                    ('apache', '2.4.0', 'ubuntu', 'def456')
                )
            
            # Tenta uma transação que falha (duplicata)
            with pytest.raises(PtsError):
                with db.transaction() as conn:
                    conn.execute(
                        "INSERT INTO packages (name, version, distro, hash_sha256) VALUES (?, ?, ?, ?)",
                        ('apache', '2.4.1', 'ubuntu', 'ghi789')
                    )
            
            # Verifica que o registro original permanece
            result = db.execute_one("SELECT * FROM packages WHERE name = ?", ('apache',))
            assert result is not None
            assert result['version'] == '2.4.0'
            
        finally:
            os.unlink(db_path)
