#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

GATE_SET = {"needs-input", "needs-approval", "needs-rework"}

def _read_json_stdin() -> dict:
    raw = sys.stdin.buffer.read()
    return json.loads(raw.decode("utf-8"))

def _skip(reason: str, code: int) -> int:
    # minimaler Skip-Output (optional); Lobster stoppt bei Exit!=0
    sys.stdout.write(json.dumps({"skip": True, "reason": reason}, ensure_ascii=False))
    return code

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--require-status", default=None)
    ap.add_argument("--require-gate", default=None)          # z.B. needs-rework
    ap.add_argument("--forbid-gates", default="")            # CSV
    ap.add_argument("--require-assignee-empty", action="store_true")
    ap.add_argument("--forbid-assignee", default=None)       # z.B. Hannes
    ap.add_argument("--artifact-path", default=None)         # z.B. requirements/<id>.md
    ap.add_argument("--artifact-must-exist", action="store_true")
    ap.add_argument("--artifact-must-not-exist", action="store_true")
    ap.add_argument("--skip-exit-code", type=int, default=3)
    args = ap.parse_args()

    task = _read_json_stdin()

    if task.get("ok") is not True:
        # "show" Fehler: als echter Fehler behandeln (nicht Skip)
        sys.stdout.write(json.dumps(task, ensure_ascii=False))
        return 2

    status = task.get("status")
    meta = task.get("meta") or {}
    tags = set(meta.get("tags") or [])
    assignee = meta.get("assignee")

    # Gate-Exklusivität: max 1 Gate-Tag aktiv (Konzept) :contentReference[oaicite:11]{index=11}
    active_gates = [t for t in tags if t in GATE_SET]
    if len(active_gates) > 1:
        return _skip(f"MULTIPLE_GATE_TAGS:{','.join(sorted(active_gates))}", args.skip_exit_code)

    # Status-Anforderung
    if args.require_status and status != args.require_status:
        return _skip(f"STATUS_MISMATCH:{status}", args.skip_exit_code)

    # Forbidden gates
    forbid = {t.strip() for t in (args.forbid_gates.split(",") if args.forbid_gates else []) if t.strip()}
    if forbid and any(t in tags for t in forbid):
        return _skip("FORBIDDEN_GATE_PRESENT", args.skip_exit_code)

    # Required gate
    if args.require_gate and args.require_gate not in tags:
        return _skip("REQUIRED_GATE_MISSING", args.skip_exit_code)

    # Assignee Regeln (Konzept) :contentReference[oaicite:12]{index=12}
    if args.require_assignee_empty and (assignee not in (None, "")):
        return _skip("ASSIGNEE_NOT_EMPTY", args.skip_exit_code)

    if args.forbid_assignee and assignee == args.forbid_assignee:
        return _skip("ASSIGNEE_FORBIDDEN", args.skip_exit_code)

    # Artefaktregeln (erstmalig vs. rework) :contentReference[oaicite:13]{index=13}
    if args.artifact_path:
        p = Path(args.artifact_path)
        if args.artifact_must_exist and not p.exists():
            return _skip("ARTIFACT_MISSING", args.skip_exit_code)
        if args.artifact_must_not_exist and p.exists():
            return _skip("ARTIFACT_EXISTS", args.skip_exit_code)

    # Proceed: Task JSON unverändert weiterreichen
    sys.stdout.write(json.dumps(task, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
