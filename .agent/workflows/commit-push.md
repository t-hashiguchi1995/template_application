---
description: Commit current changes and push to the remote branch
---

# /commit-push

Commit all changes and push to the current remote branch.

## Steps

1. Check current branch — **STOP** if on `main` or `master`:

```bash
BRANCH=$(git branch --show-current)
echo "Current branch: $BRANCH"
```

If the branch is `main` or `master`, ask the user for confirmation before continuing. Direct pushes to main/master are strongly discouraged.

2. Review the actual diff:

```bash
git status
git diff
git diff --cached
```

3. (Optional) Run quality checks if available:

```bash
# Backend
uv run ruff check . && uv run pytest

# Frontend
npm run lint && npm run type-check && npm run test
```

4. Stage all changes:

```bash
git add -A
```

5. Write the commit message following the **Conventional Commits** format (see user_rules.md):

```bash
git commit -m "<prefix>: <summary>

- <change 1>
- <change 2>"
```

6. Push to remote:

```bash
git push origin $BRANCH
```

If the remote branch doesn't exist yet:

```bash
git push --set-upstream origin $BRANCH
```

## Notes

- **Branch protection**: Never push directly to `main` or `master` without explicit user approval.
- **Commit message**: Must be based on the **actual diff** (`git diff`, `git log`).
- **Quality checks**: Run linters and tests before pushing if available in the project.
- **Scope**: This command does NOT create a PR. Use `/commit-push-pr` for that.
