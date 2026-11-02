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

## Contratos para cada requisito funcional

Listando os requisitos:
- SET chave valor -> cria e armazena um valor associado a uma chave
- GET chave -> recupera o valor associado à chave
- DEL chave -> remove a chave existente
- EXISTS chave -> verifica se uma chave existe

### RF-01 — SET chave valor

1. Descrição
O comando tem a função de criar uma relação entre uma chave e um valor

2. Entrada
Recebe valor

| Parâmetro | Tipo | Obrigatório | Descrição |
|valor|string|true|valor a ser associado a uma chave|
| | | | |

3. Pré-condições
- valor não pode ser nulo, 
- valor deve ser uma string, -
- não deve existir uma chave já atribuída a aquele valor 

4. Pós-condições
- caso o valor não tenha uma chave associada, deve retornar uma tupla {chave: valor}
- caso o valor já tenha uma chave associada, deve retornar um erro

5. Resposta
- **Sucesso:**: {chave:valor}
- **Falha:**: Error

6. Casos de borda
- Valor de `valor` é inválido
- Já existe uma chave atribuída a `valor`

7. Invariantes
- O valor de `valor` não deve ser alterado
- A chave atribuída deve ser única

8. Critérios de aceitação
- [ ] O `valor` de input é uma string, retorna erro caso seja outro tipo de dado
- [ ] O retorno é uma tupla `{chave: valor}`
- [ ] Caso já existe uma chave atrelada ao `valor`, o retorno é um erro explícito: "Já existe chave atrelada a esse valor"

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