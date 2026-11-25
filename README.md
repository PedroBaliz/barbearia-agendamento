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
docs/   artefatos do projeto (BPMN, modelo de dados, UML, ADRs, protótipos)
src/    código-fonte da aplicação
tests/  testes automatizados
```

## Stack

Python 3.12 · Django 5 · Bootstrap 5 · PostgreSQL (SQLite em desenvolvimento) · pytest · GitHub Actions · Railway.
Justificativa em [docs/adr/0001-stack-tecnologica.md](docs/adr/0001-stack-tecnologica.md).

## Documentação

- [Modelo de dados](docs/modelo-de-dados.md) — diagrama ER, dicionário de dados e regras de negócio
- [Decisões de arquitetura (ADRs)](docs/adr/)

## Como rodar

> Instruções entram aqui junto com o primeiro código (IT2).

## Equipe

Equipe de 3 integrantes — papéis definidos no plano de gestão (`docs/`).

## Iterações

| Iteração | Foco |
|---|---|
| IT1 | Jornada e planejamento — processo, requisitos, modelo de dados, protótipo |
| IT2 | Construção e qualidade — MVP funcionando, testes, Kanban em uso |
| IT3 | Entrega e sustentação — release, ADRs, indicadores, lições aprendidas |
