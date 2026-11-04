# GitHub Context Cheat Sheet for OpenCode

Copy-paste these `gh` commands to pull GitHub context into an OpenCode chat. Run them from the repo root in PowerShell.

## Authentication

```powershell
gh auth status
gh auth login
gh auth token
```

## Repository

```powershell
gh repo view --web
gh repo view pognoob321-boop/default-project --json name,description,defaultBranch,owner
gh repo list --limit 20
gh repo clone pognoob321-boop/default-project
```

## Issues (external task board / memory)

```powershell
gh issue list --state open --limit 20
gh issue list --state all --label "setup" --limit 50
gh issue view 123 --comments
gh issue create --title "Set up GitHub MCP server" --body "Configure github/github-mcp-server in OpenCode settings" --label "setup"
gh issue edit 123 --add-label "in-progress" --state closed
gh issue list --search "context decay" --state open
```

## Pull Requests

```powershell
gh pr list --state open --limit 20
gh pr view 5 --web
gh pr checks 5
gh pr merge 5 --squash --delete-branch
```

## Code Search

```powershell
gh api search/code -q 'repo:pognoob321-boop/default-project context-decay' --jq '.items[].html_url'
gh api search/code -q 'repo:pognoob321-boop/default-project session-state' --jq '.items[].html_url'
```

## API (arbitrary GitHub REST calls)

```powershell
gh api repos/pognoob321-boop/default-project/issues --jq '.[].title'
gh api repos/pognoob321-boop/default-project/contents/wiki/ai-memory/session-state.md --jq '.content' | base64 -d
```

## Workflows / Actions

```powershell
gh run list --limit 10
gh run view 1234567890 --log
gh workflow list
gh workflow run lint.yml
```

## Releases

```powershell
gh release list --limit 10
gh release view v1.0.0
```

## Quick aliases for OpenCode sessions

Save these as a PowerShell profile function or run inline:

```powershell
# Show all open issues with labels
gh issue list --state open --limit 30 --json title,number,labels,url --jq '.[] | "\(.number): \(.title) [\(.labels[].name)]"'

# Show recent PRs
gh pr list --state open --limit 10 --json title,number,headRefName,url --jq '.[] | "\(.number): \(.title) (\(.headRefName))"'

# Check repo health (security alerts, etc.)
gh api repos/pognoob321-boop/default-project --jq '.has_issues, .has_projects, .has_wiki, .archived, .disabled'
```

## Tips

- Pipe `gh` output through `ConvertFrom-Json` in PowerShell for structured parsing.
- Use `--json` + `--jq` for machine-readable output that OpenCode can read directly.
- Combine with `gh issue create` to log OpenCode findings as GitHub Issues (external memory).
- All `gh api` calls use your authenticated token from `gh auth login`.
