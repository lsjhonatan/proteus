[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/lsjhonatan/proteus/releases/tag/v1.0.0)
[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

# Proteus Tool Suite (pts)

Gerenciador de pacotes universal com atomicidade, mutabilidade e estabilidade.

Suporta Debian (APT), Fedora (DNF) e Arch Linux (Pacman) em uma única interface.

---

## Instalação

Clone o repositório:

```
git clone https://github.com/lsjhonatan/proteus.git
cd proteus
```

Compile os módulos C:

```
make build
```

Instale o sistema:

```
sudo make install
```

Verifique a instalação:

```
pts --version
```

## Dependências de Sistema

- Python 3.9+
- GCC e Make
- OpenSSL (libssl-dev)
- Zstandard (libzstd-dev)

No Ubuntu/Debian:

```
sudo apt-get install python3 python3-pip gcc make libssl-dev libzstd-dev
```

No Fedora:

```
sudo dnf install python3 python3-pip gcc make openssl-devel libzstd-devel
```

No Arch:

```
sudo pacman -S python python-pip gcc make openssl zstd
```

## Comandos

```
pts install <pacote>      # Instala com snapshot automático
pts remove <pacote>       # Remove pacote
pts snapshot-create       # Cria snapshot manual
pts snapshot-list         # Lista snapshots
pts rollback <id>         # Restaura snapshot
pts status                # Exibe estado do sistema
```

Exemplo:

```
pts install nginx postgresql
pts snapshot-create --description "pre-upgrade"
sudo apt upgrade
pts rollback 3 --yes
```

## Filosofia

- Atomicidade: operações são transacionais. Falhas resultam em rollback automático.
- Mutabilidade: snapshots do estado do sistema permitem rollback temporal.
- Estabilidade: verificação SHA-256 dos pacotes.

## Distribuições Suportadas

- Debian / Ubuntu (APT)
- Fedora / RHEL (DNF)
- Arch Linux (Pacman)

## Estrutura do Projeto

```
proteus/
├── src/
│   └── pts/
│       ├── adapters/
│       │   ├── apt.py
│       │   ├── base.py
│       │   ├── dnf.py
│       │   └── pacman.py
│       ├── cli/
│       │   └── main.py
│       ├── core/
│       │   ├── database.py
│       │   └── snapshot.py
│       ├── modules/
│       │   ├── compress.c
│       │   ├── hash.c
│       │   └── lock.c
│       ├── exceptions.py
│       └── __init__.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/
├── LICENSE
├── Makefile
├── setup.py
└── pyproject.toml
```

## Contribuição

Consulte CONTRIBUTING.md para detalhes sobre padrões de código, commits e fluxo de trabalho.

## Licença

GNU General Public License v2.0. Consulte LICENSE.
