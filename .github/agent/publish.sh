#!/usr/bin/env bash
# Publish the agent's work: guards, push, PR, auto-merge or ADD hand-off.
# The workflow copies this file from main to $RUNNER_TEMP before the agent runs,
# so edits on the agent branch cannot change what runs.
# Usage: agent_publish.sh <route> <pr-title> <summary>
set -euo pipefail
route=${1:?route is required}
title=${2:?pr title is required}
summary=${3:?summary is required}
: "${ISSUE:?ISSUE is not set}" "${PHASE:?PHASE is not set}" "${BRANCH:?BRANCH is not set}"
: "${START_SHA:?START_SHA is not set}" "${GH_TOKEN:?GH_TOKEN is not set}"

case "$PHASE:$route" in
  go:direct|go:openspec|apply:implemented) ;;
  *) echo "publish: route $route is not publishable in phase $PHASE" >&2; exit 1 ;;
esac
[ "$(git rev-parse --abbrev-ref HEAD)" = "$BRANCH" ] || { echo "publish: not on $BRANCH" >&2; exit 1; }
[ -z "$(git status --porcelain)" ] || { echo "publish: uncommitted changes" >&2; git status --porcelain >&2; exit 1; }
[ "$(git rev-parse HEAD)" != "$START_SHA" ] || { echo "publish: no new commit" >&2; exit 1; }
if git diff --name-only origin/main...HEAD | grep -E '^(\.github/|scripts/check_add\.py$)' >&2; then
  echo "publish: protected files changed (listed above)" >&2; exit 1
fi

git push origin "$BRANCH"
if [ "$PHASE" = go ]; then
  gh pr create --base main --head "$BRANCH" --title "$title" \
    --body "$(printf 'Closes #%s\n\n%s\n\nRoute: %s' "$ISSUE" "$summary" "$route")"
fi
pr=$(gh pr view "$BRANCH" --json url --jq .url)
if [ "$route" = openspec ]; then
  gh issue comment "$ISSUE" --body "ADD ready for owner review: $pr. Approve by adding the line \`Approved-by: lehard\` to add.md in the GitHub web UI, then add the label \`agent:apply\` to this issue."
  echo "publish: ADD hand-off posted for $pr"
else
  gh pr merge "$pr" --auto --squash
  echo "publish: auto-merge armed on $pr"
fi
