# Scoring Rules

This document defines the official scoring methodology for the workshop forecasting challenge.

## Overview

Scores are computed only on the forecast weeks defined by the current release metadata.

Each round score combines two metrics:

- normalized RMSE for hospitalization forecasts
- RMSE for `r0` forecasts

Lower scores are better.

## Round Score

Let:

- `H` be the predicted hospitalization-per-100k series for the forecast weeks
- `H*` be the corresponding held-out truth series
- `R` be the predicted `r0` series for the forecast weeks
- `R*` be the corresponding held-out truth series

Then:

```math
\mathrm{nRMSE}_H = rac{\sqrt{rac{1}{N}\sum_{i=1}^N (H_i - H_i^*)^2}}{ar{H}^*}
```

and

```math
\mathrm{RMSE}_{R_0} = \sqrt{rac{1}{N}\sum_{i=1}^N (R_i - R_i^*)^2}
```

The round score is the mean of these two values:

```math
\mathrm{RoundScore} = rac{\mathrm{nRMSE}_H + \mathrm{RMSE}_{R_0}}{2}
```

## Overall Score

The overall leaderboard score is the mean of the completed round scores.

```math
\mathrm{OverallScore} = rac{1}{K}\sum_{k=1}^K \mathrm{RoundScore}_k
```

where `K` is the number of scored rounds for the team.

## Tie-Breaking

If two teams have identical overall scores, the leaderboard is ordered by:

1. lower hospitalization nRMSE
2. lower `r0` RMSE
3. team name alphabetically

## Validation Boundary

Only the forecast weeks after `released_through_week` are scored.
The public released weeks are checked only for consistency with the submitted file.
