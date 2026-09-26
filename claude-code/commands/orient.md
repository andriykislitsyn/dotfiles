Orient yourself to the current project efficiently — read key files directly rather than running broad exploration agents.

## Steps

1. **Check git context** — run `git log --oneline -10` and `git status` in parallel.
2. **Look for a CLAUDE.md** — if present at the repo root, read it; it has a pre-built map.
3. **Identify project type** from the root directory listing (`ls -1`), then read only the files that define structure:
   - Python: `pyproject.toml` or `setup.py`, then `src/` top-level only
   - Node/TS: `package.json`, then `src/` top-level only
   - Go: `go.mod`, then scan top-level packages
4. **Read entry points directly** — don't glob entire trees. For each key module, use Read targeted at the file, not Agent/Explore.
5. **Report back** in ≤10 lines:
   - What the project does
   - Main entry point(s) and tech stack
   - Key directories to be aware of
   - Any open work visible in git status / recent commits

## Rules
- Use Glob or Grep for targeted lookups; never launch an Explore agent unless the project has >5 unknown directories.
- Read at most 5 files before reporting — if you need more, ask the user which area to focus on.
- Never re-read a file you already read this session.
