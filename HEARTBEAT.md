# Kanban Human Inbox

- Führe das Lobster-Workflow `lobster/human_inbox_scan.lobster` aus.
- Wenn `has_work=false`: antworte exakt `HEARTBEAT_OK`.
- Wenn `has_work=true`: nenne Anzahl needs-input und needs-approval, liste max. 5 Items (task_id, status), und frage:
  "Wenn du das jetzt bearbeiten willst, antworte mit: Start"
- Keine Artefakt-Dateien ändern. Keine Statuswechsel.
