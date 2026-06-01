# Modeling the Invisible Workshop

This repository supports the workshop competition **Modeling the Invisible: Competition on Forecasting Viral Spread with Limited Data**.

It includes:

- the public release data for each round
- the prediction submission format
- scoring rules
- validation and scoring scripts
- a plotting notebook-style script
- example submissions and synthetic truth data for testing

## Repository Structure

```text
README.md
CONTRIBUTING.md

data-release/
  round-1/
  round-2/
  round-3/

docs/
  competition-rules.md
  competition-rules.html
  prediction-format.md
  scoring-rules.md

notebooks/
  plot_team_forecasts.py

predictions/
  template/
  team-alpha/
  team-beta/

scoring/
  leaderboard.csv
  reference_answers.csv
  results/
  scripts/

.github/
  ISSUE_TEMPLATE/
  workflows/
```

## Competition Summary

Teams forecast weekly influenza-associated hospitalizations per 100,000 population and `r0`.
Forecast horizons vary by round and are defined in `data-release/round-N/release_info.json`.
Each submission contains the full trajectory from Week 1 through the release horizon.

## Data Files

For each round:

- `data-release/round-N/release_info.json` defines the released week and forecast horizon
- `data-release/round-N/release.csv` contains the public hospitalization series through the released week

## Submission Files

Teams submit predictions to:

```text
predictions/<team-name>/round-N.csv
```

Each file must contain:

- `week`
- `hospitalizations_per_100k`
- `r0`

## Scoring

Scores are computed only on the forecast weeks after the released data.
The round score is the average of:

- normalized RMSE for hospitalizations
- RMSE for `r0`

See `docs/scoring-rules.md` for the full definition.

## Local Validation and Scoring

```bash
python scoring/scripts/validate_predictions.py --root .
python scoring/scripts/score_predictions.py --root .
```

## Notebook Plotting

Run `notebooks/plot_team_forecasts.py` from the repository root to generate team plots and an aggregate plot for the latest round.

## Notes

The files in `predictions/team-alpha/`, `predictions/team-beta/`, and `scoring/reference_answers.csv` are synthetic examples included so the repository runs end-to-end out of the box.
Organizers should replace them with their own release data and truth files when launching a real workshop instance.
