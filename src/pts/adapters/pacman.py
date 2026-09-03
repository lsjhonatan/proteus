# -*- coding: utf-8 -*-

import subprocess
from .base import PackageAdapter
from ..exceptions import AdapterError

class PacmanAdapter(PackageAdapter):
    """Adaptador para o gerenciador Pacman (Arch Linux)"""
    
    def _run(self, args, check=True):
        try:
            cmd = ['pacman', '--noconfirm'] + args
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if check and result.returncode != 0:
                raise AdapterError(f"Pacman falhou: {result.stderr.strip()}")
            return result
        except FileNotFoundError:
            raise AdapterError("Pacman não encontrado no sistema")
    
    def install(self, package_name: str) -> None:
        self._run(['-S', package_name])
    
    def remove(self, package_name: str) -> None:
        self._run(['-R', package_name])
    
    def is_installed(self, package_name: str) -> bool:
        try:
            subprocess.run(['pacman', '-Q', package_name], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
