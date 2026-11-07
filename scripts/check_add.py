"""CI gate: an OpenSpec change with tasks or implementation needs an owner-approved add.md.

Rules for every change directory under openspec/changes/ touched by the pull request
and still present at HEAD:
  * if it has tasks.md, or add.md, or the PR also changes files outside openspec/,
    its add.md must contain the line `Approved-by: <ADD_APPROVER>`;
  * if that line was added by a commit of this PR (not already on the base branch),
    the commit must be authored by the GitHub user ADD_APPROVER and carry a
    GitHub-verified signature (an edit made in the GitHub web UI qualifies).
Pull requests that touch no OpenSpec change pass without an ADD.

Required environment: ADD_APPROVER, BASE_SHA, GITHUB_REPOSITORY, GITHUB_TOKEN.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

CHANGES = "openspec/changes/"


def env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        sys.exit(f"check_add: required environment variable {name} is not set")
    return value


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def change_dir(path: str) -> str | None:
    if not path.startswith(CHANGES):
        return None
    parts = path[len(CHANGES) :].split("/")
    if parts[0] == "archive":
        return CHANGES + "/".join(parts[:2]) if len(parts) > 2 else None
    return CHANGES + parts[0] if len(parts) > 1 else None


def approval_commit(add_md: Path, line: str) -> str | None:
    lines = add_md.read_text(encoding="utf-8").splitlines()
    if line not in (item.strip() for item in lines):
        return None
    number = next(i for i, item in enumerate(lines, 1) if item.strip() == line)
    blame = git("blame", "--porcelain", "-L", f"{number},{number}", "--", str(add_md))
    return blame.split()[0]


def github_commit(repo: str, sha: str, token: str) -> dict:
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/commits/{sha}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def main() -> int:
    approver = env("ADD_APPROVER")
    base = env("BASE_SHA")
    repo = env("GITHUB_REPOSITORY")
    token = env("GITHUB_TOKEN")
    approval_line = f"Approved-by: {approver}"

    changed = git("diff", "--name-only", f"{base}...HEAD").split()
    implementation = [p for p in changed if not p.startswith("openspec/")]
    touched = sorted({d for p in changed if (d := change_dir(p)) and Path(d).is_dir()})
    pr_commits = set(git("rev-list", f"{base}..HEAD").split())

    if not touched:
        print("check_add: no OpenSpec change in this PR; no ADD required")
        return 0

    errors = []
    for directory in touched:
        path = Path(directory)
        add_md = path / "add.md"
        reasons = [
            label
            for label, hit in (
                ("it has tasks.md", (path / "tasks.md").exists()),
                ("it has add.md", add_md.exists()),
                ("the PR changes implementation files", bool(implementation)),
            )
            if hit
        ]
        if not reasons:
            print(f"check_add: {directory}: proposal only, no ADD required yet")
            continue
        why = ", ".join(reasons)
        if not add_md.exists():
            errors.append(f"{directory}: add.md is missing ({why}); write the ADD first")
            continue
        sha = approval_commit(add_md, approval_line)
        if sha is None:
            errors.append(
                f"{directory}: add.md has no line '{approval_line}' ({why}); "
                "the change waits for the owner to approve the ADD"
            )
            continue
        if sha not in pr_commits:
            print(f"check_add: {directory}: approved on the base branch ({sha[:10]})")
            continue
        commit = github_commit(repo, sha, token)
        login = (commit.get("author") or {}).get("login")
        verified = commit["commit"]["verification"]["verified"]
        if login != approver or not verified:
            errors.append(
                f"{directory}: approval line was added by commit {sha[:10]} "
                f"(author login {login!r}, verified signature {verified}); it must be a "
                f"verified commit by {approver}, e.g. an edit made in the GitHub web UI"
            )
            continue
        print(f"check_add: {directory}: approved by {approver} in {sha[:10]}")

    for error in errors:
        print(f"::error::ADD gate: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
