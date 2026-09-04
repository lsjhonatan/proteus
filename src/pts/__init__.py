# -*- coding: utf-8 -*-

"""
Proteus Tool Suite - Gerenciador de pacotes universal

Atomicidade, mutabilidade e estabilidade para APT, DNF e Pacman.
"""

__version__ = "1.0.0"
__author__ = "Jhonatan L. Santos"
__license__ = "GPL-2.0-or-later"

from .exceptions import (
    PtsError,
    PackageNotFoundError,
    SnapshotError,
    LockError,
    IntegrityError
)

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "PtsError",
    "PackageNotFoundError",
    "SnapshotError",
    "LockError",
    "IntegrityError"
]
