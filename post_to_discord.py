"""Read the latest digest and post it to Discord, split into <=2000-char messages.

The daily Claude Code routine writes `digests/latest.md`, separating each intended
Discord message with a line containing exactly the delimiter below. This script
(run by GitHub Actions on push) splits on that delimiter and posts each block —
hard-splitting any block that still exceeds Discord's 2000-char limit.

Uses only the Python standard library (no pip install needed).
"""

import json
import os
import sys
import time
import urllib.request

DIGEST_PATH = "digests/latest.md"
DELIMITER = "===DISCORD-MESSAGE-BREAK==="
DISCORD_LIMIT = 2000
SAFE_LIMIT = 1900  # leave headroom


def hard_split(text: str, limit: int = SAFE_LIMIT) -> list[str]:
    """Split text into <=limit chunks, preferring line boundaries."""
    chunks: list[str] = []
    current = ""
    for line in text.split("\n"):
        # A single line longer than the limit must be cut directly.
        while len(line) > limit:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(line[:limit])
            line = line[limit:]
        if len(current) + len(line) + 1 > limit:
            chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    if current:
        chunks.append(current)
    return chunks


def post(webhook: str, content: str) -> int:
    data = json.dumps({"content": content}).encode("utf-8")
    req = urllib.request.Request(
        webhook, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status


def main() -> None:
    webhook = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if not webhook:
        sys.exit("ERROR: DISCORD_WEBHOOK_URL secret not set.")
    if not os.path.exists(DIGEST_PATH):
        sys.exit(f"ERROR: {DIGEST_PATH} not found.")

    text = open(DIGEST_PATH, encoding="utf-8").read().strip()
    if not text:
        sys.exit("ERROR: digest is empty.")

    blocks = [b.strip() for b in text.split(DELIMITER) if b.strip()]
    messages: list[str] = []
    for block in blocks:
        messages.extend([block] if len(block) <= DISCORD_LIMIT else hard_split(block))

    for i, msg in enumerate(messages, 1):
        status = post(webhook, msg)
        print(f"posted {i}/{len(messages)} -> HTTP {status}")
        time.sleep(1)  # gentle on Discord rate limits

    print(f"Done: {len(messages)} message(s) posted.")


if __name__ == "__main__":
    main()
