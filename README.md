# mini-redis
A from-scratch Redis-inspired key-value server built to study networking, storage, concurrency and reliability.

# Perguntas e respostas (Issue 1)

### O que é o Redis antes de mais nada?
O Redis é uma espécie de banco de dados, que usa uma relação chave-valor para fazer o armazenamento de informações. O grande ponto do Redis é que ele é bem rápido, por conta da estrutura chave-valor (se eu sei a chave, faço um busca em O(1)), então na prática a comunidade usa o serviço para administrar cache majoritariamente. Isso faz sentido, a partir do momento que eu realizo um busca no banco de dados e julgo ela como reccorente, ou seja, entendo que vou ir atrás desse mesmo dado outras vezes, por definição faz sentido ter uma estrutura de cache na aplicação, onde para aquele conjunto de dados eu linko uma chave. A partir do momento em que o cache está preenchido e válido, eu paro de bater no banco de dados e bato direto no Redis via chave.

O Redis trabalha com um sistema de mensegeria, então eu consigo fazer diversas pessoas ouvirem uma mesma mensagem. O processo de replication é built-in (algo que vamos precisar criar também eu imagino)

O Redis utiliza armazenamento em memória, que se diferem basicamente na volatilidade, os dados em memória morrem quando o PC é desligado, enquanto o armazenamento em disco é persistente. Se pensarmos no objetivo de cache, não faz sentido armazenar os dados cacheados em disco, então o fato do Redis utilizar armazenamento em memória melhora ainda mais a situação. No caso os dados armazenados no Redis existem enquanto o serviço estiver de pé, se derrubamos o Redis (ou o Docker que está mantendo o Redis de pé) os dados não persistem.

A ideia de implementar na mão algo dessa linha é voltar a aprender sobre as questões mais estruturais da engenharia de software, seja voltar a discutir sobre protocolos de comunicação, uso de memória, tempo computacional, perguntas que desenvolvem a senioridade.

### Objetivos do projeto
Realizar uma implementação nativa inspirada no Redis, recriando as principais funcionalidades do serviço de forma manual. Queremos implementar a lógica chave-valor, o uso de memória, protocolos de comunicação, persistência, entre outros atributos técnicos

### Requisitos funcionais
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

### 
