# -*- coding: utf-8 -*-

"""
Testes unitários para os adaptadores de pacotes
"""

import pytest
from unittest.mock import patch, MagicMock
from src.pts.adapters import detect_distro, get_adapter
from src.pts.adapters.apt import AptAdapter
from src.pts.adapters.dnf import DnfAdapter
from src.pts.adapters.pacman import PacmanAdapter
from src.pts.exceptions import AdapterError

class TestAdapters:
    def test_detect_distro_debian(self):
        """Testa detecção de distribuição Debian/Ubuntu"""
        with patch('builtins.open') as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "ID=ubuntu\nVERSION_ID=22.04"
            assert detect_distro() == 'debian'
    
    def test_detect_distro_fedora(self):
        """Testa detecção de distribuição Fedora"""
        with patch('builtins.open') as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "ID=fedora\nVERSION_ID=38"
            assert detect_distro() == 'fedora'
    
    def test_detect_distro_arch(self):
        """Testa detecção de distribuição Arch"""
        with patch('builtins.open') as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "ID=arch\n"
            assert detect_distro() == 'arch'
    
    def test_get_adapter_debian(self):
        """Testa obtenção do adaptador Debian"""
        with patch('src.pts.adapters.detect_distro', return_value='debian'):
            adapter = get_adapter()
            assert isinstance(adapter, AptAdapter)
    
    def test_get_adapter_fedora(self):
        """Testa obtenção do adaptador Fedora"""
        with patch('src.pts.adapters.detect_distro', return_value='fedora'):
            adapter = get_adapter()
            assert isinstance(adapter, DnfAdapter)
    
    def test_get_adapter_arch(self):
        """Testa obtenção do adaptador Arch"""
        with patch('src.pts.adapters.detect_distro', return_value='arch'):
            adapter = get_adapter()
            assert isinstance(adapter, PacmanAdapter)
    
    def test_get_adapter_unsupported(self):
        """Testa distribuição não suportada"""
        with patch('src.pts.adapters.detect_distro', return_value='windows'):
            with pytest.raises(AdapterError):
                get_adapter()
