# Modeling the Invisible Workshop

This repository supports the workshop **Modeling the Invisible: Competition on Forecasting Viral Spread with Limited Data**.

The competition is organized as:

- **2 independent challenges** (two different years)
- **3 rounds per challenge**
- **sequential data releases within each challenge**
- **team submissions using numeric team IDs** (`Team-01`, `Team-02`, ...)

Each round releases updated hospitalization data for that challenge-year, and each team submits a full weekly forecast trajectory through the round-specific horizon.

## Repository layout

- `data-release/` — release metadata and released data for each challenge and round
- `predictions/` — team submissions, grouped by team and challenge
- `scoring/` — hidden reference answers, leaderboard outputs, and scoring scripts
- `docs/` — rules and file-format documentation
- `.github/workflows/` — GitHub Actions workflow for validation and scoring
- `notebooks/` — local plotting helpers for exploring team forecasts

## Workflow

1. Organizers release a new round under `data-release/challenge-XX/round-YY/`.
2. Teams update `predictions/Team-XX/challenge-XX/round-YY.csv`.
3. GitHub Actions validates prediction files.
4. GitHub Actions scores submissions against the hidden reference answers.
5. Updated leaderboards are written to `scoring/`.

## Competition rules and formats

- [Competition Rules](docs/competition-rules.md)
- [Prediction Format](docs/prediction-format.md)
- [Scoring Rules](docs/scoring-rules.md)

## Local plotting

The notebook-friendly plotting helper is in:

- `notebooks/plot_team_forecasts.py`

It creates per-team visual summaries and aggregate plots from the repository data.

## Quick start

```bash
python scoring/scripts/validate_predictions.py --root .
python scoring/scripts/score_predictions.py --root .
```

