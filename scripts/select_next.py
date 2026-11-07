"""Pick the next requirement from the project board and hand it to the agent.

Reads the user-owned Projects v2 board, and when no requirement is in flight
(an open `type:requirement` Issue labelled `agent:go`), labels the open Todo
requirement with the lowest Priority with `agent:go`.

Required environment: BOARD_TOKEN, BOARD_OWNER, BOARD_NUMBER, GITHUB_REPOSITORY.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request

QUERY = """
query($owner: String!, $number: Int!) {
  user(login: $owner) {
    projectV2(number: $number) {
      items(first: 100) {
        nodes {
          status: fieldValueByName(name: "Status") {
            ... on ProjectV2ItemFieldSingleSelectValue { name }
          }
          priority: fieldValueByName(name: "Priority") {
            ... on ProjectV2ItemFieldNumberValue { number }
          }
          content {
            ... on Issue {
              number state repository { nameWithOwner }
              labels(first: 20) { nodes { name } }
            }
          }
        }
      }
    }
  }
}
"""


def env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        sys.exit(f"select_next: required environment variable {name} is not set")
    return value


def call(token: str, url: str, payload: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def main() -> int:
    token = env("BOARD_TOKEN")
    owner = env("BOARD_OWNER")
    number = int(env("BOARD_NUMBER"))
    repo = env("GITHUB_REPOSITORY")

    data = call(
        token,
        "https://api.github.com/graphql",
        {"query": QUERY, "variables": {"owner": owner, "number": number}},
    )
    if "errors" in data:
        sys.exit(f"select_next: board query failed: {data['errors']}")
    project = data["data"]["user"]["projectV2"]
    if project is None:
        sys.exit(f"select_next: project {owner}/{number} not found or not readable")

    requirements = []
    for item in project["items"]["nodes"]:
        issue = item["content"]
        if not issue or issue.get("repository", {}).get("nameWithOwner") != repo:
            continue
        labels = {label["name"] for label in issue["labels"]["nodes"]}
        if "type:requirement" not in labels or issue["state"] != "OPEN":
            continue
        requirements.append((issue["number"], labels, item["status"], item["priority"]))

    in_flight = [n for n, labels, _, _ in requirements if "agent:go" in labels]
    if in_flight:
        print(f"select_next: requirement in flight: #{in_flight[0]}; nothing to start")
        return 0

    todo = []
    for n, _, status, priority in requirements:
        if status is None:
            sys.exit(f"select_next: issue #{n} has no Status on the board")
        if status["name"] != "Todo":
            continue
        if priority is None:
            sys.exit(f"select_next: Todo issue #{n} has no Priority on the board")
        todo.append((priority["number"], n))
    if not todo:
        print("select_next: no Todo requirement on the board")
        return 0

    _, chosen = min(todo)
    call(
        token,
        f"https://api.github.com/repos/{repo}/issues/{chosen}/labels",
        {"labels": ["agent:go"]},
    )
    print(f"select_next: labelled #{chosen} with agent:go")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
