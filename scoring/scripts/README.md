# Scoring Scripts

This directory contains the two Python scripts used by GitHub Actions.

## Scripts

- `validate_predictions.py` checks each submission CSV for formatting and forecast-window consistency.
- `score_predictions.py` compares the forecasts with `scoring/reference_answers.csv` and writes the leaderboard outputs.

## Local use

```bash
python scoring/scripts/validate_predictions.py --root .
python scoring/scripts/score_predictions.py --root .
```
