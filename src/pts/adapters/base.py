# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod

class PackageAdapter(ABC):
    @abstractmethod
    def install(self, package_name: str) -> None:
        pass
    
    @abstractmethod
    def remove(self, package_name: str) -> None:
        pass
    
    @abstractmethod
    def is_installed(self, package_name: str) -> bool:
        pass
