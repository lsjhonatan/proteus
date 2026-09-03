# Arquitetura do Proteus Tool Suite

## Visão Geral

O Proteus Tool Suite é um gerenciador de pacotes universal que opera como uma camada de abstração sobre os gerenciadores nativos (APT, DNF, Pacman). A arquitetura é modular, com separação clara entre interface, lógica de negócio e integração com sistemas externos.

## Princípios Arquiteturais

- Atomicidade: operações são transacionais e reversíveis.
- Mutabilidade: snapshots permitem restauração de estado.
- Estabilidade: verificação de integridade e fallbacks em todos os níveis.

## Estrutura de Diretórios

```
src/pts/
├── adapters/       # Integração com gerenciadores nativos
├── cli/            # Interface de linha de comando
├── core/           # Lógica central (banco, snapshots)
└── modules/        # Módulos C para performance
```

## Decisões de Projeto

### 1. Adaptadores

Os adaptadores implementam o padrão Strategy. Cada distribuição possui sua própria classe que herda de `PackageAdapter`.

Decisão: isolar a lógica específica de cada gerenciador para facilitar a adição de novas distribuições e manter o núcleo do sistema limpo.

### 2. Banco de Dados

SQLite foi escolhido por ser embutido, transacional e suportar WAL (Write-Ahead Logging), essencial para atomicidade.

Schema inclui tabelas para pacotes, snapshots, operações e relacionamentos. Transações são usadas em todas as operações que modificam o estado.

### 3. Módulos C

Três módulos críticos foram implementados em C por questões de performance:

- `_hash`: SHA-256 usando OpenSSL EVP (versão moderna, compatível com OpenSSL 3.0)
- `_compress`: compressão Zstandard para snapshots
- `_lock`: lock de arquivos com flock

Decisão: manter fallback em Python para quando os módulos C não compilarem, garantindo portabilidade.

### 4. Snapshots

Snapshots são armazenados como arquivos compactados com Zstandard contendo um manifesto JSON com a lista de pacotes e hashes.

Decisão: usar arquivos externos em vez de armazenar tudo no banco para evitar crescimento excessivo do banco de dados e permitir compressão eficiente.

### 5. Atomicidade

Transações SQLite garantem atomicidade no banco de dados. Para operações que envolvem múltiplos passos (instalação + registro), a transação só é confirmada após todos os passos serem concluídos com sucesso.

### 6. Fallbacks

- Módulos C: fallback para implementações em Python puro quando a compilação falha.
- Banco de dados: fallback para diretórios temporários quando não há permissão em `/var/lib/pts/`.
- Detecção de distribuição: fallback para comandos nativos quando `/etc/os-release` não está disponível.

Decisão: garantir que o sistema funcione em qualquer ambiente, mesmo que com funcionalidades reduzidas.

### 7. Interface de Linha de Comando

CLI construída com Click e Rich para fornecer feedback visual claro (barras de progresso, tabelas, cores).

Comandos principais: `install`, `remove`, `snapshot-create`, `snapshot-list`, `rollback`, `status`.

### 8. Instalação e Build

Build via `setup.py` com compilação dos módulos C. Instalação via `pip install -e .` com flag `--break-system-packages` para sistemas com PEP 668 (Ubuntu 24.04+).

## Fluxos de Operação

### Instalação de Pacote

1. Verifica se o pacote já está instalado via adaptador.
2. Cria snapshot automático do estado atual.
3. Executa instalação via adaptador nativo.
4. Registra pacote no banco de dados.
5. Confirma transação.

### Criação de Snapshot

1. Obtém lista de pacotes instalados via adaptador.
2. Gera manifesto JSON com lista e hashes.
3. Compacta com Zstandard.
4. Salva arquivo em `/var/lib/pts/snapshots/`.
5. Registra metadados no banco de dados.

### Rollback

1. Busca snapshot no banco por ID ou nome.
2. Descompacta manifesto e verifica integridade (hash).
3. Restaura lista de pacotes via adaptador.
4. Atualiza banco de dados.

## Considerações de Segurança

- Hashes SHA-256 verificam integridade dos snapshots.
- Lock de arquivos previne execução simultânea de operações conflitantes.
- Fallbacks garantem que falhas em módulos C não comprometam o sistema.

## Limitações Conhecidas

- Snapshots restauram apenas a lista de pacotes, não configurações de usuário.
- Depende dos gerenciadores nativos para operações de instalação/remoção.
- Requer permissões de root para instalação e operações em `/var/lib/pts/`.

## Evolução Planejada

- Empacotamento para PyPI (distribuição via `pip install pts`).
- CI/CD com GitHub Actions.
- Suporte a assinaturas GPG para verificação de autenticidade.
- Logs estruturados com rotação de arquivos.
