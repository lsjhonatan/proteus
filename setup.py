#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
import sys

class PtsBuildExt(build_ext):
    def build_extensions(self):
        if sys.platform.startswith('linux'):
            for ext in self.extensions:
                ext.extra_compile_args = ['-O2', '-Wall', '-fPIC']
                ext.extra_link_args = ['-lssl', '-lcrypto', '-lzstd']
        super().build_extensions()

pts_modules = [
    Extension(
        'pts.modules._hash',
        sources=['src/pts/modules/hash.c'],
        libraries=['ssl', 'crypto'],
    ),
    Extension(
        'pts.modules._compress',
        sources=['src/pts/modules/compress.c'],
        libraries=['zstd'],
    ),
    Extension(
        'pts.modules._lock',
        sources=['src/pts/modules/lock.c'],
    ),
]

setup(
    name='pts',
    version='1.0.0',
    author='Jhonatan L. Santos',
    description='Proteus Tool Suite - Gerenciador de pacotes universal',
    license='GPL-2.0-or-later',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    ext_modules=pts_modules,
    cmdclass={'build_ext': PtsBuildExt},
    python_requires='>=3.9',
    install_requires=[
        'click>=8.0',
        'rich>=12.0',
    ],
    entry_points={
        'console_scripts': ['pts=pts.cli.main:cli'],
    },
)
