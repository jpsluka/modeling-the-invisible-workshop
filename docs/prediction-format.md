# Prediction Submission Format

Each team submits one CSV file per challenge and round.

## File location

```text
predictions/Team-XX/challenge-YY/round-ZZ.csv
```

Example:

```text
predictions/Team-01/challenge-01/round-01.csv
```

## Columns

| Column | Type | Description |
|---|---|---|
| week | integer | Week number in the season |
| hospitalizations_per_100k | number | Predicted hospitalization rate |
| r0 | number | Predicted reproduction number |

## Rule

The file must contain the full trajectory from Week 1 through the forecast horizon for that round.
The forecast horizon is read from the matching release folder:

```text
data-release/challenge-YY/release-ZZ/release_info.json
```

## Example

```csv
week,hospitalizations_per_100k,r0
1,0.82,1.32
2,0.95,1.30
3,1.11,1.28
4,1.26,1.25
```
