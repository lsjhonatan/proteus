# -*- coding: utf-8 -*-

"""Adaptadores para gerenciadores de pacotes nativos"""

from .base import PackageAdapter
from .apt import AptAdapter
from .dnf import DnfAdapter
from .pacman import PacmanAdapter
from ..exceptions import AdapterError
import platform
import subprocess

def detect_distro() -> str:
    """Detecta a distribuição Linux atual"""
    try:
        with open('/etc/os-release', 'r') as f:
            content = f.read()
            if 'debian' in content.lower() or 'ubuntu' in content.lower():
                return 'debian'
            elif 'fedora' in content.lower() or 'rhel' in content.lower():
                return 'fedora'
            elif 'arch' in content.lower():
                return 'arch'
    except FileNotFoundError:
        pass
    
    # Fallback
    try:
        subprocess.run(['apt', '--version'], capture_output=True, check=True)
        return 'debian'
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    try:
        subprocess.run(['dnf', '--version'], capture_output=True, check=True)
        return 'fedora'
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    try:
        subprocess.run(['pacman', '--version'], capture_output=True, check=True)
        return 'arch'
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    raise AdapterError("Distribuição Linux não suportada ou não detectada")

def get_adapter() -> PackageAdapter:
    """Retorna o adaptador apropriado para a distribuição atual"""
    distro = detect_distro()
    
    adapters = {
        'debian': AptAdapter,
        'fedora': DnfAdapter,
        'arch': PacmanAdapter
    }
    
    if distro not in adapters:
        raise AdapterError(f"Distribuição {distro} não suportada")
    
    return adapters[distro]()
