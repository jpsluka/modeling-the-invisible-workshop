# Participant Predictions

Participants place forecast files in a folder named for their team.

## File structure

```text
predictions/<team-name>/round-<n>.csv
```

Examples:

```text
predictions/team-alpha/round-1.csv
predictions/iu-epi/round-2.csv
predictions/team-b/round-3.csv
```

Each file must contain exactly four rows and must forecast the four weeks beyond the released data for that round.

Use `predictions/template/forecast_template.csv` as a starting point.
