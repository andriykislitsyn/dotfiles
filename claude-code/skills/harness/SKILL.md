---
name: harness
description: Use when investigating a Harness CI/CD pipeline - execution status, logs, failed tests, triggers, secrets, or input sets - or when creating/updating a trigger (the one Harness object type that isn't git-synced). Triggers on phrases like "check this Harness pipeline", "why did this Harness execution fail", "what triggers this pipeline", "what secrets exist", "which input sets does this pipeline have", "create/update this Harness trigger", or a pasted app.harness.io URL.
---

# Harness Pipeline Investigation

## Authentication

Token lives at `~/.harness/api-token` (a Harness Personal Access Token, format
`pat.<accountId>.<tokenId>.<secret>`). The script loads it automatically - no setup
needed beyond that file existing.

## Usage

`status`/`tests`/`logs` accept either a pasted execution URL or explicit ID flags.
`triggers`/`inputsets` are scoped to a pipeline (no execution needed) - a bare pipeline
URL, an execution URL (the extra segment is ignored), or explicit flags all work.
`secrets` is scoped to account/org/project (org and project are optional - a secret
can live at any of the three).

```bash
# From a pasted URL (path is parsed for account/org/project/pipeline/execution)
python3 ~/.claude/skills/harness/scripts/harness.py status --url "<execution-url>"
python3 ~/.claude/skills/harness/scripts/harness.py tests --url "<execution-url>"
python3 ~/.claude/skills/harness/scripts/harness.py logs --url "<execution-url>"
python3 ~/.claude/skills/harness/scripts/harness.py logs --url "<execution-url>" --step <stepId>
python3 ~/.claude/skills/harness/scripts/harness.py triggers --url "<pipeline-or-execution-url>"
python3 ~/.claude/skills/harness/scripts/harness.py inputsets --url "<pipeline-or-execution-url>"

# Or with explicit IDs
python3 ~/.claude/skills/harness/scripts/harness.py status \
  --account <accountId> --org <org> --project <project> \
  --pipeline <pipeline> --execution <executionId>
python3 ~/.claude/skills/harness/scripts/harness.py triggers \
  --account <accountId> --org <org> --project <project> --pipeline <pipeline>
python3 ~/.claude/skills/harness/scripts/harness.py secrets --account <accountId>
python3 ~/.claude/skills/harness/scripts/harness.py secrets --account <accountId> --org <org>
python3 ~/.claude/skills/harness/scripts/harness.py secrets --account <accountId> --org <org> --project <project>

# Create or update a trigger from local YAML (write - see Gotchas before using --apply)
python3 ~/.claude/skills/harness/scripts/harness.py apply-trigger --file <trigger.yaml> \
  --account <accountId> --connector-ref <pipeline's own codebase connectorRef> \
  --repo-name <pipeline's own codebase repoName>            # dry-run: prints CREATE or UPDATE
python3 ~/.claude/skills/harness/scripts/harness.py apply-trigger --file <trigger.yaml> \
  --account <accountId> --connector-ref <connectorRef> --repo-name <repoName> --apply
```

| Subcommand | What it shows |
|---|---|
| `status` | Pipeline name, run number, overall status, start/end time, stage counts, and per-stage status + failure message |
| `tests` | Failed test cases (suite, classname, testcase, failure type/message) via the Test Intelligence API |
| `logs` | Raw execution or step log lines (async - polls until Harness finishes zipping them, can take a few seconds) |
| `triggers` | Every trigger configured on a pipeline - name, identifier, type, enabled, branch. Use `get_triggers()`'s return value (each item's `yaml` field) for the full trigger definition (webhook payload/path conditions, cron expression, etc.) when the summary isn't enough - triggers live only in Harness, never in the repo's `.harness/` YAML. |
| `secrets` | Secret identifiers at a scope, printed as the exact `secrets.getValue(...)` string to use (`account.x`, `org.x`, or bare `x` for project scope) - never values, Harness doesn't expose those via any API. Resolves the org./account. prefix confusion that has caused real pipeline failures (a project-scoped ref failing to resolve an org-scoped secret, or vice versa) without needing to trigger a pipeline run to find out. |
| `inputsets` | Every input set on a pipeline by identifier - use when a trigger's `inputSetRefs` names one and it's unclear what that input set actually pins (branch, etc.) without reading the git-synced YAML by hand. |
| `apply-trigger` | **Write.** Create-or-update (upsert) a trigger from a local YAML file - the one Harness object type that can't be git-synced, so today it's created by hand-pasting YAML into the UI. Dry-run by default (prints whether it would CREATE or UPDATE); `--apply` performs it. |

## Example output (`status`)

```
Pipeline:    E2E v2 (run #57)
Status:      Success
Started:     2026-07-24 14:37:49 UTC
Ended:       2026-07-24 14:51:35 UTC
Stages:      3 succeeded, 0 failed, 0 running, 4 total

Stage results:
  Deploy: Success
  E2E: Success
  Cleanup: Success
  Pipeline Rollback: NotStarted
  Pytest: Skipped
```

## Gotchas

- `--step` requires the step ID as shown in the Harness UI, not a step name. Step IDs
  aren't obtainable from the `status` output - they live in each stage's own execution
  graph, a separate lookup this skill doesn't otherwise need.
- Log downloads only work with a PAT (`pat.` prefix) token - Harness's log-service
  endpoint doesn't accept a Bearer token, unlike every other endpoint this skill calls.
- `tests`/`logs` both call the status endpoint internally first to get the pipeline's
  run sequence (build number) - a failing `status` call means `tests`/`logs` will fail
  too, so start troubleshooting there.
- `status`'s failure info is per-stage (`layoutNodeMap[...].failureInfo.message`), not
  a single top-level field - a pipeline can partially fail with some stages still
  showing `Success`.
- No trigger-run or list-executions support, deliberately. The skill investigates
  and edits triggers, it doesn't start pipelines.
- `apply-trigger` needs `--connector-ref`/`--repo-name` from the *target pipeline's*
  own `properties.ci.codebase` (not the trigger's own YAML, which usually doesn't
  carry them) - read them from that pipeline's committed YAML first. Required by the
  API even though the trigger object itself is never git-synced.
- `apply-trigger`'s exists-check (`GET .../triggers/{id}`) assumes any non-200 means
  "doesn't exist yet" and creates - a transient network error would misfire as a
  CREATE attempt. Low risk in practice (a real CREATE against an existing identifier
  just fails with a clear 409/conflict from Harness, it doesn't silently duplicate
  anything), but don't retry a failed `apply-trigger --apply` blindly without reading
  why it failed first.
- Confirm the identifier/pipelineIdentifier printed in the dry-run output before
  passing `--apply` - always run without `--apply` first and read the CREATE/UPDATE
  line.
