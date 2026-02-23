#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path
import os

OPENCLAW_BIN = os.environ.get("OPENCLAW_BIN", "~/.npm-global/bin/openclaw")

def _read_json_stdin() -> dict:
    raw = sys.stdin.buffer.read()
    return json.loads(raw.decode("utf-8"))

def _read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

def _read_json_file(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--schema-file", required=True)
    ap.add_argument("--wrap-with-task", action="store_true")

    # NEW: minimal templating inputs
    ap.add_argument("--task-id", required=True)
    ap.add_argument("--requirements-dir", required=True)

    args = ap.parse_args()

    task = _read_json_stdin()
    prompt = _read_text(args.prompt_file)
    schema = _read_json_file(args.schema_file)

    requirements_path = f"{args.requirements_dir}/{args.task_id}.md"
    # minimal, deterministic templating
    prompt = (
        prompt.replace("<task_id>", args.task_id)
              .replace("<requirements_path>", requirements_path)
    )

    args_json = {"prompt": prompt, "input": task, "schema": schema}
    cmd = [
        OPENCLAW_BIN, "invoke",
        "--tool", "llm-task",
        "--action", "json",
        "--args-json", json.dumps(args_json, ensure_ascii=False),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        sys.stdout.write(proc.stdout)
        return proc.returncode

    env = json.loads(proc.stdout)
    llm = env["details"]["json"]

    out = {"task": task, "llm": llm} if args.wrap_with_task else llm
    sys.stdout.write(json.dumps(out, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
