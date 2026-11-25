# Modelo de desenvolvimento

**Decisão:** desenvolvimento **iterativo e incremental**, com práticas do **Scrum** (sprints curtas, backlog priorizado, revisão e retrospectiva) e um **quadro Kanban** para controlar o fluxo do dia a dia. Na prática, um Scrum enxuto com quadro Kanban (às vezes chamado de *Scrumban*).

- **Critério relacionado:** C2 (modelo de desenvolvimento justificado) e C6 (quadro coerente com o repositório)
- **Data:** 2026-11-25

## Contexto

| Fator | Situação do projeto |
|---|---|
| Prazo | Um ciclo (out–dez 2026), com 3 iterações e **uma apresentação única em 07/12/2026** |
| Equipe | 3 estudantes, em tempo parcial, com outras disciplinas |
| Requisitos | 18 RF já levantados e priorizados (MoSCoW), mas detalhes de tela e regra vão mudar ao ver o MVP rodando |
| Cliente | Barbearia (usuário real) disponível para dar retorno pontual |
| Avaliação | Pede evidência contínua: commits regulares, Kanban atualizado, burndown |

## Por que iterativo e incremental

As três iterações do professor já impõem entregas parciais. Um modelo **cascata** exigiria fechar requisitos e projeto antes de codar e só mostraria o sistema no fim. O risco maior deste projeto, a regra de horários livres (RF05/RF06), só aparece quando o código roda. Com incrementos, o núcleo (Must) fica pronto primeiro e é testado cedo. Should e Could entram se houver tempo, sem comprometer o MVP.

## O que usamos do Scrum (e o que adaptamos)

| Prática | Como fazemos | Adaptação e motivo |
|---|---|---|
| Product Backlog | Issues RF01–RF18 no GitHub Projects, com MoSCoW e critérios de aceitação | — |
| Sprint | **Curta (3 a 4 dias)**; uma sprint por iteração | O prazo até 07/12 não comporta sprints de 2 a 4 semanas |
| Sprint Planning | 20 min no início de cada sprint: issues saem de *Todo* para a sprint | Reunião curta, cabe na rotina |
| Daily | **Assíncrona** no canal da equipe: fiz / vou fazer / travado | Equipe não se encontra todo dia |
| Sprint Review | Demo curta no fim de cada sprint (27/11, 03/12, 06/12); a apresentação final é em 07/12 | Só há uma apresentação formal |
| Retrospectiva | 15 min no fim da sprint; lições registradas no caderno | Alimenta as lições aprendidas (C7) |
| Papéis | Sem Scrum Master dedicado: o dono de *Gestão e Jornada* facilita as reuniões | 3 pessoas não comportam papéis exclusivos |

## O que usamos do Kanban

- **Quadro:** [GitHub Projects](https://github.com/users/PedroBaliz/projects/3), colunas *Todo → In Progress → Done*.
- **Limite de WIP:** no máximo **2 cards em In Progress por pessoa**. Termina antes de começar outro.
- **Puxar, não empurrar:** cada um puxa o próximo card de maior prioridade (Must antes de Should).
- **Quadro ligado ao código:** cada card vira branch e PR que fecha a issue (`Closes #N`). O card anda sozinho para *Done* no merge, então o quadro reflete o repositório.

## Definição de Pronto (Definition of Done)

Uma issue só vai para *Done* quando:

1. todos os critérios de aceitação da issue estão atendidos;
2. existe teste automatizado cobrindo a história, e a suíte passa no GitHub Actions;
3. o código entrou na `main` por pull request revisado por outro integrante;
4. a matriz de rastreabilidade (Ficha 3) foi atualizada.

## Como isso se encaixa nas iterações

| Iteração | Sprints | Foco |
|---|---|---|
| IT1 – Jornada e planejamento | até 27/11 | Artefatos: BPMN, requisitos, modelo de dados, protótipo, plano de gestão, UML |
| IT2 – Construção e qualidade | 30/11 → 03/12 | Must do backlog (RF01–07, 09, 12, 13, 18), testes e pipeline |
| IT3 – Entrega e sustentação | 04/12 → 06/12 | Should (RF08, 10, 11, 16, 17), deploy, release, README, ADRs, lições aprendidas |
| **Apresentação final** | **07/12** | Todas as iterações apresentadas juntas |

O progresso é medido pelo **burndown** de issues por iteração (C6).

## Referências

- SOMMERVILLE, I. *Engenharia de Software*. 10. ed. Pearson, 2018 — capítulos 2 (processos de software, desenvolvimento incremental) e 3 (métodos ágeis).
- SCHWABER, K.; SUTHERLAND, J. *The Scrum Guide*, 2020. <https://scrumguides.org>
- ANDERSON, D. J. *Kanban: Successful Evolutionary Change for Your Technology Business*. Blue Hole Press, 2010 — limite de WIP e sistema puxado.
