# -*- coding: utf-8 -*-

import subprocess
from .base import PackageAdapter

class AptAdapter(PackageAdapter):
    def install(self, package_name: str) -> None:
        subprocess.run(['apt', 'install', '-y', package_name], check=True)
    
    def remove(self, package_name: str) -> None:
        subprocess.run(['apt', 'remove', '-y', package_name], check=True)
    
    def is_installed(self, package_name: str) -> bool:
        try:
            subprocess.run(['dpkg-query', '-W', package_name], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
