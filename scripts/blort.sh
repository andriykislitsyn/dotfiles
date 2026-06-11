#!/bin/bash
set -euo pipefail

usage() {
    cat <<EOF
Usage: blort [OPTIONS] [PR_NUMBER]

Run black, isort, and pylint on changed Python files.

  PR_NUMBER   Get changed files from this GitHub PR
  (no args)   Get changed files from current branch vs master

Options:
  -n, --dry-run   List changed files without running tools
  -h, --help      Show this help
EOF
    exit 0
}

DRY_RUN=false
PR_NUMBER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -n|--dry-run) DRY_RUN=true; shift ;;
        -h|--help) usage ;;
        *)
            if [[ "$1" =~ ^[0-9]+$ ]]; then
                PR_NUMBER="$1"
            else
                echo "Unknown argument: $1" >&2
                usage
            fi
            shift
            ;;
    esac
done

if [[ -n "$PR_NUMBER" ]]; then
    FILES=$(gh pr view "$PR_NUMBER" --json files --jq '.files[].path')
else
    FILES=$(git diff --name-only --diff-filter=d master...)
fi

PY_FILES=$(echo "$FILES" | grep '\.py$' || true)

if [[ -z "$PY_FILES" ]]; then
    echo "No Python files changed."
    exit 0
fi

EXISTING=()
while IFS= read -r f; do
    if [[ -f "$f" ]]; then
        EXISTING+=("$f")
    fi
done <<< "$PY_FILES"

if [[ ${#EXISTING[@]} -eq 0 ]]; then
    echo "No Python files changed (all deleted)."
    exit 0
fi

echo "Changed Python files (${#EXISTING[@]}):"
printf '  %s\n' "${EXISTING[@]}"
echo ""

if $DRY_RUN; then
    exit 0
fi

echo "=== black ==="
black "${EXISTING[@]}"
echo ""

echo "=== isort ==="
isort "${EXISTING[@]}"
echo ""

echo "=== pylint ==="
pylint "${EXISTING[@]}"
