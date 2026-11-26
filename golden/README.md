# Tarefas-ouro

Três tarefas que provam que a skill funciona. Cada uma **falha de propósito** antes da correção.
Se passar de primeira, o fixture está errado e não prova nada.

Rode a partir da pasta da tarefa, com `ap.py` no caminho relativo.

## task1-bugfix

`average([])` levanta `ZeroDivisionError`. Um critério, um comando.

```
cd task1-bugfix
python ../../scripts/ap.py init --goal "average() não pode quebrar com lista vazia" --ceiling 40000 --criteria criteria.json
python ../../scripts/ap.py verify     # FAIL
# corrija calc.py
python ../../scripts/ap.py verify     # PASS
python ../../scripts/ap.py report
```

Prova: o gate fecha com um único comando e recusa relatório antes disso.

## task2-conventions

`report.py` chama `print()`, e o `AGENTS.md` do repo proíbe. Dois critérios: um de estilo, um de
API. Antes da correção, o de estilo falha e o de API passa — é isso que mostra que os critérios
são independentes e não um carimbo único.

```
cd task2-conventions
python ../../scripts/ap.py init --goal "remover print conforme AGENTS.md" --ceiling 30000 --criteria criteria.json
python ../../scripts/ap.py verify     # style FAIL, api PASS
```

Prova: a regra do repositório entra como critério executável, não como instrução que o agente
pode ignorar.

## task3-proof

`parse_range` não está implementado. Dois critérios, o segundo com asserção de saída (`contains`).

```
cd task3-proof
python ../../scripts/ap.py init --goal "implementar parse_range com prova" --ceiling 60000 --criteria criteria.json
python ../../scripts/ap.py verify     # 2 FAIL
# implemente ranges.py
python ../../scripts/ap.py verify     # 2 PASS
```

Prova: verificação de saída, não só de código de retorno.

## Limpeza

Cada execução cria `.autopilot/` na pasta da tarefa. Apague depois de testar.
