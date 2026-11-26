# Autopilot

Uma skill de desenvolvimento de ponta a ponta que roda sob um **teto de tokens declarado** e só
declara concluído o que passa por um **comando verificável**.

Agnóstica de harness: funciona em Claude Code, Codex, Cursor, Gemini CLI, Copilot ou qualquer
agente que consiga ler um arquivo, executar um comando e editar código.

## Por que existe

Skills de ponta a ponta costumam acertar o processo e errar o que mais incomoda quem usa
agentes de código. Levantamento em 1.420 comentários e issues
(APIs oficiais do Hacker News e do GitHub), com 240 linhas codificadas à mão:

| Reclamação | Ocorrências (base 89) |
| --- | --- |
| Queima tokens, custo, limites | 32 (36%) |
| Perde contexto, compacta, esquece | 14 (16%) |
| Declara "pronto" sem estar pronto | 8 (9%) |
| Ignora AGENTS.md / CLAUDE.md | 7 (8%) |
| Entra em loop | 7 (8%) |

Daí os dois gates e os quatro freios. Nada além disso.

## Instalação

Copie a pasta inteira (a skill depende de `scripts/` e `references/`).

| harness | destino |
| --- | --- |
| Claude Code | `~/.claude/skills/autopilot/` |
| Codex | `~/.codex/skills/autopilot/` |
| Cursor | `.cursor/rules/` ou a pasta de skills do projeto |
| Gemini CLI | `~/.gemini/skills/autopilot/` |
| Genérico | qualquer pasta que o agente leia como skill |

Recarregue a sessão depois de copiar.

## Uso

```
python scripts/ap.py init --goal "adicionar rate limit no /api" --ceiling 120000 --criteria criteria.json
python scripts/ap.py budget --estimate-files 8 --estimate-commands 4
python scripts/ap.py read --path src/api/client.py --note "cliente HTTP, 90 linhas"
python scripts/ap.py spend --tokens 9000 --note "passo 5"
python scripts/ap.py verify
python scripts/ap.py report
```

Peça o fluxo explicitamente: *"use autopilot para implementar e verificar"*, *"leve até o fim"*,
*"implementa e me mostra a prova"*.

## Os dois gates

1. **Orçamento** — teto declarado antes de tocar no código. Estimativa acima do teto = cortar
   escopo ou parar. Em 70%: escrever handoff e compactar. Em 100%: parar e reportar.
2. **Prova** — "pronto" é um comando que rodou e saiu com código 0. `ap.py report` recusa
   declarar conclusão com qualquer critério vermelho.

## Os quatro freios

| freio | comando | dispara em |
| --- | --- | --- |
| Orçamento | `ap.py spend` | 70% (compactar) e 100% (parar) |
| Loop | `ap.py guard diff` / `guard cmd` | 2ª edição idêntica / 3ª falha do mesmo comando |
| Instruções | `references/instruction-precedence.md` | conflito silencioso |
| Escopo | `SKILL.md` | arquivo tocado fora dos critérios |

## Estado que sobrevive à compactação

`.autopilot/state.md` é reescrito a cada passo (nunca anexado): objetivo, regras vigentes,
critérios, decisões, próximo passo, bloqueio. Qualquer harness lê e retoma daí — trocar de
ferramenta no meio da tarefa custa uma leitura, não um rebriefing.

Adicione `.autopilot/` ao `.gitignore`.

## Tarefas-ouro

Três tarefas executáveis que provam que a skill funciona antes de você confiar nela:

```
cd golden/task1-bugfix   # bug real, falha antes, passa depois
cd golden/task2-conventions  # viola AGENTS.md, critério de estilo separado do de API
cd golden/task3-proof    # dois critérios, um deles com asserção de saída
python ../../scripts/ap.py init --goal "..." --ceiling 40000 --criteria criteria.json
python ../../scripts/ap.py verify
```

Cada uma falha de propósito antes da correção. Se passar de primeira, o fixture está errado.

## Licença

MIT.
