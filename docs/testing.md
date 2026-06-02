# Testing the Repository

This document describes how to test the repository, validation scripts, scoring workflow, and release-driven competition process.

## Prerequisites

Before testing, ensure that:

- Python 3.11 or newer is installed
- Git is installed
- The repository has been cloned locally
- Required Python packages have been installed

## Clone the Repository

```bash
git clone https://github.com/<your-org>/<your-repo>.git
cd <your-repo>
```

## Create a Python Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Verify Repository Structure

Confirm the following folders exist:

```text
data-release/
predictions/
scoring/
scoring/scripts/
docs/
.github/workflows/
```

Important files:

```text
docs/prediction-format.md
docs/scoring-rules.md
docs/workflow.md
.github/workflows/score.yml
```

## Test Release Validation

```bash
python scoring/scripts/validate_release.py --root .
```

Expected:

```text
Release validation passed.
```

## Test Prediction Validation

```bash
python scoring/scripts/validate_predictions.py --root .
```

Expected:

```text
Prediction validation passed.
```

## Test Scoring

```bash
python scoring/scripts/score_predictions.py --root .
```

Expected:

```text
Scoring complete.
```

Verify:

```text
scoring/challenge-01/leaderboard.csv
scoring/challenge-02/leaderboard.csv
scoring/overall-leaderboard.csv
```

## Test the Plotting Notebook

Run the plotting notebook/script and verify that plots are generated in:

```text
workshop_data/plots/
```

## Test the Release-Driven Workflow

### Step 1: Release 01

Verify:

```text
data-release/challenge-01/release-01/
```

contains:

```text
release_info.json
public.csv
```

No scoring should occur.

### Step 2: Create Round 1 Predictions

Verify files exist:

```text
predictions/Team-01/challenge-01/round-01.csv
predictions/Team-02/challenge-01/round-01.csv
```

Prediction uploads alone should not update leaderboards.

### Step 3: Publish Release 02

Create:

```text
data-release/challenge-01/release-02/
```

containing:

```text
release_info.json
public.csv
truth_previous_round.csv
```

Commit and push the release.

### Step 4: Verify Automatic Scoring

Open GitHub → Actions and verify:

- workflow starts automatically
- releases validate
- predictions validate
- Round 1 is scored
- leaderboards update

### Step 5: Verify Automatic Commit

Verify a commit appears:

```text
Update automated leaderboard
```

### Step 6: Test Releases 03 and 04

Release 03 scores Round 2.

Release 04 scores Round 3 and finalizes the challenge.

Repeat for Challenge 2.

## Success Criteria

The repository is functioning correctly if:

- release validation passes
- prediction validation passes
- scoring runs successfully
- leaderboards are generated
- GitHub Actions completes successfully
- scoring updates only when a new release is published
- challenge and overall leaderboards update correctly
