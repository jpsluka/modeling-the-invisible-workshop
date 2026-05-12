# Prediction CSV Specification

This document defines the required submission format for all workshop prediction files.

---

# Overview

Each participating team submits one CSV file per challenge round.

Submission files should be placed in:

```text
predictions/<team-name>/round-<n>.csv
```

Examples:

```text
predictions/team-alpha/round-1.csv
predictions/iu-modelers/round-2.csv
predictions/epi-forecast-group/round-3.csv
```

---

# Required File Format

Each CSV must:

- Use UTF-8 encoding
- Include a single header row
- Use commas as separators
- Contain no blank rows
- Use ISO dates (`YYYY-MM-DD`)
- Contain exactly one prediction per target week

---

# Required Columns

| Column | Type | Description |
|---|---|---|
| team_name | string | Official team name |
| challenge_round | integer | Challenge number (1, 2, or 3) |
| prediction_date | date | Date predictions were generated |
| target_week | date | Forecast target week ending date |
| forecast_target | string | Forecast target identifier (use `overall`) |
| predicted_cases | float | Predicted influenza case count |
| lower_95_ci | float | Lower 95% confidence interval |
| upper_95_ci | float | Upper 95% confidence interval |
| estimated_peak_week | date | Predicted epidemic peak week |
| estimated_total_cases | float | Predicted season total |
| model_name | string | Forecasting model name |
| model_parameters | stringified JSON | Key model parameters |

---

# Forecast Targets

All forecasts are made at the overall population level for the released dataset.

Each row in a submission represents one prediction for one target week.

---

# Example Submission

```csv
team_name,challenge_round,prediction_date,target_week,forecast_target,predicted_cases,lower_95_ci,upper_95_ci,estimated_peak_week,estimated_total_cases,model_name,model_parameters
team-alpha,1,2026-02-10,2026-02-14,overall,1042,980,1110,2026-03-07,18200,SEIR-v2,"{""beta"":0.34,""gamma"":0.11}"
team-alpha,1,2026-02-10,2026-02-21,overall,1180,1090,1260,2026-03-07,18200,SEIR-v2,"{""beta"":0.34,""gamma"":0.11}"
```

---

# Validation Rules

Submissions will automatically fail validation if:

- Required columns are missing
- Dates are malformed
- Numeric fields contain non-numeric values
- Confidence intervals are invalid:
  - `lower_95_ci > predicted_cases`
  - `upper_95_ci < predicted_cases`
- Duplicate `target_week` rows exist
- File names do not match required conventions

---

# Scoring Inputs

The scoring workflow uses:

| Metric | Source Column |
|---|---|
| RMSE | predicted_cases |
| Peak timing accuracy | estimated_peak_week |
| Final epidemic size accuracy | estimated_total_cases |
| Parameter estimation quality | model_parameters |

---

# Submission Workflow

1. Fork the repository
2. Add or update your CSV submission file
3. Open a Pull Request
4. GitHub Actions validates the submission
5. Organizers review and merge accepted predictions

---

# Organizer Notes

Recommended release schedule:

```text
Round 1 → Initial outbreak data
Round 2 → Mid-season update
Round 3 → Late-season update
```

Recommended freeze policy:

- Predictions become immutable after submission deadline
- Only organizers may modify merged prediction files

---

# Future Extensions

Possible future additions:

- Probabilistic forecasts
- Ensemble forecasts
- Hospitalization forecasts
- State-level forecasts
- Forecast metadata schema
- Automatic leaderboard generation

