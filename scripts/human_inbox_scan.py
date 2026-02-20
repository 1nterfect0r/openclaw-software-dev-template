#!/usr/bin/env python3
import json, os, subprocess, sys

PROJECT_ID = os.environ["PROJECT_ID"]
TASK_TRACKING_PY = os.environ["TASK_TRACKING_PY"]
HUMAN = os.environ.get("HUMAN", "Hannes")

def tt(*args):
    # task-tracking outputs exactly one JSON object to stdout (normative) :contentReference[oaicite:11]{index=11}
    p = subprocess.run([sys.executable, TASK_TRACKING_PY, *args], capture_output=True, text=True)
    out = (p.stdout or "").str:contentReference[oaicite:12]{index=12}        return {"ok": False, "error": {"code": "EMPTY_STDOUT", "message": "task-tracking returned empty stdout"}}
    try:
        return json.loads(out)
    except Exception:
        return {"ok": False, "error": {"code": "INVALID_JSON", "message": out[:500]}}

def main():
    needs_input = tt("list", PROJECT_ID, "--assignee", HUMAN, "--tag", "needs-input",
                     "--fields", "task_id,status,priority,updated_at", "--limit", "50")
    needs_approval = tt("list", PROJECT_ID, "--assignee", HUMAN, "--tag", "needs-approval",
                        "--fields", "task_id,status,priority,updated_at", "--limit", "50")

    if not needs_input.get("ok") or not needs_approval.get("ok"):
        print(json.dumps({"ok": False, "error": {"code": "UPSTREAM_ERROR",
              "details": {"needs_input": needs_input, "needs_approval": needs_approval}}}))
        return 1

    summary = {
        "ok": True,
        "project_id": PROJECT_ID,
        "count_needs_input": needs_input.get("count", 0),
        "count_needs_approval": needs_approval.get("count", 0),
        "needs_input": needs_input.get("items", [])[:5],
        "needs_approval": needs_approval.get("items", [])[:5],
        "has_work": (needs_input.get("count", 0) + needs_approval.get("count", 0)) > 0,
    }
    print(json.dumps(summary))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
