# -*- coding: utf-8 -*-

"""
Definição de exceções customizadas do Proteus Tool Suite
"""

class PtsError(Exception):
    """Exceção base para todos os erros do pts"""
    pass

class PackageNotFoundError(PtsError):
    """Pacote não encontrado no sistema ou nos repositórios"""
    pass

class SnapshotError(PtsError):
    """Erro relacionado a snapshots (criação, restauração, etc)"""
    pass

class LockError(PtsError):
    """Erro ao adquirir ou liberar lock de arquivo"""
    pass

class IntegrityError(PtsError):
    """Erro de integridade (hash mismatch, assinatura inválida)"""
    pass

class ConfigurationError(PtsError):
    """Erro na configuração do pts"""
    pass

class AdapterError(PtsError):
    """Erro no adaptador do gerenciador nativo (APT/DNF/Pacman)"""
    pass
