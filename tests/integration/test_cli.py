# -*- coding: utf-8 -*-

"""
Testes de integração para CLI
"""

import pytest
from click.testing import CliRunner
from src.pts.cli.main import cli
from src.pts import __version__

class TestCLI:
    def test_version(self):
        """Testa comando --version"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert __version__ in result.output
    
    def test_status(self):
        """Testa comando status"""
        runner = CliRunner()
        result = runner.invoke(cli, ['status'])
        assert result.exit_code == 0
        assert "Proteus Tool Suite" in result.output
    
    def test_snapshot_list_empty(self):
        """Testa listagem de snapshots vazia"""
        runner = CliRunner()
        result = runner.invoke(cli, ['snapshot-list'])
        assert result.exit_code == 0
        assert "Nenhum snapshot encontrado" in result.output
