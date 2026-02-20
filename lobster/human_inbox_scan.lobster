name: human-inbox-scan
env:
  PROJECT_ID: "YOUR_PROJECT_ID"
  TASK_TRACKING_PY: :contentReference[oaicite:10]{index=10}/task_tracking.py"
  HUMAN: "Hannes"
steps:
  - id: scan
    command: bash -lc 'python3 scripts/human_inbox_scan.py'
