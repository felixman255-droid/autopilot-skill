#!/usr/bin/env python3
"""ap.py - budget governor, state keeper, loop breaker and proof gate.

One entry point for AI coding agents. Compact output, standard library only.
Works the same under Claude Code, Codex, Cursor, Gemini CLI or a bare shell.

    ap.py init   --goal "add rate limiting" --ceiling 120000 --criteria criteria.json
    ap.py budget --estimate-files 8 --estimate-commands 4
    ap.py spend  --tokens 9000 --note "step 5"
    ap.py spawn  --n 2
    ap.py read   --path src/app.py --note "router, 40 lines, mounts /api"
    ap.py guard  diff --file src/app.py --hash a1b2c3
    ap.py guard  cmd  --command "pytest -q" --ok false
    ap.py state  --set next="write failing test" --set decision="sqlite over postgres"
    ap.py verify
    ap.py report

Exit codes: 0 ok, 1 blocked or verification failed, 2 budget or loop stop.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

STATE = Path(".autopilot")
BUDGET = STATE / "budget.json"
STATE_JSON = STATE / "state.json"
STATE_MD = STATE / "state.md"
GUARD = STATE / "guard.json"
READS = STATE / "reads.json"
CRITERIA = STATE / "criteria.json"
PROOF = STATE / "proof.json"
PROOF_MD = STATE / "proof.md"

# Heuristics, not measurements. Calibrate with real spend (see references/budget.md).
FILE_COST = 1200
CMD_COST = 800
BASELINE = 4000
COMPACT_AT = 0.70


def load(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def save(path, data):
    STATE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def stop(msg, code=1):
    print(msg)
    sys.exit(code)


def need_init():
    if not BUDGET.exists():
        stop("no budget: run `ap.py init --goal ... --ceiling N` first", 2)


# ---------------------------------------------------------------- init

def cmd_init(a):
    if BUDGET.exists() and not a.force:
        stop("already initialised; use --force to reset", 2)
    STATE.mkdir(parents=True, exist_ok=True)
    save(BUDGET, {"ceiling": a.ceiling, "spent": 0, "estimate": None,
                  "subagent_cap": a.subagent_cap, "spawned": 0, "events": []})
    save(STATE_JSON, {"goal": a.goal, "next": "", "blocked": "",
                      "rules": [], "decisions": [], "steps": []})
    save(GUARD, {"diffs": {}, "commands": {}})
    save(READS, {})
    if a.criteria:
        src = Path(a.criteria)
        if not src.exists():
            stop("criteria file not found: %s" % src)
        save(CRITERIA, load(src, {"criteria": []}))
    else:
        save(CRITERIA, {"criteria": []})
    render_state()
    print("initialised: ceiling %d tokens, %d criteria" % (a.ceiling, len(load(CRITERIA, {}).get("criteria", []))))


# ---------------------------------------------------------------- budget

def cmd_budget(a):
    need_init()
    b = load(BUDGET, {})
    est = BASELINE + a.estimate_files * FILE_COST + a.estimate_commands * CMD_COST
    b["estimate"] = est
    save(BUDGET, b)
    ceiling = b["ceiling"]
    pct = 100.0 * est / ceiling if ceiling else 999
    if est > ceiling:
        stop("OVER: estimate %d > ceiling %d (%.0f%%). Cut scope or raise the ceiling."
             % (est, ceiling, pct), 2)
    verdict = "TIGHT" if pct > 60 else "OK"
    print("%s: estimate %d / %d (%.0f%%), headroom %d" % (verdict, est, ceiling, pct, ceiling - est))


def cmd_spend(a):
    need_init()
    b = load(BUDGET, {})
    b["spent"] += a.tokens
    b.setdefault("events", []).append({"tokens": a.tokens, "note": a.note})
    save(BUDGET, b)
    if STATE_JSON.exists():
        render_state()
    ceiling, spent = b["ceiling"], b["spent"]
    pct = 100.0 * spent / ceiling if ceiling else 999
    left = ceiling - spent
    if pct >= 100:
        stop("STOP: %d / %d (%.0f%%). Ceiling reached. Write the handoff and report what is left."
             % (spent, ceiling, pct), 2)
    if pct >= COMPACT_AT * 100:
        print("COMPACT NOW: %d / %d (%.0f%%), %d left. Update state.md, drop history, continue."
              % (spent, ceiling, pct, left))
        return
    print("ok: %d / %d (%.0f%%), %d left" % (spent, ceiling, pct, left))


def cmd_spawn(a):
    need_init()
    b = load(BUDGET, {})
    cap = b.get("subagent_cap") or 0
    total = b.get("spawned", 0) + a.n
    if cap and total > cap:
        stop("STOP: %d subagents > cap %d. Do it in the parent or raise the cap deliberately."
             % (total, cap), 2)
    b["spawned"] = total
    save(BUDGET, b)
    print("subagents %d / %s" % (total, cap or "unlimited"))

# ---------------------------------------------------------------- read ledger

def cmd_read(a):
    need_init()
    r = load(READS, {})
    p = os.path.normpath(a.path)
    entry = r.get(p, {"count": 0, "sha": "", "note": ""})
    if a.note:
        entry["note"] = a.note
    if a.sha:
        entry["sha"] = a.sha
    seen = entry["count"]
    entry["count"] = seen + 1
    r[p] = entry
    save(READS, r)
    if seen == 0:
        print("first read: %s" % p)
        return
    print("ALREADY READ %dx: %s" % (seen, p))
    if entry["note"]:
        print("cached note: %s" % entry["note"])
    print("Do not re-open. Use the note or grep a line range.")


# ---------------------------------------------------------------- guard

def cmd_guard(a):
    need_init()
    g = load(GUARD, {})
    if a.what == "diff":
        key = "%s:%s" % (a.file, a.hash)
        n = g["diffs"].get(key, 0) + 1
        g["diffs"][key] = n
        save(GUARD, g)
        if n >= 2:
            stop("STOP: identical edit to %s applied %dx. You are looping. "
                 "Revert, re-read the failing assertion, change approach." % (a.file, n), 2)
        print("diff recorded 1x on %s" % a.file)
        return
    ok = a.ok.lower() in ("1", "true", "yes", "pass")
    key = a.command
    n = 0 if ok else g["commands"].get(key, 0) + 1
    g["commands"][key] = n
    save(GUARD, g)
    if ok:
        print("command ok, counter reset")
        return
    if n >= 3:
        stop("STOP: `%s` failed %dx. Stop retrying. Report the exact error and what you tried."
             % (key, n), 2)
    print("failure %d/3 on `%s`" % (n, key))


# ---------------------------------------------------------------- state

def render_state():
    s = load(STATE_JSON, {})
    b = load(BUDGET, {})
    lines = ["# Autopilot state", "",
             "**Goal:** %s" % (s.get("goal") or "-"), "",
             "**Next step:** %s" % (s.get("next") or "-"), "",
             "**Blocked:** %s" % (s.get("blocked") or "-"), "",
             "**Budget:** %d / %d" % (b.get("spent", 0), b.get("ceiling", 0)), ""]
    for key, title in (("rules", "Binding rules"), ("decisions", "Decisions"), ("steps", "Steps")):
        items = s.get(key) or []
        lines.append("## %s" % title)
        lines.extend("- %s" % i for i in items) if items else lines.append("- none")
        lines.append("")
    STATE_MD.write_text("\n".join(lines), encoding="utf-8")


def cmd_state(a):
    need_init()
    s = load(STATE_JSON, {})
    for pair in a.set or []:
        if "=" not in pair:
            stop("--set expects key=value, got %r" % pair)
        k, v = pair.split("=", 1)
        k = k.strip()
        if k in ("rules", "decisions", "steps"):
            s.setdefault(k, []).append(v.strip())
        else:
            s[k] = v.strip()
    save(STATE_JSON, s)
    render_state()
    if a.show:
        sys.stdout.write(STATE_MD.read_text(encoding="utf-8"))
    else:
        print("state updated: %s" % STATE_MD)


# ---------------------------------------------------------------- verify

def run_cmd(cmd, cwd, limit):
    try:
        p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=1800)
        out = (p.stdout or "") + (p.stderr or "")
        out = out.strip()
        if len(out) > limit:
            out = "..." + out[-limit:]
        return p.returncode, out
    except subprocess.TimeoutExpired:
        return 124, "timed out after 1800s"
    except OSError as exc:
        return 127, str(exc)


def cmd_verify(a):
    need_init()
    crit = load(CRITERIA, {}).get("criteria", [])
    if not crit:
        stop("no criteria: a task without a command is not done, it is abandoned", 1)
    results, failed = [], 0
    for c in crit:
        code, out = run_cmd(c["cmd"], a.cwd, a.max_output)
        expect = c.get("expect_exit", 0)
        ok = code == expect
        if ok and c.get("contains") and c["contains"] not in out:
            ok = False
        failed += 0 if ok else 1
        results.append({"id": c.get("id", c["cmd"][:20]), "text": c.get("text", ""),
                        "cmd": c["cmd"], "exit": code, "expect": expect,
                        "ok": ok, "output": out})
    save(PROOF, {"at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
                 "failed": failed, "results": results})
    write_proof_md(results, failed)
    for r in results:
        print("%s %s  (exit %d, expected %d)" % ("PASS" if r["ok"] else "FAIL", r["id"], r["exit"], r["expect"]))
    if failed:
        stop("%d of %d criteria failed. Not done. Fix, then verify again." % (failed, len(results)), 1)
    print("all %d criteria pass. Proof at %s" % (len(results), PROOF_MD))


def write_proof_md(results, failed):
    lines = ["# Proof", "", "Generated by `ap.py verify`. Do not edit by hand.", ""]
    lines.append("| id | result | command | exit | expected |")
    lines.append("| --- | --- | --- | --- | --- |")
    for r in results:
        lines.append("| %s | %s | `%s` | %d | %d |" % (
            r["id"], "PASS" if r["ok"] else "FAIL", r["cmd"].replace("|", "\\|"),
            r["exit"], r["expect"]))
    lines.append("")
    for r in results:
        lines.append("## %s" % r["id"])
        if r["text"]:
            lines.append(r["text"])
        lines.append("")
        lines.append("```")
        lines.append(r["output"] or "(no output)")
        lines.append("```")
        lines.append("")
    PROOF_MD.write_text("\n".join(lines), encoding="utf-8")


def cmd_report(a):
    need_init()
    b = load(BUDGET, {})
    s = load(STATE_JSON, {})
    p = load(PROOF, {})
    res = p.get("results", [])
    failed = [r["id"] for r in res if not r["ok"]]
    if not res:
        stop("no verification on record: run `ap.py verify` before reporting done", 1)
    if failed:
        stop("cannot report done: %s failed. State the blocker instead." % ", ".join(failed), 1)
    print("DONE %s" % s.get("goal", ""))
    print("proof: %d/%d criteria pass (%s)" % (len(res), len(res), PROOF_MD))
    print("tokens: %d / %d (%.0f%%)" % (b.get("spent", 0), b.get("ceiling", 0),
                                        100.0 * b.get("spent", 0) / (b.get("ceiling") or 1)))
    if s.get("blocked"):
        print("blocked: %s" % s["blocked"])


def cmd_status(a):
    b = load(BUDGET, {})
    p = load(PROOF, {})
    print(json.dumps({"spent": b.get("spent"), "ceiling": b.get("ceiling"),
                      "subagents": b.get("spawned"),
                      "criteria_failed": p.get("failed"),
                      "verified": bool(p)}, ensure_ascii=False))


# ---------------------------------------------------------------- cli

def main(argv=None):
    ap = argparse.ArgumentParser(prog="ap.py", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init")
    p.add_argument("--goal", required=True)
    p.add_argument("--ceiling", type=int, required=True)
    p.add_argument("--criteria")
    p.add_argument("--subagent-cap", type=int, default=0)
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("budget")
    p.add_argument("--estimate-files", type=int, default=0)
    p.add_argument("--estimate-commands", type=int, default=0)
    p.set_defaults(fn=cmd_budget)

    p = sub.add_parser("spend")
    p.add_argument("--tokens", type=int, required=True)
    p.add_argument("--note", default="")
    p.set_defaults(fn=cmd_spend)

    p = sub.add_parser("spawn")
    p.add_argument("--n", type=int, default=1)
    p.set_defaults(fn=cmd_spawn)

    p = sub.add_parser("read")
    p.add_argument("--path", required=True)
    p.add_argument("--sha", default="")
    p.add_argument("--note", default="")
    p.set_defaults(fn=cmd_read)

    p = sub.add_parser("guard")
    p.add_argument("what", choices=["diff", "cmd"])
    p.add_argument("--file", default="")
    p.add_argument("--hash", default="")
    p.add_argument("--command", default="")
    p.add_argument("--ok", default="true")
    p.set_defaults(fn=cmd_guard)

    p = sub.add_parser("state")
    p.add_argument("--set", action="append")
    p.add_argument("--show", action="store_true")
    p.set_defaults(fn=cmd_state)

    p = sub.add_parser("verify")
    p.add_argument("--cwd", default=".")
    p.add_argument("--max-output", type=int, default=600)
    p.set_defaults(fn=cmd_verify)

    p = sub.add_parser("report")
    p.set_defaults(fn=cmd_report)

    p = sub.add_parser("status")
    p.set_defaults(fn=cmd_status)

    a = ap.parse_args(argv)
    a.fn(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
