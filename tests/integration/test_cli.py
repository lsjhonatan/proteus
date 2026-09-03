# -*- coding: utf-8 -*-

import pytest
import tempfile
from pathlib import Path
from click.testing import CliRunner
from src.pts.cli.main import cli
from src.pts import __version__
from src.pts.core.database import Database

class TestCLI:
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert __version__ in result.output
    
    def test_status(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['status'])
        assert result.exit_code == 0
        assert "Proteus Tool Suite" in result.output
    
    def test_snapshot_list_empty(self, tmp_path):
        """Testa listagem de snapshots vazia usando um banco temporário"""
        # Cria um banco de dados temporário
        db_path = tmp_path / "test.db"
        db = Database(str(db_path))
        
        # Sobrescreve a função snapshot_list para usar o banco temporário
        # Nota: Isso é um hack para testes, mas é necessário devido à estrutura atual
        
        runner = CliRunner()
        # Executa com o banco temporário via variável de ambiente
        import os
        os.environ['PTS_DB_PATH'] = str(db_path)
        
        result = runner.invoke(cli, ['snapshot-list'])
        assert result.exit_code == 0
        assert "Nenhum snapshot encontrado" in result.output
        
        # Limpa
        del os.environ['PTS_DB_PATH']
