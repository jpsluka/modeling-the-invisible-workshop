# Scoring Rules

This document defines the official scoring method for the workshop challenge.

## Overview

Each team submits one forecast file per round. The file contains exactly four weekly forecasts for:

- hospitalizations per 100,000 individuals
- R0

Lower scores are better.

## Truth data

The reference answers are stored in:

```text
scoring/reference_answers.csv
```

The reference answers file contains these columns:

```csv
challenge_round,forecast_week,hospitalizations_per_100k,r0
```

## Round score

For each round, the validation and scoring workflow compares the four predicted weeks with the four truth rows for the same round.

Let:

- `hosp_pred[i]` be the predicted hospitalization rate for week `i`
- `hosp_true[i]` be the truth hospitalization rate for week `i`
- `r0_pred[i]` be the predicted R0 for week `i`
- `r0_true[i]` be the truth R0 for week `i`

For each series, the normalized root mean squared error is:

```math
nRMSE = rac{\sqrt{rac{1}{N}\sum_{i=1}^{N}(\hat{y}_i-y_i)^2}}{ar{y}}
```

where `N = 4` and `ar{y}` is the mean of the truth series.

If the mean of the truth series is zero, the workflow uses the unnormalized RMSE instead.

The round score is the average of the two series scores:

```math
RoundScore = rac{nRMSE_{hosp} + nRMSE_{r0}}{2}
```

## Overall score

The overall leaderboard score is the average of the round scores that a team has submitted:

```math
OverallScore = rac{1}{R}\sum_{r=1}^{R} RoundScore_r
```

where `R` is the number of rounds submitted by that team.

## Outputs

The scoring workflow writes these files:

- `scoring/results/round-1-scores.csv`
- `scoring/results/round-2-scores.csv`
- `scoring/results/round-3-scores.csv`
- `scoring/score_log.csv`
- `scoring/leaderboard.csv`

## Tie handling

If two teams have the same overall score, the workflow orders them alphabetically by team name.
