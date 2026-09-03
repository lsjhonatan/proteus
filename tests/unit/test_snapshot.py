# -*- coding: utf-8 -*-

"""
Testes unitários para o gerenciador de snapshots
"""

import pytest
import json
from pathlib import Path
from src.pts.core.database import Database
from src.pts.core.snapshot import SnapshotManager

class TestSnapshotManager:
    def test_create_snapshot(self, temp_dir):
        """Testa criação de snapshot"""
        db_path = temp_dir / "test.db"
        snapshots_dir = temp_dir / "snapshots"
        
        db = Database(str(db_path))
        snapman = SnapshotManager(db, str(snapshots_dir))
        
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
    
    def test_list_snapshots(self, temp_dir):
        """Testa listagem de snapshots"""
        db_path = temp_dir / "test.db"
        snapshots_dir = temp_dir / "snapshots"
        
        db = Database(str(db_path))
        snapman = SnapshotManager(db, str(snapshots_dir))
        
        # Cria alguns snapshots
        snapman.create("snap-1", "Primeiro")
        snapman.create("snap-2", "Segundo")
        
        # Lista
        snaps = snapman.list_all()
        assert len(snaps) == 2
        names = [s['name'] for s in snaps]
        assert "snap-1" in names
        assert "snap-2" in names
