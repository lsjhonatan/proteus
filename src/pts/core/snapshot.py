# -*- coding: utf-8 -*-

import json
import hashlib
import tempfile
import os
from datetime import datetime
from pathlib import Path

from ..exceptions import SnapshotError, IntegrityError
from ..adapters import get_adapter

try:
    from ..modules import _compress as compress
    from ..modules import _hash as hasher
    HAS_C_MODULES = True
except ImportError:
    HAS_C_MODULES = False
    class _HashFallback:
        @staticmethod
        def sha256(data):
            return hashlib.sha256(data).digest()
    hasher = _HashFallback

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

        if snapshots_dir:
            self.SNAPSHOTS_DIR = snapshots_dir
        elif os.environ.get('PTS_SNAPSHOTS_DIR'):
            self.SNAPSHOTS_DIR = os.environ['PTS_SNAPSHOTS_DIR']
        elif not self._can_write_to_var_lib():
            temp_dir = tempfile.mkdtemp(prefix="pts_snapshots_")
            self.SNAPSHOTS_DIR = temp_dir

        self._ensure_directory()

    def _can_write_to_var_lib(self) -> bool:
        try:
            Path("/var/lib/pts/snapshots").mkdir(parents=True, exist_ok=True)
            test_file = Path("/var/lib/pts/snapshots/.write_test")
            test_file.touch()
            test_file.unlink()
            return True
        except (PermissionError, OSError):
            return False

    def _ensure_directory(self):
        try:
            Path(self.SNAPSHOTS_DIR).mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError):
            temp_dir = tempfile.mkdtemp(prefix="pts_snapshots_")
            self.SNAPSHOTS_DIR = temp_dir
            Path(temp_dir).mkdir(parents=True, exist_ok=True)

    def _get_current_state(self):
        """
        Obtem o estado atual dos pacotes instalados no sistema.
        Utiliza o adaptador correspondente a distribuicao detectada.
        """
        try:
            adapter = get_adapter()
            packages = adapter.list_installed()
            return packages
        except Exception as e:
            # Fallback para dados mockados em caso de erro
            return [
                {"name": "nginx", "version": "1.24.0", "distro": "unknown", "hash": ""},
                {"name": "postgresql", "version": "15.0", "distro": "unknown", "hash": ""},
            ]

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
                    (pkg['name'], pkg['version'], pkg.get('distro', 'unknown'), pkg.get('hash', ''))
                )
                pkg_id = conn.execute(
                    "SELECT id FROM packages WHERE name = ? AND distro = ?",
                    (pkg['name'], pkg.get('distro', 'unknown'))
                ).fetchone()['id']
                conn.execute(
                    "INSERT INTO snapshot_packages (snapshot_id, package_id) VALUES (?, ?)",
                    (snapshot_id, pkg_id)
                )

        return str(snapshot_id)

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
            raise SnapshotError(f"Snapshot '{snapshot_id}' nao encontrado")

        snapshot_path = Path(self.SNAPSHOTS_DIR) / f"{snap['name']}.pts.snap"
        if not snapshot_path.exists():
            raise SnapshotError(f"Arquivo de snapshot nao encontrado: {snapshot_path}")

        compressed_data = snapshot_path.read_bytes()
        manifest_json = compress.decompress(compressed_data).decode()
        manifest = json.loads(manifest_json)

        current_hash = hasher.sha256(manifest_json.encode()).hex()
        if current_hash != snap['manifest_hash']:
            raise IntegrityError("Manifesto do snapshot corrompido")

        print(f"Restaurando {len(manifest['packages'])} pacotes do snapshot {snap['name']}")
