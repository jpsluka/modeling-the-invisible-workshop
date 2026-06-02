# Testing the Repository Directly on GitHub

This guide explains how to test the workshop repository **directly on GitHub**, without using a local clone.

---

## 1. Open the repository on GitHub

Go to the repository home page and confirm that the current branch is the branch used for the competition, usually `main`.

---

## 2. Confirm that the expected files are present

Check that the repository contains the core folders and files:

```text
data-release/
predictions/
scoring/
scoring/scripts/
docs/
.github/workflows/score.yml
```

Also confirm that the documentation files are present:

```text
docs/prediction-format.md
docs/scoring-rules.md
docs/workflow.md
docs/testing.md
```

---

## 3. Check the release folders

Open the release folders under `data-release/` and confirm that they follow the expected structure:

```text
data-release/challenge-01/release-01/
data-release/challenge-01/release-02/
data-release/challenge-01/release-03/
data-release/challenge-01/release-04/

data-release/challenge-02/release-01/
data-release/challenge-02/release-02/
data-release/challenge-02/release-03/
data-release/challenge-02/release-04/
```

For each release folder, verify that `release_info.json` and `public.csv` are present.

For releases after the first, verify that `truth_previous_round.csv` is also present.

---

## 4. Check the team prediction folders

Open the `predictions/` folder and confirm that team names use the numeric format:

```text
Team-01
Team-02
Team-03
```

Inside each team folder, verify that challenge folders exist:

```text
predictions/Team-01/challenge-01/
predictions/Team-01/challenge-02/
```

Inside each challenge folder, verify that round files exist:

```text
round-01.csv
round-02.csv
round-03.csv
```

---

## 5. Inspect one prediction file

Open one prediction file, such as:

```text
predictions/Team-01/challenge-01/round-01.csv
```

Confirm that it uses the correct GitHub Markdown-documented schema:

```csv
week,hospitalizations_per_100k,r0
```

Also confirm that:

- the week values begin at 1
- the rows are in increasing week order
- the file includes the full forecast horizon for that release
- `r0` is present and numeric

---

## 6. Inspect the release metadata

Open a file such as:

```text
data-release/challenge-01/release-02/release_info.json
```

Confirm that it includes the expected fields, such as:

- `challenge_id`
- `release_id`
- `released_through_week`
- `forecast_start_week`
- `forecast_end_week`

Also confirm that the forecast horizon matches the release-driven scoring design.

---

## 7. Check the workflow file

Open:

```text
.github/workflows/score.yml
```

Confirm that it:

- runs on pushes to `main`
- runs when `data-release/**` changes
- installs dependencies
- runs `validate_release.py`
- runs `validate_predictions.py`
- runs `score_predictions.py`
- uploads scoring artifacts
- commits updated scoring outputs back to the repository

A valid workflow should stage the entire `scoring/` tree, not only a narrow subset of CSV files.

---

## 8. Test the release-driven workflow on GitHub

To test the repository directly on GitHub, publish a new release folder under `data-release/`.

### Example test sequence

1. Add or update:
   ```text
   data-release/challenge-01/release-02/
   ```

2. Make sure that folder contains:
   - `release_info.json`
   - `public.csv`
   - `truth_previous_round.csv`

3. Commit the change directly on GitHub.

4. Open the **Actions** tab.

5. Confirm that the workflow starts automatically.

6. Confirm that the workflow:
   - validates the release files
   - validates team predictions
   - scores the newly closed round
   - updates leaderboard files
   - commits the new scoring results

---

## 9. Verify that prediction uploads do not score by themselves

Confirm that editing a file such as:

```text
predictions/Team-01/challenge-01/round-02.csv
```

does **not** trigger scoring by itself.

The repository is designed so that scoring occurs only when organizers publish the **next release**.

---

## 10. Check the generated scoring outputs

After a release triggers scoring, inspect the generated files in `scoring/`.

Expected outputs include:

```text
scoring/challenge-01/leaderboard.csv
scoring/challenge-02/leaderboard.csv
scoring/overall-leaderboard.csv
scoring/challenge-01/round-scores/
scoring/challenge-02/round-scores/
```

Verify that:

- the correct teams appear
- the scores are numeric
- the leaderboard order is sensible
- the round scores correspond to the release that closed the prior round

---

## 11. Confirm the automatic commit

After the workflow finishes, look at the commit history.

You should see a commit similar to:

```text
Update automated leaderboard
```

That confirms that the workflow not only scored the round, but also wrote the results back into the repository.

---

## 12. Repeat for all rounds and both challenges

Repeat the same GitHub-based test sequence for:

- `release-03`
- `release-04`

Then repeat the full process for:

- `challenge-02`

This confirms that the workflow behaves correctly for both independent challenges.

---

## 13. Final success criteria

The repository is working correctly on GitHub if:

- release files are structured correctly
- team prediction files are structured correctly
- the workflow runs automatically on new releases
- scoring is triggered only by new data releases
- leaderboards are regenerated automatically
- the workflow commits the updated scoring results back to the repository

At that point, the GitHub-hosted competition workflow is ready for workshop use.
