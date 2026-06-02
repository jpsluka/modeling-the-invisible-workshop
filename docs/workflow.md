# Competition Workflow

This document describes the complete workflow for running the **Modeling the Invisible Workshop Forecasting Competition**.

The competition consists of two independent challenges (years), each containing multiple sequential rounds.

Scoring is **release-driven**: scores are updated only when organizers publish a new data release.

---

# Overview

Each challenge follows the same sequence:

1. Organizers release hospitalization data.
2. Teams submit forecasts.
3. Organizers release additional data.
4. The new release closes the previous round and triggers scoring.
5. Leaderboards are updated automatically.

This process repeats until the challenge is complete.

---

# Competition Structure

The competition contains:

```text
Challenge 1 (Year 1)
  Round 1
  Round 2
  Round 3

Challenge 2 (Year 2)
  Round 1
  Round 2
  Round 3
```

Challenges are conducted sequentially.

Challenge 2 begins only after Challenge 1 is completed.

---

# Repository Structure

## Data Releases

```text
data-release/
├── challenge-01/
│   ├── release-01/
│   ├── release-02/
│   ├── release-03/
│   └── release-04/
└── challenge-02/
    ├── release-01/
    ├── release-02/
    ├── release-03/
    └── release-04/
```

## Team Submissions

```text
predictions/
├── Team-01/
├── Team-02/
├── Team-03/
└── Team-NN/
```

Each team contains challenge-specific prediction files.

Example:

```text
predictions/
└── Team-01/
    ├── challenge-01/
    │   ├── round-01.csv
    │   ├── round-02.csv
    │   └── round-03.csv
    └── challenge-02/
        ├── round-01.csv
        ├── round-02.csv
        └── round-03.csv
```

---

# Release 01

## Organizer Actions

Create:

```text
data-release/challenge-01/release-01/
```

Contents:

```text
release_info.json
public.csv
```

This release:

- opens Round 1
- provides the initial hospitalization trajectory
- does not score any predictions

Commit and push the release.

---

# Round 1 Forecasting

## Team Actions

Each team creates:

```text
predictions/Team-XX/challenge-01/round-01.csv
```

The prediction file contains:

- all weeks from Week 1 through the forecast horizon
- hospitalization forecasts
- R0 forecasts

The forecast horizon is specified in the matching `release_info.json`.

---

# Release 02

## Organizer Actions

Create:

```text
data-release/challenge-01/release-02/
```

Contents:

```text
release_info.json
public.csv
truth_previous_round.csv
```

This release:

- opens Round 2
- closes Round 1
- provides truth data for Round 1

Commit and push the release.

---

# Automatic Scoring

When Release 02 is pushed:

GitHub Actions automatically:

1. validates the release files
2. validates prediction files
3. loads `truth_previous_round.csv`
4. scores all Round 1 forecasts
5. updates challenge leaderboards
6. updates the overall leaderboard
7. commits the updated results

No manual scoring is required.

---

# Round 2 Forecasting

Teams submit:

```text
predictions/Team-XX/challenge-01/round-02.csv
```

using the forecast horizon specified in the release metadata.

---

# Release 03

This release opens Round 3, closes Round 2, and triggers scoring for Round 2.

---

# Release 04

This release closes Round 3, scores Round 3, and finalizes the challenge.

---

# Challenge Completion

Results are stored in:

```text
scoring/challenge-01/
```

After Challenge 1 is complete, repeat the same workflow for Challenge 2.

---

# Leaderboards

Generated outputs include:

```text
scoring/challenge-01/leaderboard.csv
scoring/challenge-02/leaderboard.csv
scoring/overall-leaderboard.csv
```

---

# GitHub Actions

The workflow is defined in:

```text
.github/workflows/score.yml
```

Scoring is triggered when organizers publish a new release.

Participant prediction uploads do not trigger scoring.

---

# Summary

For each challenge:

1. Release 01 opens Round 1.
2. Teams submit Round 1 forecasts.
3. Release 02 scores Round 1 and opens Round 2.
4. Teams submit Round 2 forecasts.
5. Release 03 scores Round 2 and opens Round 3.
6. Teams submit Round 3 forecasts.
7. Release 04 scores Round 3 and closes the challenge.

The same process is then repeated for the next challenge.
