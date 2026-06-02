# Modeling the Invisible Workshop

Release-driven forecasting repository for two independent challenges.

## Main ideas

- Two independent challenges represent two independent years.
- Each challenge has multiple rounds.
- Organizers publish a new release to open the next round.
- The next release also closes and scores the previous round.
- Team folders are anonymous and numeric: `Team-01`, `Team-02`, and so on.

## Workflow

1. Organizers publish `data-release/challenge-XX/release-YY/`.
2. Teams update prediction files in `predictions/Team-XX/challenge-YY/`.
3. GitHub Actions validates the release and scores the newly closed round.
4. Leaderboards are regenerated automatically.

See `docs/prediction-format.md`, `docs/scoring-rules.md`, and `docs/workflow.md`.
