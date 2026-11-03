# mini-redis
A from-scratch Redis-inspired key-value server built to study networking, storage, concurrency and reliability.

# Perguntas e respostas (Issue 1)

## O que é o Redis antes de mais nada?
O Redis é um servidor de estruturas de dados que mantém informações principalmente em memória. Entre seus usos mais comuns está o cache, pois a busca por uma chave em uma tabela hash possui complexidade O(1) em média. Com isso, uma aplicação pode evitar consultas repetidas à sua fonte de dados principal enquanto o conteúdo do cache permanecer válido.

O Redis real também oferece funcionalidades como Pub/Sub, replicação e diferentes estruturas de dados. Essas funcionalidades ajudam a entender o produto original, mas não fazem parte do escopo da primeira versão do mini-redis.

Embora trabalhe principalmente em memória, o Redis real pode persistir dados por meio de mecanismos como RDB e AOF. A perda de todo o estado ao encerrar o processo é uma decisão específica do mini-redis v1, e não uma limitação geral do Redis.

A ideia de implementar na mão algo dessa linha é voltar a aprender sobre as questões mais estruturais da engenharia de software, seja voltar a discutir sobre protocolos de comunicação, uso de memória, tempo computacional, perguntas que desenvolvem a senioridade.

## Objetivos do projeto
Realizar uma implementação manual inspirada no Redis para estudar armazenamento chave-valor, uso de memória, protocolos de comunicação e concorrência. Funcionalidades como persistência e replicação poderão ser estudadas em fases futuras, mas não fazem parte da v1.

## Escopo mínimo da v1

- Servidor acessível por uma conexão TCP persistente.
- Suporte aos comandos `SET`, `GET`, `DEL` e `EXISTS`.
- Chaves e valores representados como strings UTF-8.
- Armazenamento exclusivamente em memória.
- Perda de todo o estado quando o processo for encerrado.
- Suporte a múltiplas conexões de clientes, sem exigir paralelismo na execução dos comandos.

## Requisitos funcionais
SET chave valor -> cria e armazena um valor associado a uma chave
GET chave -> recupera o valor associado à chave
DEL chave -> remove a chave existente
EXISTS chave -> verifica se uma chave existe

exemplo de interação conceitual:
```
SET usuario:1 Fulano
GET usuario:1
-> "Fulano"

EXISTS usuario:1
→ 1

DEL usuario:1
GET usuario:1
→ chave inexistente
```


### Premissas comuns dos contratos

Na versão 1, chaves e valores são strings UTF-8. A chave é obrigatória, não pode ser vazia e diferencia letras maiúsculas de minúsculas. O valor pode ser uma string vazia.

Cada comando é executado atomicamente: nenhum outro cliente pode observar um estado intermediário da operação.

Comandos com quantidade incorreta de argumentos ou argumentos inválidos retornam um erro explícito e não alteram o armazenamento.

Os limites máximos de tamanho de chave e valor deverão ser definidos junto com o protocolo, antes da implementação.

### RF-01 — SET chave valor

#### 1. Descrição

O comando associa o valor informado à chave informada.

Quando a chave ainda não existe, uma nova associação é criada. Quando a chave já existe, seu valor anterior é substituído.

#### 2. Entrada

O comando recebe dois parâmetros:

| Parâmetro | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| chave | string | sim | Identificador usado para armazenar e recuperar o valor |
| valor | string | sim | Conteúdo que será associado à chave |

#### 3. Pré-condições

- A chave deve ser uma string válida e não pode ser vazia.
- O valor deve ser uma string válida.
- A chave e o valor devem respeitar os limites de tamanho definidos pelo protocolo.
- A existência prévia da chave não impede a operação.
- O mesmo valor pode estar associado a diferentes chaves.

#### 4. Pós-condições

- Se a chave não existia, uma nova associação é criada.
- Se a chave já existia, seu valor anterior é substituído.
- Depois do sucesso, uma consulta à chave deve retornar o novo valor.
- Nenhuma outra chave deve ser modificada.

#### 5. Resposta

- **Sucesso:** retorna `OK`.
- **Falha:** retorna um erro explícito e não altera o armazenamento.

Podem provocar falha:

- Ausência da chave ou do valor.
- Quantidade incorreta de argumentos.
- Chave vazia.
- Tipo de entrada inválido.
- Chave ou valor acima do limite permitido.

#### 6. Casos de borda

- Criação de uma chave inexistente.
- Sobrescrita de uma chave existente.
- Armazenamento de um valor vazio.
- Duas chaves diferentes contendo o mesmo valor.
- Tentativa de usar uma chave vazia.
- Entrada acima do limite permitido.

#### 7. Invariantes

- Cada chave possui no máximo um valor atual.
- Um mesmo valor pode estar associado a várias chaves.
- A operação é atômica: outros clientes não podem observar um estado intermediário.
- Em caso de erro, o estado anterior permanece inalterado.

#### 8. Critérios de aceitação

- Uma chave inexistente é criada com o valor informado.
- Uma chave existente tem seu valor substituído.
- Duas chaves diferentes podem conter o mesmo valor.
- O sucesso retorna `OK`.
- Entradas inválidas retornam erro sem modificar o armazenamento.
- Após o sucesso, `GET` para a mesma chave retorna o novo valor.

### RF-02 — GET chave

**Descrição**

Recupera o valor atualmente associado à chave informada.

**Entrada**

Recebe exatamente uma chave.

**Pré-condições**

A chave deve respeitar o tipo e os limites definidos pelo protocolo. A chave não precisa existir.

**Pós-condições**

O armazenamento não é alterado.

**Resposta**

Se a chave existir, retorna seu valor integral, inclusive quando esse valor for uma string vazia. Se não existir, retorna uma representação específica de valor ausente. Essa representação deve ser diferente de uma string vazia. Entradas inválidas retornam erro.

**Casos de borda**

O contrato deve distinguir chave inexistente de chave com valor vazio e deve cobrir ausência ou excesso de argumentos.

**Invariantes**

O comando nunca cria, remove ou altera uma chave. Chamadas repetidas produzem o mesmo resultado enquanto nenhum comando de escrita modificar a chave.

**Critérios de aceitação**

Uma chave existente devolve exatamente o valor armazenado. Uma chave inexistente devolve o marcador de ausência. A consulta não modifica o número de chaves nem seus valores.

### RF-03 — DEL chave

**Descrição**

Remove do armazenamento a chave informada e o valor associado a ela.

**Entrada**

Recebe exatamente uma chave.

**Pré-condições**

A chave deve respeitar o tipo e os limites do protocolo. A existência prévia da chave não é obrigatória.

**Pós-condições**

Se a chave existia, ela deixa de existir. Se não existia, o armazenamento permanece inalterado.

**Resposta**

Retorna `1` quando uma chave foi removida e `0` quando a chave já não existia. Entradas inválidas retornam erro sem alterar o armazenamento.

**Casos de borda**

O contrato deve cobrir remoção de chave inexistente, remoções repetidas e argumentos ausentes ou excedentes.

**Invariantes**

Nenhuma chave diferente daquela informada é modificada. Depois de uma remoção bem-sucedida, `GET` deve indicar ausência e `EXISTS` deve retornar `0`.

**Critérios de aceitação**

Remover uma chave existente retorna `1` e elimina a associação. Remover uma chave inexistente retorna `0`, sem erro. Uma segunda remoção da mesma chave retorna `0`.

### RF-04 — EXISTS chave

**Descrição**

Informa se a chave está presente no armazenamento.

**Entrada**

Recebe exatamente uma chave.

**Pré-condições**

A chave deve respeitar o tipo e os limites definidos pelo protocolo.

**Pós-condições**

O armazenamento não é alterado.

**Resposta**

Retorna `1` se a chave existir e `0` se não existir. Entradas inválidas retornam erro.

**Casos de borda**

Uma chave com valor vazio continua sendo considerada existente. O contrato também deve cobrir ausência e excesso de argumentos.

**Invariantes**

O comando nunca cria, remove ou altera chaves. Após um `SET` bem-sucedido, retorna `1`; após um `DEL` que removeu a chave, retorna `0`.

**Critérios de aceitação**

Chaves existentes retornam `1`, inclusive quando armazenam valor vazio. Chaves inexistentes retornam `0`. A execução não modifica o armazenamento.

## Requisitos não funcionais

### Comunicação
A comunicação entre cliente e servidor será feita por TCP. O protocolo entrega um fluxo ordenado de bytes dentro de cada conexão, detecta perdas durante a transmissão e realiza retransmissões quando necessário. Isso não determina, por si só, a ordem global de execução dos comandos: o mini-redis será responsável por processar corretamente as requisições recebidas de cada cliente.

As conexões poderão permanecer abertas para evitar o custo de estabelecer uma nova conexão a cada comando.

Como o TCP não preserva fronteiras entre mensagens, o mini-redis precisará implementar framing para identificar onde cada comando começa e termina, inclusive quando uma mensagem chegar fragmentada ou quando várias mensagens chegarem juntas.

### Concorrência
O TCP permite que tenhamos diversas conexões simultâneas, mas quem vai precisar cuidar da concorrência delas é o nosso querido homemade Redis.
Evidentemente que queremos conseguir lidar com requisições simultâneas, a pergunta que fica é como fazer isso. A primeira vista uma resposta trivial seria colocar uma fila antes de Redis, mas isso não faz de fato que estejamos processando coisas de forma paralela, nem que estamos tendo uma latência baixa entre as respostas. O que o Redis usa de fato, e que podemos pensar em como implementar aqui, é um multiplexador (MUX).
A ideia é que o Redis mantém conexão aberta com diversos clientes, e o sistema operacional avisa o Redis quando algum socket está pronto para leitura ou escrita. Mesmo com só um thread alocado, o que não permite que realizemos paralelismo, conseguimos administrar diversas conexões abertas simultaneamente

### Persistência
A v1 armazenará chaves e valores exclusivamente em memória. Todo o estado será perdido quando o processo for encerrado.

O mini-redis não salvará o cache em arquivos nem tentará sincronizá-lo com PostgreSQL ou outro banco de dados durante o desligamento. Aplicações que utilizarem o mini-redis continuarão responsáveis por manter sua própria fonte de dados persistente.

Persistência poderá ser estudada em uma fase futura e exigirá uma nova decisão técnica. O contexto, as alternativas e as consequências dessa escolha estão registrados em `docs/engineering-journal.md`.

### Performance
O Mini Redis deverá ser desenvolvido buscando baixa latência na execução de operações sobre dados armazenados em memória.

**Ambiente de referência:**
- Cliente e servidor executando localmente.
- Comunicação via TCP (localhost).
- Conexões persistentes.
- Valores de 128 bytes.
- 10.000 chaves previamente carregadas.
- Workload de 80% GET e 20% SET.
- Sem persistência em disco durante os testes iniciais.

**Metas iniciais (provisórias):**
- Latência p50: ≤ 1 ms.
- Latência p99: ≤ 5 ms.
- Throughput: ≥ 5.000 operações/segundo.
- Suporte a 50 clientes simultâneos.

As metas de latência e throughput serão avaliadas no cenário de 50 clientes e 100.000 operações.

**Critérios de avaliação:**
- Medir latência end-to-end no cliente.
- Registrar p50, p95, p99 e throughput.
- Executar cinco rodadas de cada cenário.
- Documentar hardware, linguagem e ambiente de execução.
- Comparar resultados com uma instância do Redis original sob condições equivalentes.

**Observação:** os valores são objetivos experimentais, não requisitos bloqueantes da primeira versão. Serão revisados após a obtenção dos primeiros benchmarks.

## O que está fora de escopo
- Persistência em disco ou sincronização com um banco de dados externo
- Replicação entre servidores
- Clusterização
- Pub/Sub e mensageria
- Autenticação e autorização
- Estruturas complexas como listas e sorted sets
- Compatibilidade completa com todas as funcionalidades do Redis

## Exercício educacional versus software de produção

### Pergunta de pesquisa

Quais são os trade-offs entre implementar um exercício e projetar software de produção?

### Resposta

Um exercício educacional é otimizado para aprendizado, enquanto um software de produção é otimizado para resolver um problema real com segurança, confiabilidade e custo operacional aceitável.

No mini-redis, implementar manualmente partes como protocolo TCP, framing, armazenamento em memória e controle de concorrência aumenta o valor educacional do projeto. Em um sistema de produção, provavelmente seria mais adequado utilizar bibliotecas e soluções já testadas, porque uma implementação manual aumenta o risco de erros, vulnerabilidades e comportamentos inesperados.

Outra diferença é o escopo. Como exercício, o mini-redis pode suportar apenas os comandos `SET`, `GET`, `DEL` e `EXISTS`, armazenar somente strings e perder todos os dados quando o processo for encerrado. Essas limitações permitem estudar os conceitos fundamentais sem introduzir prematuramente persistência, replicação, autenticação e clusterização.

Em produção, essas limitações precisariam ser avaliadas de acordo com os requisitos do negócio. Poderiam ser necessários mecanismos de recuperação, limites de memória, autenticação, criptografia, métricas, logs, backups, alta disponibilidade e compatibilidade entre versões.

Os critérios de qualidade também são diferentes. Em um exercício, uma implementação pode ser considerada bem-sucedida quando seu autor consegue explicar as decisões, os casos de falha e as alternativas consideradas. Em produção, compreender a implementação continua sendo importante, mas também é necessário demonstrar seu comportamento por meio de testes, monitoramento, objetivos de disponibilidade e procedimentos operacionais.

O fato de ser um exercício não significa que os contratos possam ser ambíguos. Requisitos claros, testes e tratamento de erros continuam sendo necessários, pois fazem parte do aprendizado. A diferença é que o projeto pode escolher conscientemente não resolver determinados problemas, desde que essas limitações sejam documentadas.

### Decisão aplicada ao mini-redis

A primeira versão será tratada como uma implementação educacional, e não como uma alternativa ao Redis para uso em produção.

Por isso:

- As funcionalidades serão implementadas manualmente sempre que isso contribuir para o aprendizado.
- A versão inicial terá somente os comandos `SET`, `GET`, `DEL` e `EXISTS`.
- Chaves e valores serão armazenados apenas em memória.
- O estado será perdido quando o processo for encerrado.
- Persistência, replicação, clusterização, autenticação e estruturas complexas ficarão fora do escopo.
- Os contratos dos comandos, os casos de erro e a concorrência serão definidos explicitamente.
- As limitações encontradas durante o desenvolvimento serão registradas no journal.

### Trade-off aceito

Ao escolher uma implementação manual e um escopo reduzido, aceito que o mini-redis terá menos funcionalidades, desempenho potencialmente inferior e menor robustez que o Redis real.

Em troca, obtenho maior compreensão sobre comunicação TCP, protocolos, estruturas de dados, concorrência, memória e decisões de arquitetura.

Caso o projeto evolua para uso real, seus requisitos deverão ser reavaliados. As decisões tomadas para maximizar o aprendizado não devem ser automaticamente consideradas adequadas para produção.