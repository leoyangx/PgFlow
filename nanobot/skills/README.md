# PgFlow Skills

This directory contains built-in skills that extend PgFlow's capabilities.

## Skill Format

Each skill is a directory containing a `SKILL.md` file with:
- YAML frontmatter (name, description, metadata)
- Markdown instructions for the agent

## Available Skills

| Skill | Description |
|-------|-------------|
| `github` | Interact with GitHub using the `gh` CLI |
| `weather` | Get weather info using wttr.in and Open-Meteo |
| `summarize` | Summarize URLs, files, and YouTube videos |
| `tmux` | Remote-control tmux sessions |
| `clawhub` | Search and install skills from ClawHub registry |
| `skill-creator` | Create new skills |

## Installing More Skills

Search and install skills from ClawHub (requires Node.js):

```bash
pgflow skill search "web scraping"
pgflow skill install web-scraper
pgflow skill list
```

Or place a `SKILL.md` file manually in `~/.pgflow/workspace/skills/<skill-name>/`.

## Writing Your Own Skill

Create a directory under `~/.pgflow/workspace/skills/<skill-name>/` with a `SKILL.md` file:

```markdown
---
name: my-skill
description: What this skill does
---

# My Skill

Instructions for the agent on how to use this skill...
```

The agent automatically picks up skills from the workspace directory.
