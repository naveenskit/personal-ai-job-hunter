Push helper and PR creation

Files added:
- `scripts/push_and_pr.ps1` — PowerShell helper to install `gh`, authenticate, push the current branch, and open a PR.
- `files/PR_BODY.md` — Suggested PR body to use with `gh pr create` or copy into the web UI.

How to run (from repo root, PowerShell):

```powershell
# run the helper (may prompt for browser auth)
powershell -ExecutionPolicy Bypass -File .\scripts\push_and_pr.ps1

# or run with explicit branch/remote
powershell -ExecutionPolicy Bypass -File .\scripts\push_and_pr.ps1 -RepoUrl https://github.com/naveenskit/Consolidate-outreach-code-and-tests.git -Branch outreach/consolidate
```

If `gh` cannot be installed, use SSH instead:
- Generate SSH key: `ssh-keygen -t ed25519 -C "you@example.com"`
- Add key to ssh-agent: `Start-Service ssh-agent; ssh-add $env:USERPROFILE\.ssh\id_ed25519`
- Copy public key: `Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub` and paste to https://github.com/settings/keys
- Set remote to SSH: `git remote set-url origin git@github.com:naveenskit/Consolidate-outreach-code-and-tests.git`
- Push: `git push -u origin outreach/consolidate`

If you previously pasted a Personal Access Token into chat, revoke it now at https://github.com/settings/tokens.
