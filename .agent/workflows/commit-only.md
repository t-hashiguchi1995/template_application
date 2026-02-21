---
description: Commit current changes to the local branch (without pushing)
---

# /commit-only

Commit all staged or unstaged changes on the current branch without pushing to remote.

## Steps

1. Check the current branch and status:

```bash
git status
git branch --show-current
```

2. Review **all** actual code differences before writing the commit message:

```bash
git diff
git diff --cached
```

3. Stage all changes:

```bash
git add -A
```

4. Write the commit message following the **Conventional Commits** format from user_rules.md:
   - Prefix: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `style`, `perf`, `revert`
   - Summary: 50 chars max, no trailing period, what & why
   - Body: bullet-point list of specific changes (in Japanese by default)

5. Commit:

```bash
git commit -m "<prefix>: <summary>

- <change 1>
- <change 2>"
```

## Notes

- **Scope**: Local commit only. Does NOT push to remote.
- **Branch strategy**: Pushing and branch management are outside this command's scope.
- **Commit message**: Must be based on the **actual diff**, not assumptions.
- Never commit sensitive data (credentials, API keys, etc.).
