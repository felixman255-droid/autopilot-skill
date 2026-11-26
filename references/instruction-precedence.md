# Instruction precedence

Every harness ships its own instruction file. Read the one that governs this repo, once,
and obey it before anything else.

## Where to look, in order

| file | harness |
| --- | --- |
| `AGENTS.md` | Codex, Cursor, Amp, and most agents that follow the open convention |
| `CLAUDE.md` | Claude Code |
| `.cursor/rules/*.mdc` | Cursor, per-glob rules |
| `.cursorrules` | Cursor, legacy single file |
| `GEMINI.md` | Gemini CLI |
| `.github/copilot-instructions.md` | GitHub Copilot |
| `.windsurfrules` | Windsurf |
| `CONTRIBUTING.md` | humans, but binding on style and process |

Nested files override the root file for their subtree. The most specific file wins.

## Precedence, highest first

1. What the user asked for in this turn, explicitly.
2. The nearest project instruction file.
3. Conventions visible in the code you are about to change (naming, error handling, test layout).
4. This skill.
5. Your default habits and preferences.

## The conflict rule

When two sources disagree, follow the higher one and **state the conflict in one line** in
the report: `AGENTS.md says tabs, the file I touched uses spaces - followed AGENTS.md.`
Never resolve a conflict silently. Silent resolution is how an agent produces a correct
change in the wrong style, which reads as a wrong change.

## Echo, do not remember

After reading, write the five rules that actually bind this task into state:

```
ap.py state --set rules="no new dependencies" --set rules="pytest only, no unittest"
```

Rules in `state.md` survive compaction. Rules in your context do not. When the context is
compacted, re-read `state.md` - it is one small file, and it is cheaper than the instruction
file plus the reasoning that produced it.

## Common failure

The instruction file is long, so the agent skims it, then violates the one rule that mattered.
Read it in full once, extract the binding rules, and never re-read it. If it is over ~200
lines, read the headings first and then only the sections the task touches.
