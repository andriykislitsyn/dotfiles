# How I Set Up Claude Code

I've been using Claude Code daily for months. This is how I've configured it to work the way I think, not the other way around.

## The Global CLAUDE.md

The most impactful thing you can do is write a global `~/.claude/CLAUDE.md`. This file is loaded into every conversation across every project. It's where you define how Claude should behave as your collaborator.

Mine covers:

- **Intellectual honesty** — don't agree to be agreeable, push back when I'm wrong, no flattery
- **Response style** — concise, no filler, no trailing summaries
- **Code quality** — minimize changes, no over-engineering, no error handling for impossible cases
- **Git workflow** — always ask before committing or pushing, always review before creating PRs

The full file is in [claude-code/CLAUDE.md](../claude-code/CLAUDE.md). The key insight: treat it like onboarding a new team member. Tell them your actual preferences, not the "correct" ones.

### Project-Level CLAUDE.md

Each repo can also have a `CLAUDE.md` at its root with project-specific instructions: how to run tests, which patterns to follow, what tools to use. These stack on top of the global file.

Good things to put in a project CLAUDE.md:

- How to activate the virtual environment
- Test commands (`pytest`, `npm run test`, etc.)
- Linting commands to run after changes
- Architecture notes that aren't obvious from the code
- Patterns to follow (or avoid) in this specific repo

## Model and Effort

In `~/.claude/settings.json`:

```json
{
  "model": "claude-opus-4-6[1m]",
  "effortLevel": "high"
}
```

I use Opus mostly as the high efficient and moderately cheap model. The 1M context window matters for large monorepos where you need the model to hold multiple files in context. The `high` effort level makes Claude think longer before acting, worth it for complex tasks.

## Permissions

Claude Code asks permission before running commands. You can pre-approve safe patterns in `settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(cat:*)",
      "Bash(find:*)",
      "Bash(grep:*)",
      "Bash(git status:*)",
      "Bash(git diff:*)",
      "Bash(git log:*)",
      "Bash(ls:*)",
      "Bash(wc:*)",
      "Bash(python3:*)",
      "Bash(pytest:*)",
      "Bash(npm run lint:*)",
      "Bash(npm run jest:*)"
    ]
  }
}
```

The pattern is `Tool(command:*)` where `:*` is a suffix wildcard. I allow read-only commands freely and keep write operations (git push, rm, file creation) behind approval. Start conservative and add rules as the permission prompts get annoying for commands you always approve.

**Gotcha**: compound commands (`cmd1 && cmd2`) are split — each subcommand needs its own rule. Commands with `cd` always prompt regardless of rules (known upstream issue).

## Plugins

Claude Code has a plugin system. These are the ones I use:

- **superpowers** — brainstorming, debugging, TDD, and verification workflows. The brainstorming skill forces you to think through design before jumping to code. The verification skill makes Claude prove things work before claiming they do.
- **code-review** — automated code review before PRs. Catches things you miss after staring at the same code for hours.
- **pr-review-toolkit** — specialized PR review agents (type design, silent failure hunting, test coverage analysis).
- **remember** — persistent memory across sessions. Claude saves context about your project and preferences so you don't re-explain things.
- **claude-md-management** — helps maintain CLAUDE.md files as your project evolves.

Install plugins with:

```bash
claude plugins:add <plugin-name>
```

## Skills

Skills are markdown files that teach Claude specific workflows. They live in `~/.claude/skills/` and activate when relevant.

Some skill patterns that work well:

- **systematic-debugging** — forces a structured approach (reproduce → hypothesize → verify) instead of shotgun fixes
- **test-driven-development** — writes tests before implementation, catches scope creep
- **verification-before-completion** — runs actual verification commands before claiming work is done
- **python-logging** — enforces consistent logging patterns across the codebase

You can write your own skills or install them from repos:

```bash
ln -s /path/to/repo/skills/skill-name ~/.claude/skills/skill-name
```

## Additional Working Directories

If you work across multiple repos (monorepo + satellite repos, forks, docs), tell Claude about them:

```json
{
  "permissions": {
    "additionalDirectories": [
      "/path/to/other-repos/",
      "/path/to/forks/",
      "/tmp"
    ]
  }
}
```

This lets Claude read and search across your entire workspace, not just the current directory.

## What Actually Changed My Workflow

The config above is important but the real shift was behavioral:

1. **I stopped writing code first.** I describe what I want, let Claude draft it, then review. My job shifted from typing to reviewing and directing.

2. **I use Claude for research before decisions.** "Search the codebase for how X is done" is faster and more thorough than doing it myself.

3. **I treat the CLAUDE.md like a living doc.** When Claude does something I don't like, I add a rule. When it does something surprisingly good, I add a rule to keep doing it. The file evolves with every session.

4. **I delegate code review.** Before pushing, I have Claude review its own work with a fresh context (subagent). It catches real issues, not just style nits, but logic bugs and missing edge cases.

5. **I let Claude manage its own memory.** The remember plugin saves project context across sessions. Instead of re-explaining "we're migrating from X to Y" every time, it just knows.

The full config files are in [claude-code/](../claude-code/).
