# -*- coding: utf-8 -*-

import pytest
import os
from pathlib import Path
from click.testing import CliRunner
from src.pts.cli.main import cli
from src.pts import __version__
from src.pts.core.database import Database
from src.pts.core.snapshot import SnapshotManager

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
        """Testa listagem de snapshots vazia usando diretórios temporários"""
        db_path = tmp_path / "test.db"
        snapshots_dir = tmp_path / "snapshots"
        
        # Cria o banco de dados
        db = Database(str(db_path))
        
        # Cria o SnapshotManager com diretório personalizado
        snapman = SnapshotManager(db, str(snapshots_dir))
        
        # Sobrescreve o SNAPSHOTS_DIR no módulo para o teste
        import src.pts.core.snapshot
        src.pts.core.snapshot.SnapshotManager.SNAPSHOTS_DIR = str(snapshots_dir)
        
        # Configura as variáveis de ambiente para o CLI
        os.environ['PTS_DB_PATH'] = str(db_path)
        os.environ['PTS_SNAPSHOTS_DIR'] = str(snapshots_dir)
        
        runner = CliRunner()
        result = runner.invoke(cli, ['snapshot-list'])
        
        assert result.exit_code == 0, f"Erro: {result.output}\nException: {result.exception}"
        assert "Nenhum snapshot encontrado" in result.output
        
        # Limpa
        del os.environ['PTS_DB_PATH']
        del os.environ['PTS_SNAPSHOTS_DIR']
