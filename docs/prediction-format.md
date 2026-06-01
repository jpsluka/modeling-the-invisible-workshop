# Prediction Submission Format

This document defines the official submission format for the **Modeling the Invisible Workshop Forecasting Competition**.

## Overview

Each team submits one prediction file for each competition round.

Prediction files contain the team's estimate of the hospitalization trajectory from Week 1 through the end of the forecast horizon for the current round, together with an estimate of `r0` for each week.

The forecast horizon is specified by the current data release and may vary between rounds.

Typical forecast horizons range from 3 to 6 weeks beyond the released data.

## Competition Time Scale

The competition uses a normalized influenza season consisting of 40 weeks.

- Week numbers are integers.
- Week 1 represents the start of the season.
- No calendar dates are used.
- All submissions use week numbers.

## Data Release Information

Each competition round includes a release metadata file:

```text
data-release/round-N/release_info.json
```

Example:

```json
{
  "round": 2,
  "released_through_week": 18,
  "forecast_start_week": 19,
  "forecast_end_week": 24
}
```

This file defines the required forecast horizon.

Teams must submit predictions through `forecast_end_week`.

## Submission Location

Prediction files must be submitted to:

```text
predictions/<team-name>/round-N.csv
```

Examples:

```text
predictions/team-alpha/round-1.csv
predictions/team-alpha/round-2.csv
predictions/team-alpha/round-3.csv
```

## Required Columns

The prediction file must contain the following columns.

| Column | Type | Description |
|----------|----------|----------|
| week | integer | Week number |
| hospitalizations_per_100k | float | Predicted hospitalization rate per 100,000 population |
| r0 | float | Predicted effective reproduction number |

## Submission Requirements

The submission must:

1. Begin with Week 1.
2. Include all weeks through the forecast horizon specified in the release.
3. Contain exactly one row per week.
4. Use ascending week order.
5. Contain no missing week numbers.

For example, if:

```json
{
  "released_through_week": 12,
  "forecast_end_week": 16
}
```

then the prediction file must contain weeks 1–16.

## Example Submission

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

## Validation Rules

Submissions automatically fail validation if:

- required columns are missing
- week values are not integers
- week numbers are not strictly increasing
- required forecast weeks are missing
- duplicate weeks exist
- non-numeric values appear in numeric fields

## Forecast Horizon

The forecast horizon is determined solely by the current release metadata.

Teams should not assume a fixed forecast length.

Examples:

| Released Through | Forecast Horizon |
|------------------|-------------------|
| Week 12 | Weeks 13–16 |
| Week 18 | Weeks 19–24 |
| Week 28 | Weeks 29–31 |

The required horizon may vary from round to round.

## Ground Truth Data

Released data are provided in:

```text
data-release/round-N/release.csv
```

with format:

```csv
week,hospitalizations_per_100k
1,0.82
2,0.95
3,1.11
```

## Reproducibility

Teams are encouraged to:

- document assumptions
- preserve code used to generate forecasts
- maintain version control
- describe uncertainty sources

The repository serves as the official archive of all submissions.
