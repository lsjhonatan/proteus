# -*- coding: utf-8 -*-

"""
Testes unitários para o gerenciador de snapshots
"""

import pytest
import tempfile
import json
from pathlib import Path
from src.pts.core.database import Database
from src.pts.core.snapshot import SnapshotManager
from src.pts.exceptions import SnapshotError, IntegrityError

class TestSnapshotManager:
    def test_create_snapshot(self, tmp_path):
        """Testa criação de snapshot"""
        db_path = tmp_path / "test.db"
        snapshots_dir = tmp_path / "snapshots"
        
        # Configura diretório de snapshots
        SnapshotManager.SNAPSHOTS_DIR = str(snapshots_dir)
        
        db = Database(str(db_path))
        snapman = SnapshotManager(db)
        
        # Cria snapshot
        snap_id = snapman.create("test-snapshot", "Snapshot de teste")
        assert snap_id is not None
        
        # Verifica no banco
        snap = db.execute_one("SELECT * FROM snapshots WHERE name = ?", ("test-snapshot",))
        assert snap is not None
        assert snap['name'] == "test-snapshot"
        assert snap['description'] == "Snapshot de teste"
        
        # Verifica arquivo
        snapshot_file = snapshots_dir / "test-snapshot.pts.snap"
        assert snapshot_file.exists()
        
        # Verifica conteúdo
        compressed = snapshot_file.read_bytes()
        from src.pts.modules import _compress
        manifest_json = _compress.decompress(compressed).decode()
        manifest = json.loads(manifest_json)
        assert manifest['name'] == "test-snapshot"
        assert 'packages' in manifest
    
    def test_list_snapshots(self, tmp_path):
        """Testa listagem de snapshots"""
        db_path = tmp_path / "test.db"
        snapshots_dir = tmp_path / "snapshots"
        
        SnapshotManager.SNAPSHOTS_DIR = str(snapshots_dir)
        
        db = Database(str(db_path))
        snapman = SnapshotManager(db)
        
        # Cria alguns snapshots
        snapman.create("snap-1", "Primeiro")
        snapman.create("snap-2", "Segundo")
        
        # Lista
        snaps = snapman.list_all()
        assert len(snaps) == 2
        assert snaps[0]['name'] in ["snap-1", "snap-2"]
    
    def test_restore_snapshot(self, tmp_path):
        """Testa restauração de snapshot"""
        # Este teste é mais complexo e será implementado com mocks
        pass
