# Resetting the Repository

This document describes how to reset the repository to its initial state before starting a new competition.

## Overview

Resetting the repository removes:

- old team submissions
- old release data
- old scoring outputs
- old leaderboards

while preserving:

- repository structure
- documentation
- workflows
- validation scripts
- scoring scripts
- issue templates

## Step 1: Create a Backup

Before resetting, create a backup copy of the repository.

Recommended:

```bash
git tag competition-archive
git push origin competition-archive
```

## Step 2: Remove Team Submissions

Delete all prediction files from:

```text
predictions/
```

Keep empty folders or `.gitkeep` files if desired.

## Step 3: Remove Release Data

Delete all release folders under:

```text
data-release/
```

## Step 4: Remove Generated Scores

Delete generated scoring outputs:

```text
scoring/challenge-01/
scoring/challenge-02/
scoring/overall-leaderboard.csv
```

Keep:

```text
scoring/scripts/
```

## Step 5: Remove Generated Plots

Delete:

```text
scoring/plots/
workshop_data/plots/
```

## Step 6: Recreate Empty Output Folders

Recreate required folders and optional `.gitkeep` files.

## Step 7: Recreate Initial Release Folders

Create:

```text
data-release/challenge-01/release-01/
data-release/challenge-02/release-01/
```

Each should contain:

```text
release_info.json
public.csv
```

## Step 8: Reset Leaderboards

Replace leaderboards with empty starter files.

## Step 9: Verify Workflow Configuration

Confirm `.github/workflows/score.yml` still uses release-driven scoring.

## Step 10: Commit the Reset

```bash
git add .
git commit -m "Reset repository for new competition"
git push
```

## Step 11: Verify the Reset

Confirm:

- no old predictions remain
- no old release data remain
- no old scores remain
- workflows remain intact
- scripts remain intact

## Step 12: Publish the First Release

Create:

```text
data-release/challenge-01/release-01/
```

Add:

```text
release_info.json
public.csv
```

Commit and push.

## Success Criteria

The repository is ready for a new competition cycle when:

- team submissions have been removed
- release data has been removed
- scoring outputs have been removed
- workflows remain intact
- documentation remains intact
