# Modelo de desenvolvimento

**Decisão:** desenvolvimento **iterativo e incremental**, com práticas do **Scrum** (sprints curtas, backlog priorizado, revisão e retrospectiva) e um **quadro Kanban** para controlar o fluxo do dia a dia. Na prática, um Scrum enxuto com quadro Kanban (às vezes chamado de *Scrumban*).

- **Critério relacionado:** C2 (modelo de desenvolvimento justificado) e C6 (quadro coerente com o repositório)
- **Data:** 2026-11-25

## Contexto

| Fator | Situação do projeto |
|---|---|
| Prazo | Um ciclo (out–dez 2026), dividido pelo professor em 3 iterações com entrega e apresentação |
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
| Sprint | **1 semana**; cada iteração do professor tem de 3 a 4 sprints | Sprints de 2 a 4 semanas não caberiam nas iterações |
| Sprint Planning | 20 min no início da semana: issues saem de *Todo* para a sprint | Reunião curta, cabe na rotina |
| Daily | **Assíncrona** no canal da equipe: fiz / vou fazer / travado | Equipe não se encontra todo dia |
| Sprint Review | Na própria apresentação de cada iteração e numa demo semanal curta | — |
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
| IT1 – Jornada e planejamento | — | Artefatos: BPMN, requisitos, modelo de dados, protótipo, TAP/EAP/riscos |
| IT2 – Construção e qualidade | 3 a 4 semanais | Must do backlog (RF01–07, 09, 12, 13, 18), testes e pipeline |
| IT3 – Entrega e sustentação | 2 a 3 semanais | Should/Could se houver folga, release, README, ADRs, lições aprendidas |

O progresso é medido pelo **burndown** de issues por iteração (C6).

## Referências

- SOMMERVILLE, I. *Engenharia de Software*. 10. ed. Pearson, 2018 — capítulos 2 (processos de software, desenvolvimento incremental) e 3 (métodos ágeis).
- SCHWABER, K.; SUTHERLAND, J. *The Scrum Guide*, 2020. <https://scrumguides.org>
- ANDERSON, D. J. *Kanban: Successful Evolutionary Change for Your Technology Business*. Blue Hole Press, 2010 — limite de WIP e sistema puxado.
