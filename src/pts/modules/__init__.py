# -*- coding: utf-8 -*-

"""Módulos C do Proteus Tool Suite"""

import sys
import warnings

# Tenta importar os módulos C
try:
    from . import _hash
    from . import _compress
    from . import _lock
    HAS_C_MODULES = True
except ImportError as e:
    HAS_C_MODULES = False
    warnings.warn(f"Módulos C não disponíveis: {e}. Usando fallback em Python.")
    
    # Fallback para hash
    import hashlib
    class _HashFallback:
        @staticmethod
        def sha256(data):
            return hashlib.sha256(data).digest()
    _hash = _HashFallback
    
    # Fallback para compress (sem compressão)
    class _CompressFallback:
        @staticmethod
        def compress(data):
            return data
        @staticmethod
        def decompress(data):
            return data
    _compress = _CompressFallback
    
    # Fallback para lock (simulado)
    class _LockFallback:
        @staticmethod
        def acquire(path, timeout=30):
            return 0
        @staticmethod
        def release(fd):
            pass
    _lock = _LockFallback

__all__ = ['_hash', '_compress', '_lock', 'HAS_C_MODULES']
