<img src="media/Banner_ModelingTheInvisibleWorkshop.png" alt="Workshop Banner" width="800">

# Modeling the Invisible Workshop Repository

This repository is a GitHub-ready starter kit for the **Modeling the Invisible** workshop competition. It is organized around the workshop workflow: organizers release data in stages, participants post forecasts, and the organizing team summarizes and scores submissions.

## Competition structure

The workshop uses three influenza challenge rounds and expects small teams to model from limited, sequentially released data. Participants may use any modeling approach, and judging focuses on season totals, RMSE, early prediction of the final state, and parameter estimation.

## Workshop Workflow 

1. Organizers release data in `data-release/`
2. Teams submit predictions in `predictions/`
3. GitHub Actions automatically validates and scores submissions
4. Leaderboards are updated in `scoring/`

## Typical workflow

### 1) Organizers release data
Place each release file under the matching challenge folder in `data-release/`.

Example:

```text
data-release/challenge-1/release_001.csv
data-release/challenge-2/release_001.csv
data-release/challenge-3/release_001.csv
```

### 2) Participants submit predictions
Participants should copy the template from `predictions/templates/forecast_template.csv` and save their forecast files under `predictions/submissions/`.

Recommended naming convention:

```text
predictions/submissions/<team_name>/<challenge_id>/<release_id>.csv
```

### 3) Organizers score and summarize results
Use the scoring workflow and scripts in `scripts/` to validate submissions and generate the leaderboard files in `scoring/`.

## Submission format

The submission template includes these columns:

- `team_name`
- `challenge_id`
- `release_id`
- `target_date`
- `predicted_severe_cases`
- `predicted_total_cases`
- `r0`
- `vaccination_effectiveness`
- `cross_protection_days`
- `notes`

## Scoring model

The included scoring script is intentionally simple and transparent. It calculates:

- **Season total error** from cumulative severe-case forecasts
- **RMSE** against the reference severe-case series
- **Early final-state score** based on the first forecast row versus the final severe-case total
- **Parameter estimation score** from the model parameters included in the submission

A combined score is then written to `scoring/leaderboard.csv`.

## Competition Rules

All participants should review the official workshop documentation before submitting forecasts.

### Documentation

- [Prediction Submission Format](docs/prediction-format.md)
- [Scoring Rules](docs/scoring-rules.md)

### Repository Workflow

1. Organizers release outbreak data in `data-release/`
2. Teams submit forecasts in `predictions/`
3. GitHub Actions automatically validates submissions
4. Scores and leaderboards are automatically regenerated in `scoring/`

### Submission Format

Prediction files must be submitted as:

```text
predictions/<team-name>/round-<n>.csv
```

Example:

```text
predictions/team-alpha/round-1.csv
```

### Automated Scoring

All validation and scoring are fully automated through GitHub Actions.

Updated leaderboards are written to:

```text
scoring/leaderboard.csv
```

Detailed round-level scoring summaries are written to:

```text
scoring/results/
```

## GitHub Actions

The repository includes a workflow that:

1. validates forecast CSV files,
2. optionally scores them against a reference answer key,
3. writes leaderboard and log files as build artifacts.

Use the manual workflow dispatch when you want to score a batch after releasing the official answer key.

## Issue templates

The `.github/ISSUE_TEMPLATE/` folder includes templates for:

- submission or validation problems
- scoring or leaderboard questions

## Notes for organizers

- Keep official release data separate from participant submissions.
- Avoid committing hidden answer keys to the public branch.
- When the competition ends, you can add a final reference file to `scoring/` and rerun the workflow to generate the official leaderboard.
