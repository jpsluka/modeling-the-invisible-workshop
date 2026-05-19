![Uploading Screenshot 2026-05-12 at 13-03-02 ModelingTheInvisibleWorkshop.png…]()

# Modeling the Invisible Workshop Repository

This repository is a GitHub-ready workshop starter for the **Modeling the Invisible** forecasting challenge.

The competition has a single weekly outcome stream and one parameter target:

- hospitalizations per 100,000 individuals
- R0

Forecast time is measured only in weeks. The season is 40 weeks long, week 1 is the first week of the season, and week 1 ends on October 7.

## Repository layout

```text
.
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
├── data-release/
│   ├── challenge-1/
│   ├── challenge-2/
│   └── challenge-3/
├── docs/
│   ├── challenge-timeline.md
│   ├── prediction-format.md
│   └── scoring-rules.md
├── predictions/
│   ├── template/
│   └── <team-name>/
├── scoring/
│   ├── reference_answers.csv
│   ├── leaderboard.csv
│   ├── score_log.csv
│   ├── results/
│   └── scripts/
└── README.md
```

## How the workshop works

1. Organizers release weekly data in `data-release/`.
2. Teams submit one CSV per round in `predictions/<team-name>/`.
3. Each submission forecasts exactly four weeks into the future.
4. GitHub Actions validates submissions, scores them against the reference answers, and regenerates the leaderboard automatically.

## Competition rules

Review these files before submitting:

- [Prediction format](docs/prediction-format.md)
- [Scoring rules](docs/scoring-rules.md)
- [Challenge timeline](docs/challenge-timeline.md)

## Submission files

Each team submits one file per round:

```text
predictions/<team-name>/round-<n>.csv
```

Where `n` is 1, 2, or 3.

Each file must contain exactly four rows, covering the four weeks beyond the released data for that round.

## Scoring outputs

Automated scoring writes these files:

- `scoring/leaderboard.csv`
- `scoring/score_log.csv`
- `scoring/results/round-1-scores.csv`
- `scoring/results/round-2-scores.csv`
- `scoring/results/round-3-scores.csv`

## GitHub automation

The repository includes a GitHub Actions workflow that:

- validates prediction CSV files
- scores each team against the reference answers
- uploads scoring artifacts
- commits refreshed leaderboard files on `main`

## Notes for organizers

- Keep `scoring/reference_answers.csv` in sync with the challenge releases.
- Update the challenge files in `data-release/` when a round is published.
- Keep the scoring scripts and the prediction format in step with each other.
