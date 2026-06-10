#!/bin/zsh
# Daily vault auto-commit + push for the WOBAR repo.
# Installed as launchd agent com.wobar.autocommit (5:00 AM daily).
# Replaces the Obsidian Git plugin auto-backup, which only ran while
# Obsidian was open and never pushed (dead since 2026-03-10).

REPO="/Users/nicholasrabow/Desktop/wobar/wobar"
GIT=/usr/bin/git

cd "$REPO" || { echo "$(date) repo missing: $REPO"; exit 1; }

echo "--- vault autocommit $(date '+%Y-%m-%d %H:%M:%S') ---"

$GIT add -A
if ! $GIT diff --cached --quiet; then
  $GIT commit -m "vault backup: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "committed: $($GIT log -1 --format='%h %s')"
else
  echo "nothing to commit"
fi

# Sync with remote; tolerate offline. Abort a half-done rebase so the
# repo is never left mid-rebase for the next interactive session.
if $GIT pull --rebase --autostash origin main; then
  $GIT push origin main && echo "pushed" || echo "push failed (offline?)"
else
  echo "pull failed — aborting any in-progress rebase, skipping push"
  $GIT rebase --abort 2>/dev/null
fi
