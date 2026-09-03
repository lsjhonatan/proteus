# -*- coding: utf-8 -*-

import pytest
import tempfile
from pathlib import Path

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

@pytest.fixture(autouse=True)
def setup_test_env():
    """Configura ambiente para testes"""
    import os
    # Garante que os testes usem um diretório temporário
    original_db = os.environ.get('PTS_DB_PATH')
    yield
    # Limpa após os testes
    if original_db:
        os.environ['PTS_DB_PATH'] = original_db
    else:
        os.environ.pop('PTS_DB_PATH', None)
