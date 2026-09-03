# -*- coding: utf-8 -*-

import subprocess
from .base import PackageAdapter
from ..exceptions import AdapterError

class DnfAdapter(PackageAdapter):
    """Adaptador para o gerenciador DNF (Fedora/RHEL)"""
    
    def _run(self, args, check=True):
        try:
            cmd = ['dnf', '-y'] + args
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if check and result.returncode != 0:
                raise AdapterError(f"DNF falhou: {result.stderr.strip()}")
            return result
        except FileNotFoundError:
            raise AdapterError("DNF não encontrado no sistema")
    
    def install(self, package_name: str) -> None:
        self._run(['install', package_name])
    
    def remove(self, package_name: str) -> None:
        self._run(['remove', package_name])
    
    def is_installed(self, package_name: str) -> bool:
        try:
            subprocess.run(['rpm', '-q', package_name], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
