# Subagent contract

A subagent is a token loan. You pay the principal when it starts and the interest when you
read what it returns. Most agent runs lose money on this trade.

## Spawn only when

- The job is genuinely separable: a search across a tree, a read of a large unfamiliar area,
  a test run whose output you would otherwise paste into your own context.
- The parent cannot answer it with one `grep` and one file read.
- You have a subagent left under the cap (`ap.py spawn --n 1`).

Do not spawn for: a file you could open, a command you could run, a summary you could write.

## What comes back

At most 40 lines, in this shape:

```
FINDING: the retry helper lives in src/net/retry.py and caps at 3 attempts
FILE: src/net/retry.py:14-38
NEXT: change MAX_ATTEMPTS there, the caller at src/api/client.py:88 reads it
RISK: two other callers depend on the 3-attempt cap
```

Four keys, no prose, no code dumps, no "I searched for..." narration.

## Hard rules

- **No transcripts.** A returned transcript is billed again in the parent. This is the single
  most expensive mistake in agent orchestration: a 121k-token task became 513k when fanned
  out, because every child carried its own bootstrap and the parent absorbed the result.
- **No file contents** unless the parent asked for a specific range, and then at most 30 lines.
- **No recommendations beyond the question asked.** "While I was there I also noticed" costs
  tokens and invites scope creep.
- **State uncertainty as uncertainty.** `NOT FOUND` is a valid, cheap answer.

## Cap the fan-out

```
ap.py spawn --n 3
```

The cap is enforced by the script, not by discipline. If the task needs more than the cap,
the task is too big for the budget - split it into two runs with two ceilings.

## When a child fails

One retry with a sharper question, then report the failure to the user. Do not spawn a third
child to investigate the second one's failure. That recursion is how a 20-minute task becomes
a two-day review.
