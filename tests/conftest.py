# -*- coding: utf-8 -*-

import pytest
import os
import tempfile
from pathlib import Path

@pytest.fixture(autouse=True, scope="session")
def setup_test_environment():
    """Configura ambiente de teste com diretórios temporários"""
    # Cria diretórios temporários
    with tempfile.TemporaryDirectory() as tmp_db_dir, \
         tempfile.TemporaryDirectory() as tmp_snap_dir:
        
        db_path = Path(tmp_db_dir) / "test.db"
        snap_dir = Path(tmp_snap_dir)
        
        # Configura variáveis de ambiente
        os.environ['PTS_DB_PATH'] = str(db_path)
        os.environ['PTS_SNAPSHOTS_DIR'] = str(snap_dir)
        
        yield
        
        # Limpeza é automática com TemporaryDirectory

@pytest.fixture
def temp_db():
    """Cria um banco de dados temporário"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    yield db_path
    
    Path(db_path).unlink(missing_ok=True)

@pytest.fixture
def temp_dir():
    """Cria um diretório temporário"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
