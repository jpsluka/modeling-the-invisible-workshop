# Scoring Scripts

- `validate_predictions.py` checks submission structure, filenames, week coverage, and numeric fields.
- `score_predictions.py` compares each team's forecast weeks against the hidden reference answers and writes leaderboards.

Run locally:

```bash
python scoring/scripts/validate_predictions.py --root .
python scoring/scripts/score_predictions.py --root .
```
