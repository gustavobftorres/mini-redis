# Engineering Journal

Este documento registra decisões técnicas, aprendizados, alternativas consideradas e mudanças de entendimento durante o desenvolvimento do mini-redis.

## Decisão 001 — Armazenamento somente em memória na v1

**Data:** 3 de novembro de 2026

### Contexto

O Redis real oferece mecanismos opcionais de persistência, mas o objetivo inicial do mini-redis é estudar comunicação TCP, framing, armazenamento chave–valor e concorrência.

Adicionar persistência agora aumentaria o escopo e introduziria problemas como formato de arquivo, recuperação após falhas, sincronização e integridade dos dados.

### Decisão

A primeira versão armazenará chaves e valores somente em memória.

Todo o estado será perdido quando o processo for encerrado. A aplicação não tentará salvar o conteúdo do cache em PostgreSQL ou em arquivos locais durante o desligamento.

### Alternativas consideradas

1. Salvar todo o conteúdo em arquivo ao encerrar o processo.
2. Registrar cada alteração em disco.
3. Sincronizar o cache com PostgreSQL.
4. Manter a primeira versão exclusivamente em memória.

### Motivo da escolha

A quarta alternativa mantém o projeto concentrado nos objetivos da primeira fase e permite compreender os componentes fundamentais antes de adicionar persistência.

### Consequências

**Positivas:**

- Escopo inicial menor.
- Implementação mais simples.
- Maior foco em TCP, protocolo e concorrência.
- Menos modos de falha na primeira versão.

**Negativas:**

- Todos os dados serão perdidos ao encerrar o processo.
- O mini-redis não será adequado para armazenar dados que não possam ser reconstruídos.
- A implementação não terá durabilidade.

### Possível evolução

Persistência poderá ser estudada em uma fase futura por meio de snapshots ou de um log de operações. Essa evolução exigirá uma nova decisão técnica.