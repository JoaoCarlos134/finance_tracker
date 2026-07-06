# Finance Tracker — Instruções do Projeto

## Visão Geral
Aplicação web pessoal para análise e previsão de gastos financeiros, construída 
como projeto de portfólio para vagas de Data Science/ML em fintech.
Stack: FastAPI (backend) + React/Vite (frontend) + SQLite (migrando para 
Postgres antes do deploy).

## Política de Dados — REGRA CRÍTICA
- Ingestão de dados é **exclusivamente via arquivo** (CSV/Excel exportado 
  manualmente do extrato da XP Investimentos).
- **Nunca** implementar scraping do site/app da XP, login automatizado, ou 
  armazenamento de credenciais bancárias em qualquer forma (variável, .env, 
  script, etc.).
- Se no futuro for integrado Open Finance (ex: Pluggy, Belvo), isso deve ser 
  discutido e aprovado explicitamente antes de qualquer implementação — nunca 
  assumir que é aceitável.

## Estrutura de Diretórios Esperada
```
finance-tracker/
├── CLAUDE.md                  ← este arquivo
├── roadmap.txt                ← fonte de verdade do progresso (ver seção abaixo)
├── README.md
├── DESIGN.md                  ← sistema visual (tokens espelhados em theme.css)
├── run.ps1 / run.bat          ← sobe backend+frontend e abre o dashboard
├── .github/workflows/ci.yml   ← CI: ruff + pytest + build do frontend
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── db_types.py        ← MoneyCents (dinheiro = centavos inteiros/Decimal)
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routers/
│   │   │   ├── transactions.py    ← GET paginado, PATCH categoria
│   │   │   ├── ingestion.py       ← POST /ingest/csv
│   │   │   ├── categorization.py  ← POST /categorize/run
│   │   │   └── analytics.py       ← summary / monthly / by-category
│   │   └── services/
│   │       ├── ingest.py          ← parsing de CSV (puro)
│   │       └── categorize.py      ← regras de categorização (puro)
│   ├── requirements.txt
│   ├── pyproject.toml         ← config do ruff
│   └── tests/                 ← pytest (unit + API, fixtures/)
├── frontend/
│   └── src/                   ← components/, utils/, styles/theme.css
└── data/
    └── raw/                   ← CSVs exportados, nunca commitados (gitignore)
```

## Convenções de Código
- Python 3.11+, type hints em todas as funções públicas
- Funções de parsing/ingestão devem ser puras (sem efeitos colaterais de 
  framework), facilitando testes
- Nunca sobrescrever os arquivos CSV originais do usuário em data/raw/

## O Que NÃO Fazer
- Não integrar nenhuma API bancária ao vivo sem aprovação explícita
- Não hardcodar caminhos de arquivo
- Não marcar tarefas como concluídas no roadmap sem testar de fato

---

## Interação Obrigatória com o Roadmap

O arquivo `roadmap.txt` é a fonte de verdade do estado do projeto.
**Toda sessão de edição deve seguir este protocolo — sem exceções:**

### Antes de qualquer edição
1. Ler `roadmap.txt` na íntegra
2. Identificar em qual fase e item o trabalho se encaixa
3. Se o trabalho não estiver no roadmap, avaliar se deve ser adicionado antes 
   de começar

### Após concluir qualquer edição
1. Marcar os itens concluídos com `[x]` no roadmap
2. Se surgiu trabalho novo não previsto, adicioná-lo na fase correta com `[ ]`
3. Se uma decisão técnica relevante foi tomada, registrá-la na seção 
   "Decisões Técnicas Registradas" com data
4. Se uma fase inteira foi concluída, revisar se os itens da próxima fase 
   ainda fazem sentido
5. Atualizar a linha "Última atualização" no topo do roadmap.txt

### Regras de atualização
- Nunca marcar `[x]` em item que não foi de fato implementado e testado
- Itens em andamento usam `[~]` — nunca deixar em `[~]` ao final da sessão 
  sem justificativa na seção de Notas/Bloqueios
- Ao adicionar itens novos, inserir na fase correta (não no final genérico) 
  e descrever o que motivou a adição
- A seção de decisões técnicas registra o *porquê* da escolha, não só o quê 
  — isso é mandatório
