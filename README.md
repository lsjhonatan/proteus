# Proteus Tool Suite (pts)

Gerenciador de pacotes universal com atomicidade, mutabilidade e estabilidade.

Suporta Debian (APT), Fedora (DNF) e Arch Linux (Pacman) em uma única interface.

## Filosofia

- Atomicidade: operacoes sao transacionais. Falhas resultam em rollback automatico.
- Mutabilidade: snapshots do estado do sistema permitem rollback temporal.
- Estabilidade: verificacao SHA-256 dos pacotes.

## Distribuicoes Suportadas

- Debian / Ubuntu (APT)
- Fedora / RHEL (DNF)
- Arch Linux (Pacman)

## Instalacao

Clone o repositorio:

```
git clone https://github.com/lsjhonatan/pts.git
cd pts
```

Compile os modulos C:

```
make build
```

Instale o sistema:

```
sudo make install
```

Verifique a instalacao:

```
pts --version
```

## Dependencias de Sistema

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
pts install <pacote>      # Instala com snapshot automatico
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

## Estrutura do Projeto

```
pts/
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

## Contribuicao

Consulte CONTRIBUTING.md para detalhes sobre padroes de codigo, commits e fluxo de trabalho.

## Licenca

GNU General Public License v3.0. Consulte LICENSE.
