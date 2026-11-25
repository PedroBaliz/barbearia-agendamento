# ADR 0001 – Stack tecnológica

- **Status:** aceita
- **Data:** 2026-11-25
- **Critérios relacionados:** C3 (Projeto do sistema), C4 (Ambiente e implementação), C5 (Qualidade e testes)

## Contexto

Precisamos entregar um MVP web de agendamento para barbearias até o fim do Ciclo 2 (dezembro de 2026), com uma equipe de 3 estudantes. A rubrica pede:

- ambiente reproduzível por terceiros (C4);
- testes automatizados rodando em pipeline, com cobertura medida (C5) — a rubrica cita **pytest** e **GitHub Actions**;
- painel administrativo para ver agendamentos, gerenciar barbeiros e configurar o horário de funcionamento (RF16, RF17, RF18);
- autenticação com três papéis: cliente, barbeiro e admin (RF01–RF04).

O prazo é curto, então a stack precisa trazer pronto o que não é o diferencial do projeto (login, admin, migrations), para o tempo ir para as regras de agendamento.

## Decisão

| Camada | Escolha |
|---|---|
| Linguagem | Python 3.12 |
| Framework web | Django 5 (monolito, páginas renderizadas no servidor com templates) |
| Interface | Templates do Django + Bootstrap 5 (responsivo, sem build de front-end) |
| Banco de dados | SQLite em desenvolvimento; PostgreSQL em produção |
| Testes | pytest + pytest-django + pytest-cov |
| CI | GitHub Actions (testes e cobertura a cada push e pull request) |
| Deploy | Railway (PaaS com PostgreSQL gerenciado) |
| Configuração | Variáveis de ambiente (`.env`, com `.env.example` versionado) |

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| **Flask** | Mais leve, mas login, admin, formulários e migrations teriam de ser montados à mão com extensões. Mais código para manter no mesmo prazo. |
| **FastAPI + React** | Duas aplicações (API e SPA), dois ambientes e dois pipelines. Mais complexidade do que o MVP precisa, e testes de front-end à parte. |
| **Node.js (Express/Nest)** | A rubrica e as aulas usam Python e pytest; trocar a linguagem aumenta a curva da equipe sem ganho para o problema. |

## Consequências

**Positivas**

- O **Django Admin** atende RF16, RF17 e RF18 com pouca configuração, liberando tempo para RF05/RF06 (cálculo de horários livres), que é o núcleo do sistema.
- Autenticação, sessões, proteção CSRF e hash de senha já vêm prontos (apoia os requisitos não funcionais de segurança).
- O ORM e as migrations deixam o modelo de dados versionado no repositório, junto com o código.
- pytest-django permite testar regras de negócio e views no mesmo padrão citado na rubrica.

**Negativas / riscos**

- Interface renderizada no servidor é menos interativa que uma SPA. Mitigação: a tela de horários pode usar um pouco de JavaScript (ou HTMX) se for necessário.
- SQLite e PostgreSQL se comportam diferente em alguns casos (concorrência, tipos). Mitigação: o CI pode rodar os testes contra PostgreSQL quando o MVP estiver estável.

## Referências

- SOMMERVILLE, I. *Engenharia de Software*. 10. ed. Pearson, 2018 — reúso de frameworks e escolha de plataforma como decisão de arquitetura.
- NYGARD, M. *Documenting Architecture Decisions*, 2011 — formato de ADR usado neste documento.
