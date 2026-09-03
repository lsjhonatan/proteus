# -*- coding: utf-8 -*-

"""
Configuração de fixtures para testes
"""

import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_db():
    """Cria um banco de dados temporário"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    yield db_path
    
    # Limpeza
    Path(db_path).unlink(missing_ok=True)

@pytest.fixture
def temp_dir():
    """Cria um diretório temporário"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
