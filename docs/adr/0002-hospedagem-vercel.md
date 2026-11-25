# ADR 0002 – Hospedagem na Vercel

- **Status:** aceita
- **Data:** 2026-11-25
- **Substitui:** a linha "Deploy" do [ADR 0001](0001-stack-tecnologica.md), que previa o Railway
- **Critérios relacionados:** C4 (ambiente e implementação), C7 (sustentação)
- **Mudança registrada:** M04 no A10 do plano de gestão

## Contexto

O ADR 0001 escolheu o Railway para o deploy. Antes do primeiro deploy, a equipe decidiu hospedar tudo na **Vercel**, aplicação e banco, num único painel. O requisito continua o RNF05: o sistema precisa estar disponível em link público antes da apresentação de 07/12/2026.

A Vercel roda Python como **funções serverless**. Para um Django isso muda três pontos em relação a um servidor tradicional:

1. **Disco temporário:** nada gravado em disco sobrevive entre requisições, então SQLite não serve em produção.
2. **Sem etapa de pré-deploy:** não há um passo garantido para rodar `migrate` ou `collectstatic` antes de publicar.
3. **Sem processo contínuo:** cada requisição pode abrir uma instância nova, o que torna conexões persistentes com o banco inúteis.

## Decisão

| Ponto | Como fica |
|---|---|
| Aplicação | Função Python da Vercel: `api/index.py` expõe o WSGI do Django; `vercel.json` manda todas as rotas para ela |
| Banco | PostgreSQL pela **Vercel Storage (Neon)**, que injeta `DATABASE_URL` no projeto |
| Arquivos estáticos | WhiteNoise servindo direto das pastas dos apps (`WHITENOISE_USE_FINDERS`), sem `collectstatic` |
| Migrations | Job `migrations-producao` no GitHub Actions, a cada merge na `main` (secret `DATABASE_URL_PRODUCAO`) |
| Conexões | `CONN_MAX_AGE = 0` na Vercel |
| Proteções | Sem `DATABASE_URL` na Vercel, o app se recusa a subir; domínios `*.vercel.app` liberados automaticamente |
| Previews | Cada pull request ganha uma URL de preview da Vercel |

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Railway (ADR 0001) | Servidor tradicional, mais simples para Django, mas a equipe preferiu concentrar tudo na Vercel |
| Render / Fly.io | Mesmo motivo; mais uma conta e mais um painel para a equipe aprender |

## Consequências

**Positivas**

- Deploy automático a cada push, com URL de preview por PR, o que ajuda na revisão (risco R2) e no C4.
- Aplicação e banco no mesmo painel, com HTTPS automático.

**Negativas / riscos**

- **Cold start:** a primeira requisição depois de um tempo parado é mais lenta. Isso pode afetar o RNF01 (menos de 3 s). Mitigação: abrir o site alguns minutos antes da apresentação.
- **Migrations fora do deploy:** se o job do GitHub Actions falhar, o código novo pode rodar com o banco antigo. Mitigação: o job depende dos testes e roda logo após o merge. A verificação faz parte da Definição de Pronto.
- **Limites do plano gratuito** da Vercel e do Neon (tempo de função, armazenamento). São suficientes para o MVP e ficam monitorados no risco R5.
- **Uploads de arquivo** não podem ir para o disco. Hoje o sistema não tem upload. Se tiver no futuro, o armazenamento vai precisar de Vercel Blob.

## Referências

- Vercel. *Python Runtime*. <https://vercel.com/docs/functions/runtimes/python>
- WhiteNoise. *Using WhiteNoise with Django*. <https://whitenoise.readthedocs.io/en/stable/django.html>
