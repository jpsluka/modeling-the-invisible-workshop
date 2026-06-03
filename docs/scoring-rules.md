# Scoring Rules

Scores are updated only when organizers publish a new release.

## Release-driven scoring

- Release 01 opens Round 01 and does not score anything.
- Release 02 scores Round 01.
- Release 03 scores Round 02.
- Release 04 scores Round 03 and closes the challenge.

## What is scored

For each newly closed round, only the forecast weeks are scored.
Historical released weeks are not counted.

## Round score

Scores are calculated using weighting to combine the hospitalization_nRMS and the R0_RMSE. The two are combined with;

`round_score = 0.8 × hospitalization_nRMSE + 0.2 × R0_RMSE`

## Challenge score

The challenge score is the mean of the round scores in that challenge.

## Overall score

The overall score is the mean of the two challenge scores.

Lower is better.
