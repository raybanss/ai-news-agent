# AI News Agent

A daily news digest (AI/tech, healthcare IT + AI, markets/crypto/real estate)
delivered to Discord. Built as a **hybrid** because the remote routine that does
the AI work can't reach Discord directly (its sandbox blocks outbound webhooks).

## How it works

```
Claude Code routine (runs on Max plan, daily 7am ET)
  → web search, summarize, classify into a digest
  → writes digests/latest.md (message blocks split by a delimiter) and pushes to this repo
        │
        ▼
GitHub Action (post-digest.yml, fires on push to digests/latest.md)
  → post_to_discord.py reads the digest, splits on the delimiter,
    posts each block to Discord (webhook in Actions secrets)
```

The split: the AI/LLM work runs on the Anthropic Max subscription (the routine),
and delivery runs on GitHub Actions (which *can* reach Discord). No API cost.

## The digest file contract

`digests/latest.md` contains the full digest. Each intended Discord message is
separated by a line containing exactly:

```
===DISCORD-MESSAGE-BREAK===
```

The Action posts each block as its own message; any block over 2000 chars is
hard-split to respect Discord's limit. A dated copy is archived under
`digests/archive/YYYY-MM-DD.md`.

## Setup

The Discord webhook is stored as a repo secret (never committed):

```bash
gh secret set DISCORD_WEBHOOK_URL   # paste the webhook URL when prompted
```

The routine that feeds this repo: https://claude.ai/code/routines (AI News Daily Digest).

## Test delivery manually

Put any content (with delimiters) in `digests/latest.md`, push, and the Action
fires — or use the **Run workflow** button (workflow_dispatch) in the Actions tab.
