# -*- coding: utf-8 -*-

"""
Gerenciador de snapshots do Proteus Tool Suite

Criação, listagem e restauração de snapshots atômicos.
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from ..exceptions import SnapshotError, IntegrityError
from ..modules import _compress as compress
from ..modules import _hash as hasher

class SnapshotManager:
    """Gerencia snapshots do estado do sistema"""
    
    SNAPSHOTS_DIR = "/var/lib/pts/snapshots"
    
    def __init__(self, database):
        self.db = database
        self._ensure_directory()
    
    def _ensure_directory(self) -> None:
        Path(self.SNAPSHOTS_DIR).mkdir(parents=True, exist_ok=True)
    
    def create(self, name: str, description: str = "") -> str:
        """
        Cria um snapshot do estado atual dos pacotes
        
        Args:
            name: Nome único do snapshot
            description: Descrição opcional
            
        Returns:
            ID do snapshot criado
        """
        # Coleta estado atual dos pacotes
        packages = self._get_current_state()
        
        # Cria manifesto
        manifest = {
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "packages": packages
        }
        
        # Serializa e compacta
        manifest_json = json.dumps(manifest, indent=2)
        manifest_hash = hasher.sha256(manifest_json.encode()).hex()
        
        # Salva snapshot compactado
        snapshot_path = Path(self.SNAPSHOTS_DIR) / f"{name}.pts.snap"
        compressed_data = compress.compress(manifest_json.encode())
        snapshot_path.write_bytes(compressed_data)
        
        # Registra no banco
        with self.db.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO snapshots (name, description, manifest_hash) VALUES (?, ?, ?)",
                (name, description, manifest_hash)
            )
            snapshot_id = cursor.lastrowid
            
            # Registra pacotes do snapshot
            for pkg in packages:
                conn.execute(
                    """INSERT OR IGNORE INTO packages (name, version, distro, hash_sha256)
                       VALUES (?, ?, ?, ?)""",
                    (pkg['name'], pkg['version'], pkg['distro'], pkg.get('hash', ''))
                )
                
                # Associa ao snapshot
                pkg_id = conn.execute(
                    "SELECT id FROM packages WHERE name = ? AND distro = ?",
                    (pkg['name'], pkg['distro'])
                ).fetchone()['id']
                
                conn.execute(
                    "INSERT INTO snapshot_packages (snapshot_id, package_id) VALUES (?, ?)",
                    (snapshot_id, pkg_id)
                )
        
        return str(snapshot_id)
    
    def _get_current_state(self) -> List[Dict]:
        """
        Obtém o estado atual dos pacotes do sistema
        TODO: Integrar com adaptadores reais
        """
        # Placeholder - será substituído pela integração real
        return [
            {"name": "nginx", "version": "1.24.0", "distro": "ubuntu", "hash": "abc123"},
        ]
    
    def list_all(self) -> List[Dict]:
        """Lista todos os snapshots disponíveis"""
        return self.db.execute(
            "SELECT id, name, description, created_at FROM snapshots ORDER BY created_at DESC"
        )
    
    def restore(self, snapshot_id: str) -> None:
        """
        Restaura um snapshot
        
        Args:
            snapshot_id: ID ou nome do snapshot
        """
        # Busca snapshot no banco
        if snapshot_id.isdigit():
            snap = self.db.execute_one(
                "SELECT * FROM snapshots WHERE id = ?", (int(snapshot_id),)
            )
        else:
            snap = self.db.execute_one(
                "SELECT * FROM snapshots WHERE name = ?", (snapshot_id,)
            )
        
        if not snap:
            raise SnapshotError(f"Snapshot '{snapshot_id}' não encontrado")
        
        # Carrega manifesto
        snapshot_path = Path(self.SNAPSHOTS_DIR) / f"{snap['name']}.pts.snap"
        if not snapshot_path.exists():
            raise SnapshotError(f"Arquivo de snapshot não encontrado: {snapshot_path}")
        
        compressed_data = snapshot_path.read_bytes()
        manifest_json = compress.decompress(compressed_data).decode()
        manifest = json.loads(manifest_json)
        
        # Verifica integridade
        current_hash = hasher.sha256(manifest_json.encode()).hex()
        if current_hash != snap['manifest_hash']:
            raise IntegrityError("Manifesto do snapshot corrompido")
        
        # TODO: Restauração real via adaptadores
        print(f"Restaurando {len(manifest['packages'])} pacotes do snapshot {snap['name']}")
