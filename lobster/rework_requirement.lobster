name: wf.rework_requirement
args:
  project_id:
    required: true
  task_id:
    required: true
  task_tracking_bin:
    required: true

  requirements_dir:
    default: "requirements"
  assignee_human:
    default: "Hannes"

  max_body_lines:
    default: 400
  max_body_chars:
    default: 20000

env:
  PROJECT_ID: ${project_id}
  TASK_ID: ${task_id}
  TASK_TRACKING_BIN: ${task_tracking_bin}
  REQUIREMENTS_DIR: ${requirements_dir}
  ASSIGNEE_HUMAN: ${assignee_human}
  MAX_BODY_LINES: ${max_body_lines}
  MAX_BODY_CHARS: ${max_body_chars}

steps:
  - id: show_task
    command: |
      python3 "${TASK_TRACKING_BIN}" show "${PROJECT_ID}" "${TASK_ID}" \
        --body --max-body-lines "${MAX_BODY_LINES}" --max-body-chars "${MAX_BODY_CHARS}"

  - id: precheck
    stdin: $show_task.stdout
    command: |
      python3 scripts/precheck.py \
        --require-status REQUIREMENT \
        --require-gate needs-rework \
        --forbid-gates needs-input,needs-approval \
        --forbid-assignee "${ASSIGNEE_HUMAN}" \
        --artifact-path "${REQUIREMENTS_DIR}/${TASK_ID}.md" \
        --artifact-must-exist \
        --skip-exit-code 3

  - id: llm
    stdin: $precheck.stdout
    command: |
      python3 scripts/llm_task_run.py \
        --prompt-file prompts/rework_requirement.txt \
        --schema-file schemas/rework_requirement.schema.json \
        --wrap-with-task \
        --task-id "${TASK_ID}" \
        --requirements-dir "${REQUIREMENTS_DIR}"

  - id: apply
    stdin: $llm.stdout
    command: |
      python3 scripts/apply_rework_requirement.py \
        --project-id "${PROJECT_ID}" \
        --task-id "${TASK_ID}" \
        --task-tracking-bin "${TASK_TRACKING_BIN}" \
        --requirement-path "${REQUIREMENTS_DIR}/${TASK_ID}.md" \
        --assignee-human "${ASSIGNEE_HUMAN}"
