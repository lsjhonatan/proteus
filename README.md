# Proteus Tool Suite (pts)

Gerenciador de pacotes universal com atomicidade, mutabilidade e estabilidade.

Suporta Debian (APT), Fedora (DNF) e Arch Linux (Pacman) em uma única interface, adicionando camadas de controle e segurança que os gerenciadores nativos não oferecem.

## Filosofia

- Atomicidade: operações são transacionais. Falhas resultam em rollback automático.
- Mutabilidade: snapshots do estado do sistema permitem rollback temporal.
- Estabilidade: verificação SHA-256 e suporte a assinaturas GPG.

## Distribuições Suportadas

- Debian / Ubuntu (APT)
- Fedora / RHEL (DNF)
- Arch Linux (Pacman)

## Instalação

Via pip:

```
pip install pts
```

Via fonte:

```
git clone https://github.com/lsjhonatan/pts.git
cd pts
make install
```

Dependências de sistema:

- Python 3.9+
- GCC e Make
- OpenSSL
- Zstandard

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
│   │   ├── test_adapters.py
│   │   ├── test_database.py
│   │   └── test_snapshot.py
│   ├── integration/
│   │   └── test_cli.py
│   ├── fixtures/
│   │   └── mock_packages.json
│   ├── conftest.py
│   └── __init__.py
├── docs/
├── LICENSE
├── Makefile
├── setup.py
└── pyproject.toml
```

## Contribuição

Consulte CONTRIBUTING.md para detalhes sobre padrões de código, commits e fluxo de trabalho.

## Licença

GNU General Public License v3.0. Consulte LICENSE.
