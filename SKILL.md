---
name: autopilot
description: Run a development task end to end under a declared token budget, with a machine-checkable definition of done. Use when the user says autopilot, "implement and verify", "take this to done", "run it end to end", "finish this task", or asks for work completed without burning the context window.
version: 1.0.0
license: MIT
---

# Autopilot

Take the task to a verifiable result inside a token ceiling the user can see.
Harness-neutral: works anywhere you can read a file, run a command and edit code.

## Two gates. Nothing else counts.

1. **Budget gate** - declare a ceiling before touching code. Refuse work that cannot fit.
2. **Proof gate** - "done" means a command ran and exited 0. Nothing else is done.

## Loop

0. `python scripts/ap.py init --goal "<one line>" --ceiling <tokens> --criteria criteria.json`

1. **Read the room.** Find the repo root, branch and dirty files. Read the instruction file
   that governs this repo (`references/instruction-precedence.md`). Echo the binding rules
   into state. Before opening any file, `ap.py read --path F`: a second read is a bug.

2. **Define done.** Each criterion is a command plus its expected exit code. If a criterion
   cannot be written as a command, it is not a criterion - say so and ask.

3. **Budget the plan.** `ap.py budget --estimate-files N --estimate-commands M`.
   OVER means cut scope or stop and ask. Do not start and hope.

4. **Plan in steps**, each ending in a runnable check. Write them to state.

5. **Implement with TDD.** Failing test first, minimal change, tests green. Nothing else.

6. **Deterministic review.** Lint, types, tests, coverage diff. Do not spawn a panel of
   review agents - parallel review fan-out is the largest single token sink in this category.

7. **Verify.** `ap.py verify` runs every criterion and writes `proof.md`.
   Any failure means not done.

8. **Deliver only what was authorised**: commit, branch, PR, merge. Then `ap.py report`.

## Four brakes

- **Budget.** `ap.py spend --tokens N` after each step. At 70% write the handoff and compact.
  At 100% stop and report what is left. Never continue silently.
- **Loop.** `ap.py guard diff --file F --hash H` stops on the second identical edit.
  `ap.py guard cmd --command C --ok false` stops on the third failure of the same command.
  A stop is information: re-read the assertion, change approach, do not retry.
- **Instructions.** Project instructions outrank this skill; this skill outranks habit.
  Conflicts are resolved by specificity and stated in one line, never silently.
- **Scope.** Touch only files the criteria need. Unrequested refactors are a defect, not a bonus.

## State that survives compaction

`.autopilot/state.md` is rewritten each step, never appended: goal, binding rules, criteria,
decisions, next step, blocker. Any harness can read it and any harness can resume from it.
This is the portability layer - switching tools mid-task costs one file read, not a re-brief.

## Subagents

Spawn one only when the parent cannot finish with a single read. Cap the count with
`ap.py spawn --n K`. Every subagent returns at most 40 lines: finding, `file:line`, next action.
Never a transcript - the parent pays for every line it accepts. Contract in
`references/subagent-contract.md`.

## Output

Short. What changed, the proof block, tokens spent against the ceiling, what is blocked.
No preamble, no praise, no restating the request.

## Files

- `scripts/ap.py` - budget, state, guard, read ledger, verify, report. Stdlib only.
- `references/` - load on demand, one at a time, never all at once:
  `budget.md`, `proof.md`, `instruction-precedence.md`, `subagent-contract.md`.
- `golden/` - three runnable tasks that prove the skill works before you trust it.
