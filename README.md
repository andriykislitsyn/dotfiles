# dotfiles

My development environment configuration. macOS, zsh, and the tools I use daily as a Software Engineer working on platform infrastructure, observability, and CI/CD.

## What's Inside

```
zsh/          Shell configuration (Powerlevel10k, lazy-loading, aliases)
git/          Git aliases, delta pager, GPG signing
claude-code/  Claude Code: CLAUDE.md, settings.json, output style, /orient, skills (permissions, Harness, Slack)
scripts/      Utility scripts (linting, automation)
posts/        Pointers to the setup notes, now on Agentic Engineering
```

## Highlights

**Shell startup in ~140ms** — down from 5+ seconds. The main wins were lazy-loading NVM and virtualenvwrapper (they eagerly initialize on every shell, even when unused) and deduplicating `compinit` calls. Details in [Shell startup: from 5s to 140ms](https://andriykislitsyn.github.io/agentic-engineering/articles/zshrc-from-5s-to-140ms/).

**Lazy-load pattern** — NVM, virtualenvwrapper, and other heavy tools are wrapped in shell functions that replace themselves on first call:

```zsh
nvm() { unset -f nvm node npm npx; [[ -s "$HOME/.nvm/nvm.sh" ]] && . "$HOME/.nvm/nvm.sh"; nvm "$@"; }
```

First `nvm` call loads the real thing; every subsequent call is native speed.

**Git aliases for real workflows** — `git please` (force-with-lease), `git bonk` (push current branch), `git trim` (clean merged branches), `git lg` (compact colored log). Full list in [git/.gitconfig](git/.gitconfig).

**Delta as git pager** — side-by-side diffs with line numbers in the terminal. Once you try it, plain `git diff` feels broken.

**Modern CLI replacements** — `bat` for `cat`, `lsd` for `ls`, `ripgrep` for `grep`, `zoxide` for `cd`, `delta` for `diff`. All drop-in compatible with muscle memory.

**blort.sh** — runs `black`, `isort`, and `pylint` only on Python files changed in your PR or branch. No more linting the entire repo when you touched three files. Supports `--dry-run` and PR number lookup via `gh`.

**create_icons.sh** — generates a full macOS `.icns` icon set from any image using `sips`. Handy when you need app icons without opening a design tool.

## Posts

- [Shell startup: from 5s to 140ms](https://andriykislitsyn.github.io/agentic-engineering/articles/zshrc-from-5s-to-140ms/) — lazy-loading NVM/virtualenvwrapper, deduplicating compinit
- [Zsh setup with Oh My Zsh](https://andriykislitsyn.github.io/agentic-engineering/articles/zsh-setup-with-oh-my-zsh/) — Powerlevel10k, plugins, modern CLI replacements, full walkthrough
- [Signed Git commits with GPG](https://andriykislitsyn.github.io/agentic-engineering/articles/signed-git-commits/) — why and how to sign every commit
- [How I set up Claude Code](https://andriykislitsyn.github.io/agentic-engineering/articles/how-i-set-up-claude-code/) — permissions, output style, CLAUDE.md, and skills, each rule where it gets enforced

## Setup

These are reference configs, not an install script. Fork and adapt to your setup:

1. Review each file and replace placeholder values (marked with `# CHANGEME`) with your own
2. Symlink what you need: `ln -sf ~/dotfiles/zsh/.zshrc ~/.zshrc`
3. Install dependencies: `bat`, `lsd`, `ripgrep`, `delta`, `zoxide`, `fzf` (all via `brew`)

```bash
brew install bat lsd ripgrep git-delta zoxide fzf
```
