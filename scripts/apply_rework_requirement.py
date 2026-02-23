#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

GATE_TAGS = {"needs-input", "needs-approval", "needs-rework"}

def _read_json_stdin() -> dict:
    raw = sys.stdin.buffer.read()
    return json.loads(raw.decode("utf-8"))

def _run_tt(task_tracking_bin: str, argv: list[str], stdin_text: str | None = None) -> dict:
    proc = subprocess.run(
        ["python3", task_tracking_bin, *argv],
        input=stdin_text,
        text=True,
        capture_output=True,
    )
    # CLI: stdout ist immer JSON, auch im Fehlerfall :contentReference[oaicite:18]{index=18}
    if proc.returncode != 0:
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        raise SystemExit(proc.returncode)
    return json.loads(proc.stdout)

def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".tmp.{path.name}")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-id", required=True)
    ap.add_argument("--task-id", required=True)
    ap.add_argument("--task-tracking-bin", required=True)
    ap.add_argument("--requirement-path", required=True)
    ap.add_argument("--assignee-human", required=True)
    args = ap.parse_args()

    wrapper = _read_json_stdin()
    task = wrapper["task"]
    llm = wrapper["llm"]

    action = llm["action"]
    body = llm["updated_task_body"]
    req_md = llm["requirement_markdown"]

    meta = task.get("meta") or {}
    tags = meta.get("tags") or []

    # Gate-Entscheidung gemäß Konzept:
    # - needs-input oder needs-approval -> assignee=Hannes
    # - needs-rework sollte nach Apply entfernt sein :contentReference[oaicite:19]{index=19}
    if action == "needs_input":
        gate_tag = "needs-input"
        assignee = args.assignee_human
        wrote_artifact = False
    else:
        gate_tag = "needs-approval"
        assignee = args.assignee_human
        wrote_artifact = True

    # Gate-Exklusivität: alle Gate-Tags entfernen, dann genau eines setzen :contentReference[oaicite:20]{index=20}
    new_tags = sorted(set([t for t in tags if t not in GATE_TAGS] + [gate_tag]))

    patch = {
        "set": {"tags": new_tags, "assignee": assignee},
        "unset": []
    }

    req_path = Path(args.requirement_path)

    # Artefakt-Sperre: wenn needs-input gesetzt wird, KEIN Artefakt schreiben 
    if wrote_artifact:
        _atomic_write(req_path, req_md)

    _run_tt(args.task_tracking_bin, ["meta-update", args.project_id, args.task_id, "--stdin"], stdin_text=json.dumps(patch, ensure_ascii=False))
    _run_tt(args.task_tracking_bin, ["set-body", args.project_id, args.task_id, "--stdin"], stdin_text=body)

    out = {
        "ok": True,
        "action": action,
        "gate_tag": gate_tag,
        "requirement_path": str(req_path),
        "wrote_requirement": wrote_artifact,
    }
    sys.stdout.write(json.dumps(out, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
