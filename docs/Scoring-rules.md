# Scoring Rules

This document defines the official scoring methodology for the *Modeling the Invisible* workshop forecasting challenge.

---

# Overview

Participants submit influenza forecasts during three sequential challenge rounds.

Each submission is automatically evaluated against the released ground-truth data after the corresponding challenge period ends.

The scoring workflow is fully automated using GitHub Actions.

Lower scores are better.

---

# Competition Structure

The workshop consists of:

| Round | Description |
|---|---|
| Round 1 | Early outbreak forecasting |
| Round 2 | Mid-season forecasting |
| Round 3 | Late-season forecasting |

Teams submit one prediction file per round.

---

# Forecast Targets

Each submission predicts:

- weekly influenza case counts
- epidemic peak timing
- total epidemic size
- optional model parameters

Forecasts are made at the overall population level.

---

# Evaluation Metrics

Each round score combines four metrics.

## 1. Forecast Accuracy (nRMSE)

The primary metric is normalized root mean squared error (nRMSE) between predicted and observed weekly case counts.

```math
\mathrm{nRMSE}=
\frac{
\sqrt{
\frac{1}{N}
\sum_{i=1}^{N}(\hat{y}_i-y_i)^2
}
}{
\bar{y}
}
````

Where:

* ( \hat{y}_i ) = predicted weekly cases
* ( y_i ) = observed weekly cases
* ( \bar{y} ) = mean observed weekly cases
* ( N ) = number of forecasted weeks

Lower values indicate better forecast accuracy.

---

## 2. Peak Timing Error

Teams predict the epidemic peak week.

Peak timing error is measured as the absolute difference (in weeks) between predicted and observed peak timing.

```math
\mathrm{PeakError}=
\left|
\mathrm{PredictedPeakWeek}
-
\mathrm{ObservedPeakWeek}
\right|
```

Lower values indicate better peak timing forecasts.

---

## 3. Total Epidemic Size Error

Teams estimate the total number of influenza cases across the season.

The score uses relative error:

```math
\mathrm{TotalError}=
\frac{
|\hat{T}-T|
}{
T
}
```

Where:

* ( \hat{T} ) = predicted total cases
* ( T ) = observed total cases

Lower values indicate more accurate estimates.

---

## 4. Parameter Estimation Error (Optional)

If organizers release true simulation parameters after a round, submissions may also be evaluated on parameter estimation quality.

Relative parameter error is computed for shared parameters:

```math
\mathrm{ParameterError}=
\frac{
|\hat{\theta}-\theta|
}{
|\theta|
}
```

Where:

* ( \hat{\theta} ) = predicted parameter
* ( \theta ) = true parameter

Only parameters present in both the submission and truth file are scored.

---

# Round Score

The round score is the arithmetic mean of all available metric scores.

```math
\mathrm{RoundScore}=
\frac{1}{K}
\sum_{k=1}^{K}m_k
```

Where:

* ( m_k ) = metric values
* ( K ) = number of available metrics

Lower scores are better.

---

# Overall Competition Score

The final leaderboard score is the mean of all completed round scores.

```math
\mathrm{OverallScore}=
\frac{1}{R}
\sum_{r=1}^{R}\mathrm{RoundScore}_r
```

Where:

* ( R ) = number of completed rounds

Teams are ranked from lowest overall score to highest.

---

# Validation Rules

Submissions automatically fail validation if:

* required columns are missing
* dates are malformed
* numeric fields contain invalid values
* confidence intervals are inconsistent
* duplicate target weeks exist
* filenames do not follow required conventions

Invalid submissions are not scored.

---

# Ties

If two teams have identical overall scores:

1. lower nRMSE wins
2. lower peak timing error wins
3. earliest valid submission timestamp wins

---

# Automation Workflow

All scoring is automated through GitHub Actions.

When a submission is merged:

1. validation scripts run automatically
2. scores are recomputed
3. leaderboard files are regenerated
4. updated results are committed back to the repository

No manual score calculation is required.

---

# Leaderboard Files

Generated outputs include:

| File                                 | Description              |
| ------------------------------------ | ------------------------ |
| `scoring/leaderboard.csv`            | Overall rankings         |
| `scoring/results/round-1-scores.csv` | Detailed Round 1 metrics |
| `scoring/results/round-2-scores.csv` | Detailed Round 2 metrics |
| `scoring/results/round-3-scores.csv` | Detailed Round 3 metrics |

---

# Reproducibility

All scoring scripts are version-controlled in the repository.

All submitted forecasts remain permanently archived for reproducibility and auditing.

---

# Organizer Notes

Organizers may:

* update released truth data
* add additional forecast targets
* release supplemental metadata
* publish final reports and visualizations

Any scoring-rule changes after the competition begins should be documented publicly in the repository history.

```
```
