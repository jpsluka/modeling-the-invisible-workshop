# Prediction Submission Format

This document defines the official submission format for the **Modeling the Invisible Workshop Forecasting Competition**.

## Overview

Each team submits one CSV file per challenge round.

Prediction files contain the team's full weekly forecast trajectory from Week 1 through the end of the forecast horizon defined by the current release metadata.

The forecast horizon may vary by round. Typical horizons range from 3 to 6 weeks beyond the released data.

## Competition time scale

- The competition uses a normalized 40-week influenza season.
- Week numbers are integers.
- Week 1 represents the start of the season.
- No calendar dates are used in submission files.

## Data release information

Each round includes a release metadata file:

```text
data-release/challenge-XX/round-YY/release_info.json
```

Example:

```json
{
  "challenge_id": 1,
  "round_id": 2,
  "released_through_week": 18,
  "forecast_start_week": 19,
  "forecast_end_week": 24
}
```

Teams must submit predictions through `forecast_end_week`.

## Submission location

Prediction files must be submitted to:

```text
predictions/Team-XX/challenge-YY/round-ZZ.csv
```

Examples:

```text
predictions/Team-01/challenge-01/round-01.csv
predictions/Team-01/challenge-01/round-02.csv
predictions/Team-01/challenge-02/round-01.csv
```

## Required columns

The prediction file must contain the following columns.

| Column | Type | Description |
|---|---:|---|
| week | integer | Week number |
| hospitalizations_per_100k | float | Predicted hospitalization rate per 100,000 population |
| r0 | float | Predicted effective reproduction number |

## Submission requirements

The submission must:

1. Begin with Week 1.
2. Include all weeks through the forecast horizon specified in the release metadata.
3. Contain exactly one row per week.
4. Use ascending week order.
5. Contain no missing week numbers.
6. Include numeric values for both `hospitalizations_per_100k` and `r0`.

For example, if the matching release metadata says:

```json
{
  "released_through_week": 12,
  "forecast_end_week": 16
}
```

then the prediction file must contain:

```text
weeks 1–16
```

## Example submission

```csv
week,hospitalizations_per_100k,r0
1,0.82,1.32
2,0.95,1.30
3,1.11,1.28
4,1.26,1.25
5,1.40,1.23
6,1.55,1.21
7,1.82,1.18
8,2.05,1.16
9,2.31,1.14
10,2.62,1.12
11,2.95,1.10
12,3.30,1.08
13,3.75,1.05
14,4.10,1.02
15,4.35,0.99
16,4.45,0.96
```

## Validation rules

Submissions automatically fail validation if:

- required columns are missing
- week values are not integers
- week numbers are not strictly increasing
- required forecast weeks are missing
- duplicate weeks exist
- non-numeric values appear in numeric fields
- the file does not begin at Week 1
- the file does not extend through the required forecast end week

## Forecast horizon

The forecast horizon is determined solely by the current release metadata.

Teams should not assume a fixed forecast length.

Examples:

| Released through | Forecast horizon |
|---|---|
| Week 12 | Weeks 13–16 |
| Week 18 | Weeks 19–24 |
| Week 24 | Weeks 25–30 |

The required horizon may vary from round to round.
