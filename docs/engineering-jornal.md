# Engineering jornal

## 03/11/2026 -> Issue 1
Registrando algumas decisões e aprendizados durante a elaboração conceitual do `mini-redis`:
- Redis é um banco chave-valor, por isso funciona tão bem para o caso de aplicaçãod e camada cache
- Para administrar diversas conexões paralelas com o banco, precisamos não só de um protocolo de comunicação adequado (no caso o TCP), mas também alguma forma de administrar as diversas requisições mesmo que não exista a capacidade de paralelismo, no caso usando um MUX