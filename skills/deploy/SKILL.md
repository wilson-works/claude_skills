---
name: deploy
description: Commit all staged/unstaged changes and push to GitHub to trigger a Railway deploy. Invoke with /deploy or /deploy [commit message].
---

# Deploy to Railway via GitHub Push

## Purpose

Commits current changes and pushes to GitHub, which triggers an automatic Railway deployment.

## Invocation

```
/deploy                          # Auto-generates commit message
/deploy fix the login bug        # Uses provided text as commit message
```

## Workflow

### 1. Check for changes

- Run `git status` and `git diff` to see what changed
- If there are no changes, tell the user there's nothing to deploy and stop

### 2. Commit

- If the user provided a message, use it as the commit message
- If not, analyze the diff and write a concise commit message
- Stage the specific files this change touches, by name. Never `git add -A` or
  `git add .` — in any clone more than one session writes, that publishes other
  sessions' work under your name.
- Commit with the message, appending `Co-Authored-By: Claude <noreply@anthropic.com>` (do not hardcode a model version — it goes stale)

### 3. Push

- Run `git push` to push to the current branch on GitHub
- Railway will automatically pick up the push and deploy

### 4. Confirm

- Tell the user the push succeeded and Railway should be deploying
- Do NOT check Railway status or wait for the deploy to finish

## Important Notes

- Do NOT ask the user for confirmation before committing/pushing — this skill is an explicit deploy request
- Do NOT run tests or builds locally — Railway handles the build
- If the push fails, report the error and suggest fixes
