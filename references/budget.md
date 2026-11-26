# Budget

The ceiling is a promise. Everything here exists to keep it.

## Estimate before you start

```
ap.py budget --estimate-files 8 --estimate-commands 4
```

| constant | default | meaning |
| --- | --- | --- |
| `BASELINE` | 4000 | system prompt, skill, tool definitions, one round trip |
| `FILE_COST` | 1200 | one average source file read once |
| `CMD_COST` | 800 | one test/lint run including its output |

These are heuristics, not measurements. Calibrate against your own history: after a task,
compare `spent` with the estimate and adjust the two constants in `scripts/ap.py` once,
not per task.

## The three states

| spend | state | action |
| --- | --- | --- |
| < 70% | OK | continue |
| 70-99% | COMPACT NOW | write handoff into `state.md`, drop history, continue from state |
| >= 100% | STOP | report what is done, what is left, what blocked it |

`ap.py spend` prints the state and exits 2 at the ceiling. A non-zero exit is not a
suggestion.

## Where the tokens actually go

Ranked by cost, from the field data behind this skill:

1. **Parallel review agents.** Five to twelve reviewers on one diff cost more than the change.
2. **Subagent transcripts.** A parent that accepts full transcripts pays twice for one job.
3. **Re-reading files.** Every repeat read is a full re-payment for information you had.
4. **Exploration by wandering.** Grep beats reading a tree; a line range beats a whole file.
5. **Long explanations.** Prose in the transcript is billed like code.

## Rules that follow

- One subagent per genuinely separable job, never a panel.
- Subagent output capped at 40 lines, with `file:line`, never a transcript.
- `ap.py read` before every open. Second read of the same path is a defect.
- Read a line range, not a file, when you already know the shape.
- Ask for the ceiling before starting when the user has not given one. A guessed ceiling
  is better than none, and the user can correct it in one line.
