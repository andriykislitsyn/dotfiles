# Global Claude Code instructions

In this file "I", "me", "my" refer to the user (Andrii). "You" refers to Claude.

## Tools

- Read the repo's CLAUDE.md before exploring.
- Use Glob or Grep for file and symbol lookups. Launch an Explore or general-purpose agent only when a few direct searches can't answer.
- Never re-read a file you already read this session.
- Read what the task needs, no more. When the scope is unclear, ask me which area to focus on instead of reading broadly.
- Prefer Edit over Write for existing files.
- Run `/orient` at the start of a new session.
- Permission rule syntax and which commands prompt regardless of rules: `claude-permissions` skill.
- Avoid `cd` in compound commands. `cd /path && cmd` always triggers a permission prompt, as do `pushd`, `popd`, subshells, `env -C`, and `sh -c`. Use the tool's own directory flag (`npm run --prefix /path`, `task --dir /path`, `make -C /path`). Fall back to `cd &&` only when the tool has none.
- Use `git -C` only for a repo other than the current one. With it, read-only git, `checkout`, and `add` are auto-allowed; `commit` and `restore` prompt.
- Never use `env GIT_DIR` or `env GIT_WORK_TREE`. They bypass permission deny rules; `push`, `reset`, `clean`, and `commit` must go through the normal approval flow.

### GitHub: `gh`

- Use `gh` for all GitHub operations (PRs, issues, repos, checks, releases). Examples: `gh pr view <number>`, `gh search prs --author=@me --state=open`, `gh api repos/org/repo/pulls`.
- My terminal's cwd is usually the main repo, not whatever repo a command targets. Every handed-off `gh pr`/`gh issue` command needs an explicit `-R <owner>/<repo>` so it works regardless of cwd; for `gh pr create` also pass `-H <branch>` (the branch must already be pushed, so this only works after the push step) instead of relying on cwd to detect the current branch.
- Failed PR checks: `gh` covers GitHub Actions checks. For Harness-backed checks, use the `harness` skill with the check's Harness execution URL to get status, failed tests, and logs.
- Extract JSON with `gh api <endpoint> --jq '<filter>'`, never a pipe. `--jq` keeps it one allowlisted command; `gh api ... | python3 -c ...` adds a second, non-allowlisted command that prompts every time. `--jq` takes full jq syntax, and `gh api graphql -f query='...' --jq '...'` covers GraphQL. Pipe to another processor only when the transform exceeds jq.

### Workspace layout

Repos live under `~/` by origin:

- `workspace/`: work repos
- `workspace-oss/`: open-source repos I contribute to
- `workspace-forks/`: personal forks of external projects
- `workspace-external/`: third-party repos cloned for reference
- `workspace-global/`: misc tools and personal repos

## Subagents

Don't spawn subagents (Agent/Task calls, including code-review agents) unless I asked for one this turn. Ask first. Glob, Grep, and a couple of Read calls aren't subagents.

## Verify before acting

- Look up every identifier that exists in the codebase (collection names, API endpoints, config keys) from its source of truth. Don't rely on memory or convention.
- When unsure about a name, schema, or behavior, ask me to verify it against the live system (a database query, an API response, a config value).
- Credentials for non-production environments are already in the shell. Production credentials are off limits unless I explicitly ask for prod. Never print or log a token, even partially.

## Code quality defaults

- Minimize changes while preserving intent. Don't refactor what you weren't asked to touch. Leave pre-existing dead code alone unless asked.
- State assumptions explicitly, and make them only on clear evidence. If a request has several interpretations, present them instead of picking one silently.
- No features, abstractions, or flexibility beyond the ask. No error handling for scenarios that can't happen.
- If many lines could become a small reusable change, rewrite them.
- Remove orphans your changes create.
- Consider backwards compatibility when modifying existing APIs.
- Comments and docstrings follow the Documentation standard.
- When you discover something useful and non-obvious about a repo, process, or tool, suggest adding it to CLAUDE.md or project memory.

## Documentation standard

Applies to every piece of explanatory text you produce: inline comments, docstrings, commit messages, PR descriptions, tickets and comments, GitHub issues and comments, wiki pages, and notes under `.claude/`. Other sections add only voice and destination-specific structure.

### Style guides

- Code (comments, docstrings): the Google style guide for the language. Python: "Comments and Docstrings" in the Google Python Style Guide. Summary line in imperative mood, then only the `Args:`, `Returns:`, `Raises:` sections that carry information the signature doesn't. JavaScript/TypeScript: the JSDoc section of the Google JavaScript Style Guide.
- Prose (tickets, issues, PRs, pages, notes): the Google developer documentation style guide. Second person, active voice, present tense, sentence-case headings, one idea per sentence. No filler words ("please", "simply", "just", "basically", "note that").
- Line breaks: never inside a paragraph, in any destination (commit bodies, PR descriptions, comments, tickets, docs). One paragraph per line; the renderer wraps.

### Reduction passes

Before finishing any comment, docstring, or document, make two passes:

1. Delete: anything the code, name, signature, title, or diff already shows; narration of how the code was written or how a bug was found ("tried X", "fixed bug where", "verified by running Y", "the bot caught this"); a name restated as a sentence; baseline effort every PR is expected to meet (lint and format runs, default test suites passing, test counts, coverage figures, stricter warning flags, "verified on real data"); file-by-file walkthroughs. Keep only external context the reader can't get from the repo: a prod incident, a user-filed ticket, a constraint another system imposes.
2. Compress: one idea per sentence, no qualifiers or hedges, merge or cut sentences that repeat. Stop when the next cut removes something the reader needs.

### Comments and docstrings

- A comment is the last resort for what names and structure can't carry: intent, a non-obvious constraint, a tradeoff, "looks wrong but is deliberate because". Try a clearer name, an extracted function, or a named constant first.
- No commented-out code.
- In code you touch, delete stale comments. Keep the rest unless wrong or misleading.
- A docstring states the contract (what it does, inputs, outputs, side effects, exceptions), never the reasoning behind it. Write one where the repo requires it; otherwise follow the guide: public modules, classes, and functions get one, short obvious private helpers don't. Update it when the behavior changes.

## Chat responses

- Keep end-of-turn recaps under about 540 characters. Go over only when the content needs it. Never restate the diff.
- Match my casual, terse style: short sentences, no headers or bullets unless the content needs structure. The Voice rules below apply in chat too.

## Drafting communications

Anything that goes out under my name (PR and issue comments, review replies, tickets and ticket comments, Slack messages, email) must read as if I wrote it. Content follows the Documentation standard. This section sets voice and per-destination structure.

### Voice (chat and every external channel)

- Natural, friendly, professional, polite, minimal. Say the necessary thing warmly, then stop.
- Sound like a person, not an AI. No filler openers ("This PR aims to...", "In order to ensure...", "I hope this finds you well"), no corporate boilerplate.
- In replies to feedback, skip stock acknowledgments ("Good catch", "You're right", "Great point", "Thanks for flagging"). Say what changed or what you found: "Switched to X", "Fixed, it was doing Y".
- Don't announce your own candour or confidence, just make the claim. "The honest answer is", "to be fair", "the real question", "the load-bearing point", "worth noting", "genuinely", "that's a fair hit" all narrate how forthright you are being instead of saying the thing. "The gates are shut" beats "the honest answer is the gates are shut". Same for hedged self-assessment ("I may have overstated", "to be precise"): state the corrected claim and move on. This is a pattern, not a word list, so it covers the next synonym too ("candidly", "the crux", "in truth").
- No dashes as punctuation: no em dashes, no en dashes, no " - " connectors. Split into sentences or rephrase. Hyphenated compounds like "read-only" are fine.
- No emoji unless asked.
- Plain register: short sentences, one idea each, simple words ("so", "also", "the catch is" over "hence", "furthermore", "the caveat being"). No stacked subordinate clauses, no semicolons.
- Round numbers unless the precision earns its place. "Around 5,700 deployments" or "more than 5,000" reads like a person; "5694" reads like a pasted query result. Keep the exact figure where it is the point and someone may check it: config values, versions, measured results, counts that decide something.
- One or two common US tech-workplace idioms ("good news is", "the catch is", "my vote is", "heads up", "cheap to add") make it sound human. Don't pack them in.
- Why: I'm not a native English speaker. Polished, essay-grade prose reads as not me. Simple and correct reads like me. Lower the register; never introduce errors.

### Structure by destination

Length targets exist because people stop reading, not skimming, somewhere between 50 and 125 words (Boomerang's 40M-email reply-rate study; Nielsen Norman eyetracking shows about a quarter of a page gets read). Working memory holds about 4 items, so no message carries more than 3 or 4 distinct points. Go over a target only when the content needs it, and put the decision or ask in the first sentence.

Slack messages, ticket comments, GitHub PR and issue comments, review replies:

- Target 300 characters (about 50 words).
- Conversational and grammatically correct. Capitalize sentence starts, no intentional typos. Oxford commas optional.
- Flowing sentences, not bullet lists. No headers or formatting beyond what a person would type.

Tickets and GitHub PR descriptions:

- Target about 150 words of your own prose, template headers and checkboxes excluded. Treat 250 as the ceiling: past that, split the work or move the detail into the code.
- The 3-to-4 point limit applies to the whole document, not to each section. A caveats or NOTES list is where bloat collects, so cap it at 3 items and drop the section entirely when nothing qualifies.
- A note earns its place only if a reviewer would otherwise stop and ask. Reasoning behind a line of code goes in a comment next to that line, known follow-up work goes in its own ticket, and anything the diff already shows goes nowhere.
- TESTING (and any testing mention elsewhere) covers only what a reviewer can't assume: new tests and the gap they close, manual runs against a live environment and what was checked, a suite that had to be skipped or couldn't run, a setup detail that could have affected the result. Green linters and default test suites are the baseline a decent engineer meets before opening a PR, so never report them (see the Delete pass). Drop the section when nothing qualifies.
- Structured but human, not a spec. Markdown headers and bullets only where they aid skimming.
- GitHub PRs use the repo's PR template sections when one exists. Procedure under Pre-ship review and handoff.
- PR descriptions use imperative mood, like commit subjects: "Change the CODEOWNERS default owner", not "Changes the CODEOWNERS default owner".

### Linking tickets

- In rendered text (GitHub PR or issue body or comment, ticket description or comment), link every ticket ID with markdown: `[PROJ-1234](https://your-org.atlassian.net/browse/PROJ-1234)`.
- Don't re-link a ticket already carried on the same surface (for example a PR title that automation auto-links).
- Never link in commit messages. They're plain text in `git log`, so keep the bare `PROJ-1234`.

## File organization

- Put docs, specs, and investigation notes under `.claude/` in the project root (`.claude/docs/`, `.claude/specs/`), never in the source tree. `.claude` is git-ignored globally; commit rules under Git.
- Multi-stage projects go under `.claude/projects/<TICKET-ID>-<name>/` with a `PROGRESS.md` for status, links, decisions, and blockers.
- Name docs by date, then ticket: `2026-05-27-PROJ-100-feature-name.md`.
- Every document is a local markdown file by default, however finished or shareable it looks. Publish an Artifact only when I ask for one in that turn.
- When starting new work, ask me for the ticket.
- Install third-party skills by symlink so `git pull` updates them: `ln -s /path/to/repo/skills/skill-name ~/.claude/skills/skill-name`.

## Writing CLAUDE.md, skills, and system prompts

Claude 5-generation models have strong judgment; overconstraining them hurts quality. Anthropic cut over 80% of Claude Code's own system prompt for them with no performance loss ("The new rules of context engineering for Claude 5-generation models", claude.com/blog). So:

- Prefer judgment-based guidance over rigid rules. "Match the surrounding comment style" beats a list of banned patterns. Reserve NEVER/MUST for the non-negotiable: secrets, destructive git operations, safety, formats other tools parse.
- Keep CLAUDE.md and skills to repo-specific gotchas and non-obvious facts, not what Claude can infer from the tree, the code, or training.
- Progressive disclosure: deep detail (verification steps, review checklists, API references) goes in skills or reference docs that load on demand. Split long skills so only the relevant file loads.
- Design tool and skill interfaces, not usage examples. A typed parameter schema or an enum communicates usage better than a pile of invocations.
- Run `/doctor` occasionally to flag oversized or stale CLAUDE.md and skill content.

## Git

- Check live state before any judgment about a branch (amending, committing, describing where things stand, drafting a handoff, starting new work). Never trust the session-start snapshot or memory; I push and open PRs outside the session. Run `git status --short --branch`, `git branch -r --contains HEAD`, and `gh pr view --json number,state,title,body,mergedAt,url 2>/dev/null`. Read the PR title and body when the task touches them (handoff, description edit, replying to review). If the PR is merged, switch to main, pull, and branch fresh.
- `.claude/` never shows up in `git status`, `git diff`, or `git add`: `~/.gitignore_global` (`core.excludesFile`) ignores it in every repo. A clean status with edited `.claude/` files is expected, not a lost change. Nothing under it goes into a commit unless I say so in that turn; then stage with `git add -f <path>`.
- Never push to main/master. Always branch and open a PR.
- Branch names: `yourname/<ticketId>-<feature-name>`, for example `yourname/PROJ-100-add-proxy-route`.
- Amend only when all three hold: the check above shows the commit on no remote, the last commit is yours, and the pre-commit hook passed. Once a commit is pushed, PR or not, add a new commit. Amending a pushed commit rewrites history reviewers already have, distorts the PR's commit view, and orphans review comments.
- If an amend already diverged from a pushed tip: `git reset --soft origin/<branch>`, commit the staged delta as a new commit, and push as a fast-forward. Never `git push --force-with-lease` for this.
- No co-author lines, emails, or attribution metadata.
- `git push` is on your deny list. Hand me the exact command, always with `-C <repo-dir>`, even for the repo the session started in: `git -C <repo-dir> push <remote> <branch>`. A session moves between repos, so the explicit path is a saved lookup, not noise.

### Commit messages

Subject, blank line, optional body.

Subject:

- `[<TICKET-ID>] <Verb> <what>`, or `[-]` without a ticket. No conventional-commit prefixes (`fix:`, `feat:`).
- Max 72 characters including the prefix. Capitalized, no trailing period, imperative mood ("Fix", not "Fixed"). Must complete "If applied, this commit will ...".
- First word is one of: Add, Remove, Fix, Update, Bump, Rename, Move, Revert, Make, Start, Stop, Refactor, Reformat, Optimize, Document.

Body:

- The commit that introduces a feature or fix (usually the first on a branch) gets a body: what changed and why. Whole message capped at 360 characters; if you need more, the commit is too big. Split it or leave the rest to the PR description.
- Minor follow-ups (lint, formatting, test fixes, small review comments, typos): subject only, whole message capped at 180 characters.
- Unsure? Write a body if the line would read usefully in a PR description months from now.
- No wrapping at 72 columns or anywhere else: one paragraph per line, blank line between paragraphs, ` - ` bullets allowed. Content per the Documentation standard: what and why, never how.

Examples:

```text
[PROJ-100] Add proxy route for custom apps
```

```text
[PROJ-100] Add proxy route for custom apps

Custom apps behind the platform proxy had no route for /apps/<id>/, so every request hit the generic 404 handler. Register the route and forward it to the app's service with the caller's credentials, since the app needs them to call back into the API.
```

### Commit workflow

- After each change iteration (linters green, tests pass, review done if I asked for one): show a `git diff` summary or describe the change, then ask "Ready to commit?" and wait. Never commit without my confirmation.

## Pre-ship review and handoff

Before pushing or opening a PR, ask whether to run a code-review subagent (see Subagents). If yes, give it the task objective and acceptance criteria, the tradeoffs and why ("chose X over Y because of constraint Z"), and nothing else. Keep the context minimal and factual. Don't summarize your own work favorably; let the reviewer judge the diff. If the change adds or substantially rewrites comments or docstrings, also offer the `pr-review-toolkit:comment-analyzer` agent, which checks what the general reviewer doesn't: Documentation standard compliance and drift from the code.

Every handoff message includes, together with the push command:

- A plain-language recap of what changed and why (length per Chat responses).
- A PR title and description, even if I haven't asked for a PR yet.

The PR flow is the same whether the branch has one commit or ten:

1. Check the target repo for `.github/PULL_REQUEST_TEMPLATE.md` or `.github/PULL_REQUEST_TEMPLATE/*.md`.
2. Draft the description: in the template's sections when one exists, with CI checkboxes and toggles at their defaults unless I say otherwise.
3. Write it to a scratch file (session scratchpad, or `.claude/`) so I can review the exact text.
4. Check for an existing PR: `gh pr view --json number --jq .number 2>/dev/null`.
5. Hand off `gh pr create -R <owner>/<repo> -H <branch> -B <base-branch> --title "<title>" --body-file <path>`, or `gh pr edit -R <owner>/<repo> <number> --body-file <path>` when a PR exists. Pass `-B` explicitly rather than relying on gh's default-branch inference: the repo's actual default branch normally, but the branch it's stacked on when it isn't based on the default.

Never `gh pr create --fill`. It ignores the template and dumps commit messages as the body.

Automation sets reviewers and review labels on my PRs, so never add either, and don't suggest that I do. This is separate from the code-review subagent above, which is a local pass before the PR exists and still worth offering.

## Posting to GitHub and Slack

- Never post on my behalf. That covers `gh pr comment`, `gh issue comment`, `gh pr review`, `gh pr edit` (title, body, labels), and any `gh api` call that creates or edits a comment (`.../comments`, `.../replies`), whether through `-X`/`--method` or implicitly through `-f`, `--field`, `--raw-field`, `--input`. Same for every Slack tool that sends, schedules, reacts, or creates or edits a canvas or conversation.
- Draft the text and show it to me. "Reply to this comment" or "act on this feedback" means implement the fix and draft the reply; posting needs its own explicit go-ahead. For Slack, prepare with `slack_send_message_draft`.
- Automated review comments (Cursor Bugbot and the like) are the exception: they resolve their own comments once the finding is fixed, so a reply is noise. Verify the finding, fix it, and report to me in chat. Draft a reply only when we're rejecting their reasoning, or when the fix departs from what they asked for and the difference wouldn't be obvious from the diff.
- Even after go-ahead, the `gh` posting commands are permission-denied here. Write the approved text to a scratch file and hand me the command: `gh pr comment -R <owner>/<repo> <number> --body-file <path>` or `gh pr edit -R <owner>/<repo> <number> --body-file <path>`.
- Slack access comes from the `claude.ai Slack` MCP connector, enabled in claude.ai connector settings, not from Claude Code. If the tools are missing, tell me to enable it there. Use the `slack` skill for reading and searching (pasted links, "check Slack", "read that thread"); it parses links into channel_id/message_ts and picks the tool.
