# Changelog

## 1.0.0 - 2026-11-26

Primeira versão publicada.

### Gates

- **Orçamento** — teto de tokens declarado, estimativa antes de começar, parada em 70%
  (compactar) e 100% (parar e reportar).
- **Prova** — "pronto" é um comando que rodou e saiu com código 0. `verify` gera `proof.md`;
  `report` recusa concluir com critério vermelho.

### Freios

- Loop: 2ª edição idêntica no mesmo arquivo, ou 3ª falha do mesmo comando.
- Instruções: precedência entre `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, `GEMINI.md`,
  `.github/copilot-instructions.md`, com regra de conflito explícita.
- Escopo: só arquivos que os critérios exigem.
- Leitura: nenhum arquivo lido duas vezes.

### Também nesta versão

- `state.md` reescrito a cada passo, portátil entre harnesses.
- Contrato de retorno de subagente: ≤40 linhas com `file:line`, nunca transcrição.
- Revisão determinística (lint, tipos, testes) em vez de painel de revisores.
- Referências locais carregadas sob demanda, sem dependência de skills externas.
- Três tarefas-ouro executáveis em `golden/`.
