# Prediction Format

This document defines the exact CSV format for team submissions.

## Forecast setup

- The season is 40 weeks long.
- Week numbers are integers from 0 to 39.
- Week 0 is the first week of the season.
- Week 0 ends on October 7.
- All dates in the repository are represented as week integers, not calendar dates.
- Each submission forecasts exactly the specified number of weeks beyond the data released for that round.

If a round releases data through week `W`, then the submission must include forecasts for:

- `W + 1`
- ...
- `W + n`

## File location

Each team submits one file per round:

```text
predictions/<team-name>/round-<n>.csv
```

Examples:

```text
predictions/team-alpha/round-1.csv
predictions/iu-epi/round-2.csv
predictions/team-b/round-3.csv
```

## Required columns

The CSV header must be exactly:

```csv
team_name,challenge_round,release_week,forecast_week,hospitalizations_per_100k_pred,r0_pred,model_name,model_parameters
```

## Column definitions

| Column | Type | Description |
|---|---|---|
| team_name | string | Team name; must match the folder name |
| challenge_round | integer | Challenge round number, must be 1, 2, or 3 |
| release_week | integer | Last week included in the released data for that round |
| forecast_week | integer | Future week being predicted |
| hospitalizations_per_100k_pred | float | Predicted hospitalization rate per 100,000 individuals |
| r0_pred | float | Predicted R0 value for that forecast week |
| model_name | string | Short name of the model used |
| model_parameters | JSON object | JSON-encoded model parameters, written as a single CSV cell |

## Required row structure

Each submission must:

- contain exactly four data rows
- use the same `team_name` in every row
- use the same `challenge_round` in every row
- use the same `release_week` in every row
- use the same `model_name` in every row
- use the same `model_parameters` in every row
- include one row for each of the four forecast weeks beyond the release week

For a release week of 8, the required forecast weeks are 9, 10, 11, and 12.

## Example submission

```csv
team_name,challenge_round,release_week,forecast_week,hospitalizations_per_100k_pred,r0_pred,model_name,model_parameters
team-alpha,1,8,9,15.2,1.31,SEIR-v2,"{""beta"":0.34,""gamma"":0.11}"
team-alpha,1,8,10,15.8,1.33,SEIR-v2,"{""beta"":0.34,""gamma"":0.11}"
team-alpha,1,8,11,16.6,1.35,SEIR-v2,"{""beta"":0.34,""gamma"":0.11}"
team-alpha,1,8,12,17.1,1.36,SEIR-v2,"{""beta"":0.34,""gamma"":0.11}"
```

## Validation rules

Submissions fail validation if any of the following are true:

- required columns are missing
- the header does not match exactly
- `challenge_round` is not 1, 2, or 3
- `release_week` is not an integer between 1 and 36
- `forecast_week` is not one of the four expected future weeks
- any required field is blank
- numeric fields cannot be parsed as numbers
- `model_parameters` is not valid JSON
- `model_parameters` is not a JSON object
- the file contains more or fewer than four data rows

## Organizers

The scoring workflow expects the file structure and column names above to remain stable.
