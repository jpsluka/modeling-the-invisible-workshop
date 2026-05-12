# Scoring Scripts

This directory contains the automated validation and scoring scripts used for the **Modeling the Invisible Workshop** forecasting challenge.

These scripts are executed automatically through GitHub Actions whenever prediction submissions are added or updated.

---

# Directory Structure

```text
scoring/scripts/
├── README.md
├── validate_predictions.py
└── score_predictions.py
```

---

# Overview

The scoring workflow consists of two stages:

| Script | Purpose |
|---|---|
| `validate_predictions.py` | Validates submission formatting and schema compliance |
| `score_predictions.py` | Computes scores and generates leaderboard outputs |

Both scripts are designed to run without manual intervention.

---

# Validation Workflow

The validation script checks all prediction submissions for:

- Correct file naming conventions
- Required CSV columns
- ISO-formatted dates
- Valid numeric values
- Proper confidence interval ordering
- Duplicate target weeks
- Valid JSON in `model_parameters`
- Internal consistency within files

Invalid submissions fail GitHub Actions validation and are not scored.

---

# Scoring Workflow

The scoring script:

1. Loads all prediction submissions
2. Loads released ground-truth data
3. Computes evaluation metrics
4. Generates round summaries
5. Regenerates the overall leaderboard
6. Writes outputs to the `scoring/` directory

All scoring is deterministic and reproducible.

---

# Input Data

## Prediction Files

Prediction submissions are expected at:

```text
predictions/<team-name>/round-<n>.csv
```

Example:

```text
predictions/team-alpha/round-1.csv
```

---

## Truth Files

Ground-truth observations are expected at:

```text
data-release/round-<n>/truth.csv
```

Example:

```text
data-release/round-1/truth.csv
```

Expected truth file format:

```csv
target_week,observed_cases
2026-02-14,1045
2026-02-21,1178
2026-02-28,1321
```

---

# Generated Outputs

The scoring workflow produces:

| File | Description |
|---|---|
| `scoring/leaderboard.csv` | Overall rankings |
| `scoring/results/round-1-scores.csv` | Detailed Round 1 scores |
| `scoring/results/round-2-scores.csv` | Detailed Round 2 scores |
| `scoring/results/round-3-scores.csv` | Detailed Round 3 scores |

These files are automatically updated after successful workflow execution.

---

# Evaluation Metrics

The scoring workflow computes:

- Normalized RMSE (nRMSE)
- Peak timing error
- Total epidemic size error
- Optional parameter estimation error

Lower scores are better.

See:

```text
docs/scoring-rules.md
```

for the complete scoring specification.

---

# Running Scripts Locally

Both scripts can be executed locally for testing purposes.

## Validate prediction files

```bash
python scoring/scripts/validate_predictions.py --root .
```

---

## Generate scores and leaderboard

```bash
python scoring/scripts/score_predictions.py --root .
```

---

# GitHub Actions Integration

These scripts are automatically executed through:

```text
.github/workflows/score.yml
```

The workflow triggers when:

- Prediction files change
- Truth data changes
- Scoring scripts change
- Workflow files change

---

# Error Handling

Validation errors cause the GitHub Actions workflow to fail.

Common validation failures include:

- Missing columns
- Incorrect file names
- Invalid dates
- Duplicate forecast weeks
- Malformed JSON
- Invalid numeric values

Errors are displayed directly in the GitHub Actions logs.

---

# Reproducibility

The scoring system is fully reproducible because:

- All submissions are version controlled
- All scoring scripts are version controlled
- All workflow executions are logged by GitHub Actions
- Generated leaderboards are committed back to the repository

This ensures transparency and auditability throughout the workshop.

---

# Extending the Workflow

Possible future extensions include:

- Probabilistic forecasts
- Ensemble forecast scoring
- Visualization dashboards
- Forecast calibration metrics
- Automatic report generation
- GitHub Pages leaderboard dashboards

---

# Maintainers

Workshop organizers are responsible for:

- Releasing truth data
- Maintaining scoring scripts
- Reviewing pull requests
- Managing repository workflows

Participants should not modify scoring scripts directly.