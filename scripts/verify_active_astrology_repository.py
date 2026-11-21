#!/usr/bin/env python3
"""Preflight for canonical PUBLIC astrology research Git writes.

This is deliberately independent of network/API credentials and other private
repositories. It must fail when invoked inside the superseded HD repository,
even if a stale prompt, handoff, or local directory name suggests otherwise.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess

CANONICAL = "u-dont-existDOTcom/astro-research"
SENTINEL = "ASTRO_RESEARCH_CANONICAL=u-dont-existDOTcom/astro-research"


def normalized_remote(url: str) -> str:
    url = url.strip().rstrip("/")
    if not url:
        raise ValueError("No origin remote configured")
    # Handles git@github.com:owner/repo.git, ssh://, https://github.com...
    val = re.match(
        r"^(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)([^/\s:]+)/([^/\s]+?)(?:\.git)?$",
        url,
        re.IGNORECASE,
    )
    if not val:
        raise ValueError("Unrecognized GitHub origin; do not assume active repository")
    return f"{val.group(1)}/{val.group(2)}".removesuffix(".git").lower()


def verify(root: Path) -> dict:
    root = root.resolve(strict=True)
    if not (root / ".git").exists():
        # Worktrees may use a .git text pointer, so only require existence.
        raise ValueError("Directory is not a Git checkout")
    proc = subprocess.run(
        ["git", "-C", str(root), "remote", "get-url", "origin"],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise ValueError("No origin GitHub remote")
    observed = normalized_remote(proc.stdout)
    expected = CANONICAL.lower()
    if observed != expected:
        raise ValueError(f"Wrong canonical astrology destination: {observed}; expected {expected}")
    agent = root / "AGENTS.md"
    if not agent.is_file() or SENTINEL not in agent.read_text(encoding="utf-8"):
        raise ValueError("Missing current astro-research AGENTS.md repository sentinel")
    if not (root / "state" / "CURRENT-STATE.md").exists():
        raise ValueError("Missing active repository research checkpoint")
    return {
        "status": "CANONICAL_PUBLIC_ASTRO_RESEARCH_CHECKOUT",
        "origin_repository": observed,
        "repository_sentinel_present": True,
        "no_legacy_hd_write_path": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(verify(args.root))


if __name__ == "__main__":
    main()
