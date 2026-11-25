# Changelog

Mudanças relevantes de cada versão. O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e as versões seguem o [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [0.2.0] – 2026-11-25 · Ambiente, CI e deploy

Primeira versão com código: o ambiente completo, com o site no ar em <https://barbearia-agendamento-phi.vercel.app>. Guia: [docs/ambiente.md](docs/ambiente.md). Fecha a issue #34.

### Adicionado

- Projeto Django 5.2 em `src/` (`config`, `contas`, `core`), configurado por variáveis de ambiente (`.env.example`).
- Usuário customizado com login por e-mail e papéis cliente, barbeiro e admin (tabela `usuario` do modelo de dados).
- Senhas com bcrypt (RNF02), página inicial responsiva no visual do protótipo (RNF03) e healthcheck `/saude/`.
- Testes com pytest + pytest-django e cobertura mínima de 60% (RNF04); lint e formatação com ruff.
- GitHub Actions: lint, checagem de migrations e testes contra PostgreSQL; job que aplica as migrations em produção a cada merge na `main`.
- Deploy na Vercel com PostgreSQL Neon; preview automático por pull request.
- ADR 0002 – Hospedagem na Vercel; guia `docs/ambiente.md`.

### Alterado

- Hospedagem prevista no ADR 0001 (Railway) substituída pela Vercel (mudança M04 do plano de gestão).
- Cronograma reajustado para a apresentação única em 07/12/2026 (mudança M03).

## [0.1.0] – 2026-11-25 · IT1 – Jornada e planejamento

Primeira versão. Contém só documentação, sem código ainda. Resumo da fase: [docs/entregas/IT1-jornada-e-planejamento.md](docs/entregas/IT1-jornada-e-planejamento.md).

### Adicionado

- Estrutura do repositório (`docs/`, `src/`, `tests/`), README e `.gitignore`.
- Backlog com 18 requisitos funcionais como issues (#1–#18), priorizados por MoSCoW, com critérios de aceitação *Dado/Quando/Então*, no GitHub Projects.
- BPMN To-Be do processo de agendamento (`docs/bpmn/`), em BPMN 2.0, com a v1 original e o registro das correções.
- ADR 0001 – Stack tecnológica: Python 3.12 + Django 5 + PostgreSQL, pytest e GitHub Actions.
- Modelo de dados: diagrama ER, dicionário de dados e regras de negócio.
- Modelo de desenvolvimento: iterativo e incremental, Scrum enxuto + Kanban, Definição de Pronto.
- Protótipo de interface (`docs/prototipo/`).

[0.2.0]: https://github.com/PedroBaliz/barbearia-agendamento/releases/tag/v0.2.0
[0.1.0]: https://github.com/PedroBaliz/barbearia-agendamento/releases/tag/v0.1.0
