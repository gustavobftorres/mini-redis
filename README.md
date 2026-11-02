# mini-redis
A from-scratch Redis-inspired key-value server built to study networking, storage, concurrency and reliability.

# Perguntas e respostas (Issue 1)

## O que é o Redis antes de mais nada?
O Redis é uma espécie de banco de dados, que usa uma relação chave-valor para fazer o armazenamento de informações. O grande ponto do Redis é que ele é bem rápido, por conta da estrutura chave-valor (se eu sei a chave, faço um busca em O(1)), então na prática a comunidade usa o serviço para administrar cache majoritariamente. Isso faz sentido, a partir do momento que eu realizo um busca no banco de dados e julgo ela como reccorente, ou seja, entendo que vou ir atrás desse mesmo dado outras vezes, por definição faz sentido ter uma estrutura de cache na aplicação, onde para aquele conjunto de dados eu linko uma chave. A partir do momento em que o cache está preenchido e válido, eu paro de bater no banco de dados e bato direto no Redis via chave.

O Redis trabalha com um sistema de mensegeria, então eu consigo fazer diversas pessoas ouvirem uma mesma mensagem. O processo de replication é built-in (algo que vamos precisar criar também eu imagino)

O Redis utiliza armazenamento em memória, que se diferem basicamente na volatilidade, os dados em memória morrem quando o PC é desligado, enquanto o armazenamento em disco é persistente. Se pensarmos no objetivo de cache, não faz sentido armazenar os dados cacheados em disco, então o fato do Redis utilizar armazenamento em memória melhora ainda mais a situação. No caso os dados armazenados no Redis existem enquanto o serviço estiver de pé, se derrubamos o Redis (ou o Docker que está mantendo o Redis de pé) os dados não persistem.

A ideia de implementar na mão algo dessa linha é voltar a aprender sobre as questões mais estruturais da engenharia de software, seja voltar a discutir sobre protocolos de comunicação, uso de memória, tempo computacional, perguntas que desenvolvem a senioridade.

## Objetivos do projeto
Realizar uma implementação nativa inspirada no Redis, recriando as principais funcionalidades do serviço de forma manual. Queremos implementar a lógica chave-valor, o uso de memória, protocolos de comunicação, persistência, entre outros atributos técnicos

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
→ true

DEL usuario:1
GET usuario:1
→ chave inexistente
```

em uma sessão posterior vou definir com mais calma os contratos de cada requisito funcional

### Premissas comuns dos contratos

Na versão 1, chaves e valores são strings UTF-8. A chave é obrigatória, não pode ser vazia e diferencia letras maiúsculas de minúsculas. O valor pode ser uma string vazia.

Cada comando é executado atomicamente: nenhum outro cliente pode observar um estado intermediário da operação.

Comandos com quantidade incorreta de argumentos ou argumentos inválidos retornam um erro explícito e não alteram o armazenamento.

Os limites máximos de tamanho de chave e valor deverão ser definidos junto com o protocolo, antes da implementação.

### RF-01 — SET chave valor

**Descrição**

Associa o valor informado à chave informada.

**Entrada**

Recebe uma chave e um valor, ambos fornecidos pelo cliente.

**Pré-condições**

A chave e o valor devem respeitar os tipos e limites definidos pelo protocolo. A chave não pode ser vazia. Não é necessário que a chave seja inédita, e valores iguais podem ser associados a chaves diferentes.

**Pós-condições**

Se a chave não existia, uma nova associação é criada. Se já existia, seu valor anterior é substituído integralmente. Nenhuma outra chave é modificada.

**Resposta**

Em caso de sucesso, retorna uma confirmação `OK`. Se os argumentos forem inválidos, retorna um erro explícito e mantém o estado anterior.

**Casos de borda**

O contrato deve cobrir valor vazio, chave já existente, duas chaves com o mesmo valor, ausência de argumentos, argumentos excedentes e chave ou valor acima dos limites permitidos.

**Invariantes**

Existe no máximo um valor atual para cada chave. Um valor pode aparecer em várias chaves. Depois de uma resposta de sucesso, um `GET` da mesma chave deve devolver o novo valor.

**Critérios de aceitação**

Uma chave inexistente é criada. Uma chave existente é sobrescrita. Duas chaves podem armazenar o mesmo valor. Entradas inválidas produzem erro sem alterar o armazenamento.

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
A comunicação entre cliente e servidor será feita por meio de um protocolo TCP, que já é o mais coerente para uma aplicação que imita um Redis, como é isso que estamos fazendo aqui, seguiremos essa lógica. A pergunta que fica então é porque TCP é o mais adequado, vamos discorrer sobre algumas caracterísiticas do protocolo que corroboram com esse ponto:
- O TCP garante uma coordenação de transmissão dos bytes de acordo com o solicitado pelo cliente, então se eu envio uma sequência de comandos ao Redis, consigo garantir que eles vão ser executados na mesma ordem que eu enviei
- A lógica de checksum do TCP garante confiabilidade na transmissão dentro da rede, tentando recuperar os dados por restransmissão caso algo se perca no meio do caminho
- O TCP permite uma conexão persistente, então podemos manter um túnel entre Redis <-> TCP de forma contínua, economizando assim o custo computacional e a latência que seria abrir uma nova conexão a cada nova chamada ao banco

A grande questão na comunicação vai ser implementar um framing na recepção dos dados, pois o TCP vai enviando os bytes sem diferenciar o que é cada resposta, no sentido que não existe uma distinção ou pausa entre a resposta de duas requisições diferentes

### Concorrência
O TCP permite que tenhamos diversas conexões simultâneas, mas quem vai precisar cuidar da concorrência delas é o nosso querido homemade Redis.
Evidentemente que queremos conseguir lidar com requisições simultâneas, a pergunta que fica é como fazer isso. A primeira vista uma resposta trivial seria colocar uma fila antes de Redis, mas isso não faz de fato que estejamos processando coisas de forma paralela, nem que estamos tendo uma latência baixa entre as respostas. O que o Redis usa de fato, e que podemos pensar em como implementar aqui, é um multiplexador (MUX).
A ideia é que o Redis mantém conexão aberta com diversos clientes, e o sistema operacional avisa o Redis quando algum socket está pronto para leitura ou escrita. Mesmo com só um thread alocado, o que não permite que realizemos paralelismo, conseguimos administrar diversas conexões abertas simultaneamente

### Persistência
A ideia central do Redis é ser usado como sistema de cache pela velocidade que é fazer uma operação de leitura em um banco chave-valor. Mas a partir do momento que o serviço do Redis é derrubado, não há necessidade dele ser responsável pela persistência dos dados, até porque o Redis utiliza armazenamento de memória. A ideia então é que a priori a persistência não deve sobreviver ao encerramento do processo, o que entendo como lógico é ter uma camada de banco de dados estruturada (um PostgresSQL da vida) que vai garantir persistência, antes do nosso querido mini-redis ser derrubado, escrevemos no banco o que temos no cache alterado

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
- Replicação entre servidores
- Clusterização
- Autenticação e autorização
- Estruturas complexas como listas e sorted sets
- Compatibilidade completa com todas as funcionalidades do Redis