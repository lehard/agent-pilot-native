# Agent instructions for requirement Issues

You run inside GitHub Actions on a branch the workflow prepared. You are told the
Issue number and the phase (`go` or `apply`). Read the Issue with `gh issue view <N>`.
The workflow pushes, opens the pull request and arms auto-merge; you never push.

## Phase `go`: choose the route

Choose **openspec** when the requirement needs a choice between materially different
approaches: a persistent data format or migration, a new dependency, or an Issue that
says a decision is needed before implementation. Otherwise choose **direct**.

### Route `direct`
1. Implement the requirement with tests and README updates where behaviour is visible.
2. Run `ruff check .`, `ruff format .` and `python -m pytest -q`; all must pass.
3. Commit everything with message `<summary> (#<N>)`.

### Route `openspec`
1. `npx -y @fission-ai/openspec@1.16.0 new change <change-id>` (kebab-case id).
2. Write, in order, the artifacts of schema `add-gated`: proposal.md, specs, design.md,
   add.md. Use `npx -y @fission-ai/openspec@1.16.0 instructions <artifact> --change <change-id>`
   for each artifact's rules.
3. In add.md leave the line `Approved-by:` empty. Never write an approval: only the
   owner approves, and CI rejects approvals not committed by the owner.
4. Do NOT write tasks.md or any code.
5. `npx -y @fission-ai/openspec@1.16.0 validate <change-id>` must pass. Commit with
   message `Propose <change-id> (#<N>)`.

## Phase `apply`

The branch holds an OpenSpec change whose add.md must contain `Approved-by: lehard`.
If it does not, stop at once with route `blocked`.
1. Write tasks.md following the decision in add.md.
2. Implement the tasks with tests, ticking each task in tasks.md.
3. `ruff check .`, `ruff format .`, `python -m pytest -q` and
   `npx -y @fission-ai/openspec@1.16.0 validate <change-id>` must pass.
4. `npx -y @fission-ai/openspec@1.16.0 archive <change-id> --yes`.
5. Commit with message `Implement <change-id> (#<N>)`.

## Always
- Never edit `.github/`, `scripts/check_add.py` or any `Approved-by:` line.
- No fallbacks: missing or invalid input fails with an explicit error.
- If you cannot finish (tests fail, requirement unclear), commit nothing and return
  route `failed` with the reason.
- Final answer: the structured output (route, change_id or empty, pr_title, summary).
