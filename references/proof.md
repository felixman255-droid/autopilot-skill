# Proof

If it is not a command, it is an opinion.

## criteria.json

```json
{
  "criteria": [
    {"id": "unit", "text": "average() handles an empty list",
     "cmd": "python -m pytest -q", "expect_exit": 0},
    {"id": "style", "text": "no bare print in library code",
     "cmd": "python check_style.py", "expect_exit": 0},
    {"id": "cli", "text": "CLI prints the total",
     "cmd": "python calc.py 1 2 3", "expect_exit": 0, "contains": "6"}
  ]
}
```

- `id` - short, stable, used in the proof table.
- `text` - the acceptance criterion in the user's words.
- `cmd` - exactly what a human would run. Not a paraphrase of it.
- `expect_exit` - usually 0. Use 1 for "must fail" criteria, e.g. a regression test.
- `contains` - optional substring that must appear in the output.

## What counts as proof

| counts | does not count |
| --- | --- |
| `pytest -q` exiting 0 | "I ran the tests and they pass" |
| `ruff check .` with no findings | "the code looks clean" |
| `curl` returning the expected body | "the endpoint works" |
| a screenshot path produced by a command | "I checked the UI" |
| exit code 1 on the pre-fix code, 0 after | "the test would have failed" |

## The proof block

`ap.py verify` writes `.autopilot/proof.md`: a table of id, result, command, exit code,
expected code, then a fenced excerpt of each output, truncated to the last 600 characters.

Paste the table into the final report. The user reads the table, not your summary of it.

## Anti-patterns

- Writing the criterion after the fix, to match what the fix does.
- A criterion that runs the thing you just wrote and nothing else.
- "Manual verification" with no command and no artifact.
- Reporting done while a criterion is red because it "looks unrelated".
