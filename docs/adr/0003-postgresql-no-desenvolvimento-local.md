# ADR 0003 – PostgreSQL também no desenvolvimento local

- **Status:** aceita
- **Data:** 2026-11-26
- **Complementa:** o [ADR 0001](0001-stack-tecnologica.md), que previa "PostgreSQL (SQLite em desenvolvimento)"
- **Critérios relacionados:** C4 (ambiente e implementação), C5 (qualidade e testes)
- **Issue:** #60

## Contexto

Até a v0.4.0, os três ambientes do projeto usavam bancos diferentes:

| Ambiente | Banco |
|---|---|
| Máquina de quem desenvolve | SQLite (`src/db.sqlite3`) |
| CI (GitHub Actions) | PostgreSQL 16 |
| Produção (Vercel) | PostgreSQL Neon |

Isso funcionou bem enquanto o código só fazia cadastros simples. A v0.5.0, porém, traz o **RF06 (agendar horário)**, com a regra mais sensível do sistema: dois clientes não podem reservar o mesmo horário do mesmo barbeiro ao mesmo tempo (regra 1 do [modelo de dados](../modelo-de-dados.md)).

A proteção contra essa corrida usa uma transação com **trava de linha** (`select_for_update`) antes de gravar o agendamento. É exatamente aqui que os dois bancos se comportam de forma diferente:

- **SQLite:** não tem trava de linha. O Django simplesmente ignora o `select_for_update`, e o SQLite trava o banco inteiro em cada escrita. Um teste de concorrência passa mesmo que a proteção esteja errada.
- **PostgreSQL:** trava só as linhas envolvidas e deixa o resto do banco livre, exatamente como acontece em produção.

Com SQLite local, um erro de concorrência só apareceria no CI, a cada push, ou pior, em produção.

## Decisão

Usar **PostgreSQL também no desenvolvimento local**, configurado pela mesma variável `DATABASE_URL` que o CI e a produção já usam:

```
DATABASE_URL=postgresql://barbearia:barbearia@localhost:5432/barbearia
```

- O banco e o usuário se chamam `barbearia`, os mesmos nomes do CI (`.github/workflows/ci.yml`).
- O usuário `barbearia` não é administrador: é dono só do banco `barbearia` e tem `CREATEDB`, porque o pytest cria e apaga o banco temporário `test_barbearia` a cada rodada.
- A senha do administrador `postgres` não fica em arquivo nenhum. Ela só é usada uma vez, para criar o usuário do app.
- O **SQLite continua funcionando** como alternativa: com `DATABASE_URL` vazia, o projeto volta para o `src/db.sqlite3`. Nenhuma linha de código mudou.

O passo a passo está em [docs/ambiente.md](../ambiente.md#postgresql-local-recomendado).

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Continuar com SQLite e confiar no CI | Cada erro de concorrência custaria um push e uma espera de CI. No RF06, que é o núcleo do sistema, o ciclo de correção ficaria lento demais para o prazo de 03/12 |
| PostgreSQL em Docker | Daria a mesma versão do CI (16), mas exigiria instalar e manter o Docker. A máquina de desenvolvimento já tinha o PostgreSQL 18 instalado |
| Usar o banco Neon de produção também no desenvolvimento | Risco de apagar ou sujar dados reais, além de depender de internet para rodar os testes |

## Consequências

- **Positivas:**
  - os três ambientes usam o mesmo tipo de banco;
  - os testes do RF06 em diante mostram localmente o comportamento real de transações e travas;
  - as `CheckConstraint` (preço, duração, horário) são validadas pelo mesmo motor de produção.
- **Negativas:**
  - quem for desenvolver precisa instalar o PostgreSQL e criar o usuário e o banco, o que dá uns 5 minutos;
  - a versão local (18) é diferente da do CI (16). O Django 5.2 suporta as duas e o código não usa nada específico de versão; qualquer diferença aparece no CI.
- **Verificação (26/11/2026):** com o PostgreSQL 18 local, as 22 migrations foram aplicadas e os 114 testes passaram, com cobertura de 96%.
