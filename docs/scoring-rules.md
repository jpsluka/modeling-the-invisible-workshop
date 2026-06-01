# Scoring Rules

This document defines the scoring rules for the workshop forecasting competition.

## Competition structure

- **Challenge 01** and **Challenge 02** are independent years.
- Each challenge has **3 rounds**.
- Rounds within a challenge are scored separately and then averaged into a challenge score.
- Challenge scores are averaged into an overall workshop score.

## Score inputs

Each submission file includes a full weekly trajectory from Week 1 through the forecast horizon specified by the round metadata.

Scoring is applied only to the forecast weeks:

- from `forecast_start_week`
- through `forecast_end_week`

Released weeks are included in the file for context and plotting, but they are not scored.

## Metrics

### 1. Hospitalization trajectory error

The primary metric is normalized root mean squared error (nRMSE) on hospitalization forecasts.

```math
nRMSE = RMSE / mean(observed)
```

where RMSE is computed over the forecast weeks only.

### 2. R0 error

R0 is scored with mean absolute percentage error (MAPE) over the forecast weeks.

```math
MAPE = mean(|predicted - observed| / |observed|)
```

If an observed R0 value is zero, the absolute error is used for that week.

### 3. Round score

The round score is the arithmetic mean of the hospitalization nRMSE and the R0 MAPE.

Lower is better.

### 4. Challenge score

The challenge score is the arithmetic mean of the round scores within that challenge.

### 5. Overall score

The overall workshop score is the arithmetic mean of the two challenge scores.

## Leaderboards

The repository produces:

- `scoring/challenge-01/leaderboard.csv`
- `scoring/challenge-02/leaderboard.csv`
- `scoring/overall-leaderboard.csv`

## Tie handling

If two teams have identical overall scores, the tie is broken by:

1. lower challenge 01 score
2. lower challenge 02 score
3. lower hospitalization nRMSE on the final scored round

## Automation

Validation and scoring are executed by GitHub Actions using the scripts in `scoring/scripts/`.
