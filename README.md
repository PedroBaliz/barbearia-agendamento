# Barbearia Agendamento

Sistema web de agendamento para barbearias — Projeto Integrador Ciclo 2 de Engenharia de Software (CEUB, 2026/2).

## Problema

Barbearias pequenas controlam horários por WhatsApp ou caderno, o que gera conflitos de agenda, faltas e perda de clientes. O sistema permite que o cliente veja horários livres e agende sozinho, e que o barbeiro gerencie a própria agenda.

## Funcionalidades principais (MVP — Must have)

- Cadastro e login de clientes e barbeiros
- Cadastro de serviços (nome, preço, duração)
- Configuração do horário de funcionamento da barbearia
- Consulta de horários disponíveis e agendamento
- Cancelamento de agendamento
- Agenda do dia do barbeiro

O backlog completo (18 requisitos, priorizados por MoSCoW) está no GitHub Projects do repositório.

## Estrutura do repositório

```
docs/          artefatos do projeto (BPMN, modelo de dados, UML, ADRs, protótipo, gestão)
src/config/    configurações do Django (settings, urls)
src/contas/    usuários (login por e-mail, papéis cliente/barbeiro/admin)
src/core/      páginas gerais e healthcheck
src/templates/ layout base
tests/         testes automatizados (pytest)
```

## Stack

Python 3.12 · Django 5 · Bootstrap 5 · PostgreSQL (SQLite em desenvolvimento) · pytest · GitHub Actions · Vercel.
Justificativa em [ADR 0001](docs/adr/0001-stack-tecnologica.md) e [ADR 0002 (Vercel)](docs/adr/0002-hospedagem-vercel.md).

## Documentação

- [Entrega da IT1 – Jornada e planejamento](docs/entregas/IT1-jornada-e-planejamento.md) — resumo da fase e mapa dos artefatos
- [Plano de gestão A01–A12](docs/gestao/) — TAP, EAP, cronograma, RACI, riscos (Kit de Artefatos preenchido)
- [BPMN do processo (To-Be)](docs/bpmn/)
- [Modelo de desenvolvimento](docs/modelo-de-desenvolvimento.md) — Scrum enxuto + Kanban, Definição de Pronto
- [Modelo de dados](docs/modelo-de-dados.md) — diagrama ER, dicionário de dados e regras de negócio
- [Protótipo de interface](docs/prototipo/)
- [Decisões de arquitetura (ADRs)](docs/adr/)
- [CHANGELOG](CHANGELOG.md)

## Como rodar

Pré-requisito: **Python 3.12**.

```bash
# 1. Ambiente virtual e dependências
python -m venv .venv
source .venv/bin/activate        # Windows (Git Bash): source .venv/Scripts/activate
pip install -r requirements-dev.txt

# 2. Variáveis de ambiente
cp .env.example .env             # depois preencha SECRET_KEY (o próprio arquivo mostra como gerar)

# 3. Banco e servidor
python src/manage.py migrate
python src/manage.py createsuperuser
python src/manage.py runserver
```

Acesse <http://127.0.0.1:8000>. O painel administrativo fica em `/admin` e o healthcheck em `/saude/`.

Sem `DATABASE_URL`, o projeto usa SQLite local. Em produção, o PostgreSQL vem da Vercel Storage (Neon).

## Testes e qualidade

```bash
pytest                 # testes + cobertura (falha abaixo de 60%, RNF04)
ruff check .           # lint
ruff format .          # formatação
```

O GitHub Actions roda lint, checagem de migrations e testes contra PostgreSQL a cada push e pull request (`.github/workflows/ci.yml`).

## Deploy

**Vercel** ([ADR 0002](docs/adr/0002-hospedagem-vercel.md)). O Django roda como função serverless (`api/index.py` + `vercel.json`) e o banco é um PostgreSQL da Vercel Storage (Neon).

1. Na Vercel, importe o repositório e, em **Storage**, crie um banco **Neon** ligado ao projeto. Isso define `DATABASE_URL`.
2. Em **Settings → Environment Variables**, defina `SECRET_KEY` e `DEBUG=false`. Os domínios `*.vercel.app` já são aceitos automaticamente.
3. No GitHub (**Settings → Secrets → Actions**), crie `DATABASE_URL_PRODUCAO` (a mesma URL do Neon) e `SECRET_KEY_PRODUCAO`. A cada merge na `main`, o job `migrations-producao` aplica as migrations.

Cada push na `main` publica em produção, e cada pull request ganha uma URL de preview.

## Equipe

Equipe de 3 integrantes — papéis definidos no plano de gestão (`docs/`).

## Iterações

| Iteração | Foco |
|---|---|
| IT1 | Jornada e planejamento — processo, requisitos, modelo de dados, protótipo |
| IT2 | Construção e qualidade — MVP funcionando, testes, Kanban em uso |
| IT3 | Entrega e sustentação — release, ADRs, indicadores, lições aprendidas |
