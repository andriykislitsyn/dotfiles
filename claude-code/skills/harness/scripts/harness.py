#!/usr/bin/env python3
"""Investigate Harness pipeline executions: status, logs, and failed tests."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

TOKEN_PATH = Path.home() / ".harness" / "api-token"
BASE_URL = "https://app.harness.io"


def load_auth_header(token_path: Path = TOKEN_PATH) -> dict[str, str]:
    if not token_path.exists():
        sys.exit(f"Harness token not found at {token_path}")
    token = token_path.read_text().strip()
    if not token:
        sys.exit(f"Harness token file at {token_path} is empty")
    headers = {"Content-Type": "application/json"}
    if token.startswith("pat."):
        headers["x-api-key"] = token
    else:
        headers["Authorization"] = f"Bearer {token}"
    return headers


URL_PATTERN = re.compile(
    r"/account/(?P<account>[^/]+)/.*?"
    r"/orgs/(?P<org>[^/]+)"
    r"/projects/(?P<project>[^/]+)"
    r"/pipelines/(?P<pipeline>[^/]+)"
    r"/executions/(?P<execution>[^/]+)"
)


def parse_execution_url(url: str) -> dict[str, str]:
    from urllib.parse import urlparse

    path = urlparse(url).path
    match = URL_PATTERN.search(path)
    if not match:
        sys.exit(
            f"Could not parse account/org/project/pipeline/execution IDs from URL "
            f"path {path!r} - expected a Harness execution URL shape like "
            ".../account/<id>/.../orgs/<org>/projects/<project>/pipelines/<pipeline>"
            "/executions/<executionId>/..."
        )
    return match.groupdict()


def resolve_ids(args: argparse.Namespace) -> dict[str, str]:
    ids: dict[str, str] = {}
    if args.url:
        ids.update(parse_execution_url(args.url))
    for key in ("account", "org", "project", "pipeline", "execution"):
        flag_value = getattr(args, key, None)
        if flag_value:
            ids[key] = flag_value
    missing = [k for k in ("account", "org", "project", "pipeline", "execution") if not ids.get(k)]
    if missing:
        sys.exit(
            f"Missing required IDs: {', '.join(missing)}. "
            "Pass --url <execution-url> or the explicit --account/--org/--project/"
            "--pipeline/--execution flags."
        )
    return ids


def request_or_die(method: str, url: str, **kwargs: Any) -> "requests.Response":
    """requests.request(), but non-2xx prints status + a body snippet and exits
    non-zero instead of raising an unhandled traceback."""
    import requests

    response = requests.request(method, url, **kwargs)
    if not response.ok:
        snippet = response.text[:500]
        sys.exit(f"Harness API call failed: {method} {url} -> {response.status_code}\n{snippet}")
    return response


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--url", help="Full Harness pipeline execution URL")
    parser.add_argument("--account", help="Harness account ID")
    parser.add_argument("--org", help="Harness org ID")
    parser.add_argument("--project", help="Harness project ID")
    parser.add_argument("--pipeline", help="Harness pipeline ID")
    parser.add_argument("--execution", help="Harness execution ID")


PIPELINE_URL_PATTERN = re.compile(
    r"/account/(?P<account>[^/]+)/.*?"
    r"/orgs/(?P<org>[^/]+)"
    r"/projects/(?P<project>[^/]+)"
    r"/pipelines/(?P<pipeline>[^/]+)"
)


def parse_pipeline_url(url: str) -> dict[str, str]:
    from urllib.parse import urlparse

    path = urlparse(url).path
    match = PIPELINE_URL_PATTERN.search(path)
    if not match:
        sys.exit(
            f"Could not parse account/org/project/pipeline IDs from URL path {path!r} - "
            "expected a Harness pipeline or execution URL shape like "
            ".../account/<id>/.../orgs/<org>/projects/<project>/pipelines/<pipeline>/..."
        )
    return match.groupdict()


def resolve_pipeline_ids(args: argparse.Namespace) -> dict[str, str]:
    """Like resolve_ids, but for operations scoped to a pipeline rather than one
    execution (no execution ID required or parsed)."""
    ids: dict[str, str] = {}
    if args.url:
        ids.update(parse_pipeline_url(args.url))
    for key in ("account", "org", "project", "pipeline"):
        flag_value = getattr(args, key, None)
        if flag_value:
            ids[key] = flag_value
    missing = [k for k in ("account", "org", "project", "pipeline") if not ids.get(k)]
    if missing:
        sys.exit(
            f"Missing required IDs: {', '.join(missing)}. "
            "Pass --url <pipeline or execution URL> or the explicit --account/--org/"
            "--project/--pipeline flags."
        )
    return ids


def _add_pipeline_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--url", help="Full Harness pipeline or execution URL")
    parser.add_argument("--account", help="Harness account ID")
    parser.add_argument("--org", help="Harness org ID")
    parser.add_argument("--project", help="Harness project ID")
    parser.add_argument("--pipeline", help="Harness pipeline ID")


def resolve_pipeline_ids_no_pipeline(args: argparse.Namespace) -> dict[str, str]:
    """Like resolve_pipeline_ids, but only account is required - org/project are
    optional scoping (a secret can live at account, org, or project scope)."""
    ids: dict[str, str] = {}
    if args.url:
        try:
            ids.update(parse_pipeline_url(args.url))
        except SystemExit:
            # A bare account-level URL has no /orgs/.../projects/... segment -
            # that's fine here, org/project are optional at this scope.
            match = re.search(r"/account/(?P<account>[^/]+)/", args.url)
            if match:
                ids["account"] = match["account"]
    for key in ("account", "org", "project"):
        flag_value = getattr(args, key, None)
        if flag_value:
            ids[key] = flag_value
    if not ids.get("account"):
        sys.exit(
            "Missing required ID: account. Pass --url <harness-url> or --account."
        )
    return ids


def get_execution_status(ids: dict[str, str], headers: dict[str, str]) -> dict[str, Any]:
    response = request_or_die(
        "GET",
        f"{BASE_URL}/gateway/pipeline/api/pipelines/execution/v2/{ids['execution']}",
        headers=headers,
        params={
            "routingId": ids["account"],
            "accountIdentifier": ids["account"],
            "orgIdentifier": ids["org"],
            "projectIdentifier": ids["project"],
        },
        timeout=30,
    )
    summary = response.json()["data"]["pipelineExecutionSummary"]
    summary["run_sequence"] = summary.get("runSequence")
    return summary


def cmd_status(args: argparse.Namespace) -> None:
    ids = resolve_ids(args)
    headers = load_auth_header()
    summary = get_execution_status(ids, headers)

    print(f"Pipeline:    {summary.get('name', ids['pipeline'])} (run #{summary.get('run_sequence')})")
    print(f"Status:      {summary.get('status')}")
    print(f"Started:     {_format_ts(summary.get('startTs'))}")
    print(f"Ended:       {_format_ts(summary.get('endTs'))}")
    print(
        f"Stages:      {summary.get('successfulStagesCount', 0)} succeeded, "
        f"{summary.get('failedStagesCount', 0)} failed, "
        f"{summary.get('runningStagesCount', 0)} running, "
        f"{summary.get('totalStagesCount', 0)} total"
    )

    stages = [
        node
        for node in summary.get("layoutNodeMap", {}).values()
        if node.get("nodeGroup") == "STAGE" and node.get("nodeType") != "parallel"
    ]
    if stages:
        print("\nStage results:")
        for stage in stages:
            print(f"  {stage.get('name', stage.get('nodeIdentifier'))}: {stage.get('status')}")
            failure_message = (stage.get("failureInfo") or {}).get("message")
            if failure_message:
                print(f"    Failure: {failure_message}")


def _format_ts(ts_ms: int | None) -> str:
    if ts_ms is None:
        return "n/a"
    from datetime import datetime, timezone

    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def build_log_prefix(ids: dict[str, str], run_sequence: str, step: str | None) -> str:
    prefix = f"{ids['account']}/pipeline/{ids['pipeline']}/{run_sequence}/-{ids['execution']}"
    if step:
        prefix += f"/{step}"
    return prefix


def get_execution_logs(
    ids: dict[str, str], run_sequence: str, headers: dict[str, str], step: str | None = None
) -> list[str]:
    import io
    import time
    import zipfile

    token = TOKEN_PATH.read_text().strip()
    if not token.startswith("pat."):
        sys.exit(
            "Log download requires a PAT token (starting with 'pat.') - "
            f"the token at {TOKEN_PATH} does not look like one."
        )
    log_headers = {"content-type": "application/json", "x-api-key": token}
    prefix = build_log_prefix(ids, run_sequence, step)

    for attempt in range(30):
        response = request_or_die(
            "POST",
            f"{BASE_URL}/gateway/log-service/blob/download",
            headers=log_headers,
            params={"accountID": ids["account"], "prefix": prefix},
            timeout=30,
        )
        data = response.json()
        if data.get("status") == "success":
            break
        time.sleep(2)
    else:
        sys.exit(f"Log download for prefix {prefix!r} never reached 'success' status after 30 attempts")

    zip_response = request_or_die("GET", data["link"], timeout=60)

    lines: list[str] = []
    with zipfile.ZipFile(io.BytesIO(zip_response.content)) as archive:
        for name in archive.namelist():
            lines.extend(archive.read(name).decode("utf-8", errors="replace").splitlines())
    return lines


def cmd_logs(args: argparse.Namespace) -> None:
    import json

    ids = resolve_ids(args)
    headers = load_auth_header()
    summary = get_execution_status(ids, headers)
    raw_lines = get_execution_logs(ids, summary["run_sequence"], headers, step=args.step)

    for line in raw_lines:
        try:
            entry = json.loads(line)
            level = entry.get("level", "")
            message = entry.get("out", entry.get("message", line))
            print(f"[{level}] {message}" if level else message)
        except json.JSONDecodeError:
            print(line)


def get_failed_tests(
    ids: dict[str, str], run_sequence: str, headers: dict[str, str]
) -> list[dict[str, str]]:
    suites_response = request_or_die(
        "GET",
        f"{BASE_URL}/gateway/ti-service/reports/test_suites",
        headers=headers,
        params={
            "routingId": ids["account"],
            "accountId": ids["account"],
            "orgId": ids["org"],
            "projectId": ids["project"],
            "pipelineId": ids["pipeline"],
            "buildId": run_sequence,
            "report": "junit",
            "pageIndex": 0,
            "testCaseSearchTerm": "",
            "sort": "fail_pct",
            "pageSize": 100,
            "status": "failed",
            "order": "DESC",
        },
        timeout=30,
    )
    test_suites = suites_response.json()["content"]

    all_failed: list[dict[str, str]] = []
    for suite in test_suites:
        cases_response = request_or_die(
            "GET",
            f"{BASE_URL}/gateway/ti-service/reports/test_cases",
            headers=headers,
            params={
                "routingId": ids["account"],
                "accountId": ids["account"],
                "orgId": ids["org"],
                "projectId": ids["project"],
                "buildId": run_sequence,
                "pipelineId": ids["pipeline"],
                "report": "junit",
                "suite_name": suite["name"],
                "status": "failed",
                "testCaseSearchTerm": "",
                "sort": "status",
                "order": "ASC",
                "pageIndex": 0,
                "pageSize": 10,
            },
            timeout=30,
        )
        for test_case in cases_response.json()["content"]:
            if test_case["result"]["type"] == "Passed":
                continue
            all_failed.append(
                {
                    "suite": test_case["suite_name"],
                    "testcase": test_case["name"],
                    "classname": test_case["class_name"],
                    "type": test_case["result"]["type"],
                    "message": test_case["result"]["message"],
                }
            )
    return all_failed


def cmd_tests(args: argparse.Namespace) -> None:
    ids = resolve_ids(args)
    headers = load_auth_header()
    summary = get_execution_status(ids, headers)
    failed_tests = get_failed_tests(ids, summary["run_sequence"], headers)

    if not failed_tests:
        print("No failed tests found (or this pipeline has no Test Intelligence reports).")
        return
    print(f"{len(failed_tests)} failed test(s):\n")
    for test in failed_tests:
        print(f"[{test['suite']}] {test['classname']} :: {test['testcase']}")
        print(f"  {test['type']}: {test['message']}\n")


def get_secrets(ids: dict[str, str], headers: dict[str, str]) -> list[dict[str, Any]]:
    """Secret metadata only (identifier, name, type, scope) - Harness never
    returns encrypted secret values via this or any API."""
    response = request_or_die(
        "GET",
        f"{BASE_URL}/gateway/ng/api/v2/secrets",
        headers=headers,
        params={
            "accountIdentifier": ids["account"],
            "orgIdentifier": ids.get("org"),
            "projectIdentifier": ids.get("project"),
            "pageIndex": 0,
            "pageSize": 200,
        },
        timeout=30,
    )
    data = response.json()["data"]
    return [c["secret"] for c in data.get("content", [])]


def _secret_scope(ids: dict[str, str], secret: dict[str, Any]) -> str:
    """Reconstruct the `<scope>.<identifier>` form used in secrets.getValue(...) -
    this is the exact prefix confusion (unscoped vs org. vs account.) that has
    caused real pipeline failures, so make it explicit rather than just
    printing org/project fields."""
    if not secret.get("orgIdentifier") and not secret.get("projectIdentifier"):
        return f"account.{secret['identifier']}"
    if secret.get("orgIdentifier") and not secret.get("projectIdentifier"):
        return f"org.{secret['identifier']}"
    return secret["identifier"]


def cmd_secrets(args: argparse.Namespace) -> None:
    ids = resolve_pipeline_ids_no_pipeline(args)
    headers = load_auth_header()
    secrets = get_secrets(ids, headers)

    if not secrets:
        print("No secrets found at this scope.")
        return
    print(f"{len(secrets)} secret(s):\n")
    for s in sorted(secrets, key=lambda s: s["identifier"]):
        print(f"- {_secret_scope(ids, s)}  (name: {s.get('name')}, type: {s.get('type')})")


def get_input_sets(ids: dict[str, str], headers: dict[str, str]) -> list[dict[str, Any]]:
    response = request_or_die(
        "GET",
        f"{BASE_URL}/gateway/pipeline/api/inputSets",
        headers=headers,
        params={
            "accountIdentifier": ids["account"],
            "orgIdentifier": ids["org"],
            "projectIdentifier": ids["project"],
            "pipelineIdentifier": ids["pipeline"],
            "pageIndex": 0,
            "pageSize": 100,
        },
        timeout=30,
    )
    data = response.json()["data"]
    return data.get("content", [])


def cmd_inputsets(args: argparse.Namespace) -> None:
    ids = resolve_pipeline_ids(args)
    headers = load_auth_header()
    input_sets = get_input_sets(ids, headers)

    if not input_sets:
        print(f"No input sets found for pipeline {ids['pipeline']!r}.")
        return
    print(f"{len(input_sets)} input set(s) on pipeline {ids['pipeline']!r}:\n")
    for i in input_sets:
        print(f"- {i.get('identifier')} ({i.get('inputSetType', 'INPUT_SET')})")


def get_triggers(ids: dict[str, str], headers: dict[str, str]) -> list[dict[str, Any]]:
    response = request_or_die(
        "GET",
        f"{BASE_URL}/gateway/pipeline/api/triggers",
        headers=headers,
        params={
            "accountIdentifier": ids["account"],
            "orgIdentifier": ids["org"],
            "projectIdentifier": ids["project"],
            "targetIdentifier": ids["pipeline"],
            "pageIndex": 0,
            "pageSize": 100,
        },
        timeout=30,
    )
    data = response.json()["data"]
    return data.get("content", [])


def cmd_triggers(args: argparse.Namespace) -> None:
    ids = resolve_pipeline_ids(args)
    headers = load_auth_header()
    triggers = get_triggers(ids, headers)

    if not triggers:
        print(f"No triggers configured on pipeline {ids['pipeline']!r}.")
        return
    print(f"{len(triggers)} trigger(s) on pipeline {ids['pipeline']!r}:\n")
    for t in triggers:
        print(f"- {t.get('name', t.get('identifier'))} (identifier: {t.get('identifier')})")
        print(f"    type: {t.get('type')}    enabled: {t.get('enabled')}")
        branch = t.get("pipelineBranchName") or t.get("branch")
        if branch:
            print(f"    branch: {branch}")


_YAML_FIELD_RE = "^\\s*{field}:\\s*(\\S.*)$"


def _extract_yaml_field(text: str, field: str) -> str | None:
    """Pulls one top-level scalar field out of a trigger YAML by regex rather
    than a real YAML parse - this script deliberately has no yaml dependency,
    and every trigger YAML this has been pointed at keeps
    identifier/orgIdentifier/projectIdentifier/pipelineIdentifier as simple
    `key: value` lines directly under `trigger:`."""
    match = re.search(_YAML_FIELD_RE.format(field=re.escape(field)), text, re.MULTILINE)
    return match.group(1).strip().strip("\"'") if match else None


def apply_trigger(
    yaml_text: str,
    account: str,
    connector_ref: str,
    repo_name: str,
    headers: dict[str, str],
    dry: bool,
) -> str:
    """Create or update (upsert) a trigger from local YAML - the write
    counterpart to `triggers`, for the one Harness object type that can't be
    git-synced and today can only be edited by hand-pasting YAML into the UI.

    Mirrors harness_client's Triggers.create/update: same query params
    (including storeType=REMOTE, required even though the trigger itself isn't
    git-synced) and a Content-Type: application/yaml body, called directly via
    requests to avoid adding harness_client as a dependency for one script.
    """
    import requests

    trigger_id = _extract_yaml_field(yaml_text, "identifier")
    pipeline_id = _extract_yaml_field(yaml_text, "pipelineIdentifier")
    org = _extract_yaml_field(yaml_text, "orgIdentifier")
    project = _extract_yaml_field(yaml_text, "projectIdentifier")
    if not trigger_id or not pipeline_id or not org or not project:
        sys.exit(
            "Could not find identifier/pipelineIdentifier/orgIdentifier/projectIdentifier "
            "in the trigger YAML - expected simple `key: value` lines directly under `trigger:`."
        )

    base_params = {
        "accountIdentifier": account,
        "orgIdentifier": org,
        "projectIdentifier": project,
        "targetIdentifier": pipeline_id,
        "connectorRef": connector_ref,
        "repoName": repo_name,
        "storeType": "REMOTE",
        "ignoreError": "false",
    }
    url = f"{BASE_URL}/gateway/pipeline/api/triggers"
    get_response = requests.get(
        f"{url}/{trigger_id}",
        headers=headers,
        params={k: base_params[k] for k in ("accountIdentifier", "orgIdentifier", "projectIdentifier", "targetIdentifier")},
        timeout=30,
    )
    exists = get_response.status_code == 200
    verb = "UPDATE" if exists else "CREATE"
    print(f"{'DRY  ' if dry else 'RUN  '}{verb} trigger {trigger_id!r} on pipeline {pipeline_id!r}")
    if dry:
        return verb

    yaml_headers = {**headers, "Content-Type": "application/yaml"}
    if exists:
        request_or_die(
            "PUT", f"{url}/{trigger_id}", headers=yaml_headers, params=base_params,
            data=yaml_text.encode(), timeout=30,
        )
    else:
        request_or_die(
            "POST", url, headers=yaml_headers, params=base_params,
            data=yaml_text.encode(), timeout=30,
        )
    return verb


def cmd_apply_trigger(args: argparse.Namespace) -> None:
    if not args.account:
        sys.exit("--account is required (trigger YAML has no accountIdentifier field)")
    yaml_text = Path(args.file).read_text()
    headers = load_auth_header()
    verb = apply_trigger(
        yaml_text, args.account, args.connector_ref, args.repo_name, headers, dry=not args.apply
    )
    if args.apply:
        print(f"{verb}D.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    status_parser = subparsers.add_parser("status", help="Fetch execution status")
    _add_common_args(status_parser)
    status_parser.set_defaults(func=cmd_status)

    logs_parser = subparsers.add_parser("logs", help="Fetch execution/step logs")
    _add_common_args(logs_parser)
    logs_parser.add_argument("--step", help="Step ID to scope logs to (optional)")
    logs_parser.set_defaults(func=cmd_logs)

    tests_parser = subparsers.add_parser("tests", help="Fetch failed test summary")
    _add_common_args(tests_parser)
    tests_parser.set_defaults(func=cmd_tests)

    triggers_parser = subparsers.add_parser("triggers", help="List triggers configured on a pipeline")
    _add_pipeline_args(triggers_parser)
    triggers_parser.set_defaults(func=cmd_triggers)

    secrets_parser = subparsers.add_parser("secrets", help="List secret identifiers (never values) at a scope")
    _add_pipeline_args(secrets_parser)
    secrets_parser.set_defaults(func=cmd_secrets)

    inputsets_parser = subparsers.add_parser("inputsets", help="List input sets configured on a pipeline")
    _add_pipeline_args(inputsets_parser)
    inputsets_parser.set_defaults(func=cmd_inputsets)

    apply_trigger_parser = subparsers.add_parser(
        "apply-trigger", help="Create or update a trigger from a local YAML file (write - dry-run by default)"
    )
    apply_trigger_parser.add_argument("--file", required=True, help="Path to the trigger YAML")
    apply_trigger_parser.add_argument("--account", help="Harness account ID")
    apply_trigger_parser.add_argument(
        "--connector-ref", required=True, help="connectorRef of the target pipeline's own codebase"
    )
    apply_trigger_parser.add_argument(
        "--repo-name", required=True, help="repoName of the target pipeline's own codebase"
    )
    apply_trigger_parser.add_argument(
        "--apply", action="store_true", help="actually create/update (default: dry-run)"
    )
    apply_trigger_parser.set_defaults(func=cmd_apply_trigger)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
