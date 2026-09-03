# Guia de Contribuição

## Reportando Bugs

Abra uma issue com:
- Descrição clara do problema
- Distribuição e versão do Python
- Comandos executados e logs de erro
- Passos para reproduzir

## Enviando Pull Requests

### Preparação

```
git clone https://github.com/lsjhonatan/pts.git
cd pts
pip install -e .[dev]
make build
```

### Padrões de Código

Python:
- PEP 8
- Type hints obrigatórios
- Docstrings em português
- Formatação com black: `make format`

C:
- ISO C99
- Comentários em português
- Cabeçalho GPL 3.0 em todos os arquivos

### Padrão de Commits

Conventional Commits:

```
<tipo>(<escopo>): <descrição curta>

<descrição longa opcional>
```

Tipos: feat, fix, docs, style, refactor, test, chore

Exemplo:

```
feat(snapshot): adiciona compressão Zstandard

Implementa compressão de snapshots para reduzir espaço em disco.
```

### Testes

```
make test          # Executa todos os testes
make test-unit     # Apenas unitários
make coverage      # Relatório de cobertura
```

Novas funcionalidades devem incluir testes unitários.

### Módulos C

Ao modificar src/pts/modules/:
- Compilar com `make build`
- Manter fallback em Python para quando a compilação falhar
- Testar em diferentes distribuições quando possível

## Código de Conduta

- Respeito entre todos os participantes
- Colaboração e revisão construtiva
- Foco na qualidade do código e documentação
