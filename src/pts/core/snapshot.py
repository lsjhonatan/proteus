# -*- coding: utf-8 -*-

import json
import hashlib
from datetime import datetime
from pathlib import Path

from ..exceptions import SnapshotError, IntegrityError

# Tenta importar os módulos C, usa fallback se não estiverem disponíveis
try:
    from ..modules import _compress as compress
    from ..modules import _hash as hasher
    HAS_C_MODULES = True
except ImportError:
    HAS_C_MODULES = False
    # Fallback para hash
    class _HashFallback:
        @staticmethod
        def sha256(data):
            return hashlib.sha256(data).digest()
    hasher = _HashFallback
    
    # Fallback para compress (sem compressão)
    class _CompressFallback:
        @staticmethod
        def compress(data):
            return data
        @staticmethod
        def decompress(data):
            return data
    compress = _CompressFallback

class SnapshotManager:
    SNAPSHOTS_DIR = "/var/lib/pts/snapshots"
    
    def __init__(self, database, snapshots_dir=None):
        self.db = database
        # Permite sobrescrever o diretório de snapshots
        if snapshots_dir:
            self.SNAPSHOTS_DIR = snapshots_dir
        self._ensure_directory()
    
    def _ensure_directory(self):
        Path(self.SNAPSHOTS_DIR).mkdir(parents=True, exist_ok=True)
    
    def create(self, name: str, description: str = "") -> str:
        packages = self._get_current_state()
        manifest = {
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "packages": packages
        }
        manifest_json = json.dumps(manifest, indent=2)
        manifest_hash = hasher.sha256(manifest_json.encode()).hex()
        
        snapshot_path = Path(self.SNAPSHOTS_DIR) / f"{name}.pts.snap"
        compressed_data = compress.compress(manifest_json.encode())
        snapshot_path.write_bytes(compressed_data)
        
        with self.db.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO snapshots (name, description, manifest_hash) VALUES (?, ?, ?)",
                (name, description, manifest_hash)
            )
            snapshot_id = cursor.lastrowid
            
            for pkg in packages:
                conn.execute(
                    "INSERT OR IGNORE INTO packages (name, version, distro, hash_sha256) VALUES (?, ?, ?, ?)",
                    (pkg['name'], pkg['version'], pkg['distro'], pkg.get('hash', ''))
                )
                pkg_id = conn.execute(
                    "SELECT id FROM packages WHERE name = ? AND distro = ?",
                    (pkg['name'], pkg['distro'])
                ).fetchone()['id']
                conn.execute(
                    "INSERT INTO snapshot_packages (snapshot_id, package_id) VALUES (?, ?)",
                    (snapshot_id, pkg_id)
                )
        
        return str(snapshot_id)
    
    def _get_current_state(self):
        return [
            {"name": "nginx", "version": "1.24.0", "distro": "ubuntu", "hash": "abc123"},
        ]
    
    def list_all(self):
        return self.db.execute(
            "SELECT id, name, description, created_at FROM snapshots ORDER BY created_at DESC"
        )
    
    def restore(self, snapshot_id: str):
        if snapshot_id.isdigit():
            snap = self.db.execute_one("SELECT * FROM snapshots WHERE id = ?", (int(snapshot_id),))
        else:
            snap = self.db.execute_one("SELECT * FROM snapshots WHERE name = ?", (snapshot_id,))
        
        if not snap:
            raise SnapshotError(f"Snapshot '{snapshot_id}' não encontrado")
        
        snapshot_path = Path(self.SNAPSHOTS_DIR) / f"{snap['name']}.pts.snap"
        if not snapshot_path.exists():
            raise SnapshotError(f"Arquivo de snapshot não encontrado: {snapshot_path}")
        
        compressed_data = snapshot_path.read_bytes()
        manifest_json = compress.decompress(compressed_data).decode()
        manifest = json.loads(manifest_json)
        
        current_hash = hasher.sha256(manifest_json.encode()).hex()
        if current_hash != snap['manifest_hash']:
            raise IntegrityError("Manifesto do snapshot corrompido")
        
        print(f"Restaurando {len(manifest['packages'])} pacotes do snapshot {snap['name']}")
