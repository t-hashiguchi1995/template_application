---
description: Commit current changes, push to remote branch, and create a Pull Request
---

# /commit-push-pr

Full workflow: commit all changes, push to remote, then create a Pull Request using GitHub CLI.

## Steps

### Phase 1: Pre-flight Checks

1. Check current branch — **STOP** if on `main` or `master`:

```bash
BRANCH=$(git branch --show-current)
BASE=$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name' 2>/dev/null || echo "main")
echo "Branch: $BRANCH, Base: $BASE"
```

If `$BRANCH == $BASE`, stop and ask user to create a feature branch first.

2. Check for uncommitted changes:

```bash
git status --porcelain
```

### Phase 2: Quality Checks (if applicable)

Run quality gates if available in the project:

```bash
# Backend (Python)
uv run ruff check . && uv run pytest

# Frontend (TypeScript/React)
npm run lint && npm run type-check && npm run test
```

Skip if tools aren't available or not applicable.

### Phase 3: Commit

3. Review the actual diff:

```bash
git diff
git diff --cached
git log $BASE..$BRANCH --oneline
```

4. Stage and commit following **Conventional Commits** format:

```bash
git add -A
git commit -m "<prefix>: <summary>

- <change 1>
- <change 2>"
```

### Phase 4: Push

5. Push to remote:

```bash
git push origin $BRANCH
# If first push to this branch:
# git push --set-upstream origin $BRANCH
```

### Phase 5: Create Pull Request

6. Review all commits and diff for the PR:

```bash
git log $BASE..$BRANCH --oneline
git diff $BASE...$BRANCH
```

7. Write the PR title and body based on the **actual diff** (see user_rules.md for PR format).

8. Create the PR (draft by default for review):

```bash
gh pr create \
  --draft \
  --base "$BASE" \
  --title "<prefix>(<scope>): <summary>" \
  --body "$(cat <<'EOF'
## 概要

[What this PR accomplishes]

## 変更内容

- [Specific change 1]
- [Specific change 2]

## テスト

- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] CI passes
EOF
)"
```

To create a non-draft (ready for review) PR, remove `--draft`.

### Phase 6: Report

9. Share the PR URL with the user:

```bash
gh pr view --web  # opens in browser
# or
gh pr view       # show in terminal
```

## Notes

- **Branch protection**: Never create PRs from `main`/`master` to itself.
- **PR message**: Must be generated from **actual diff** — never fabricate content.
- **Draft PRs**: Default to draft. Mark as ready for review when all checks pass.
- **GitHub CLI**: Requires `gh` to be authenticated. If not available, provide the manual URL.
- **Alternative (GitHub MCP)**: If `gh` CLI is unavailable but GitHub MCP is configured, use MCP tools to create the PR.

## Troubleshooting

If `gh` is not authenticated:
```bash
gh auth login
```

If PR already exists for this branch:
```bash
gh pr view  # see existing PR
# Update it if needed:
gh api -X PATCH repos/{owner}/{repo}/pulls/PR_NUMBER \
  -f title='new title' \
  -f body='new body'
```
