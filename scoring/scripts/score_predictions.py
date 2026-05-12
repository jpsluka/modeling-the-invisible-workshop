#!/usr/bin/env python3
"""
Generate scores and leaderboard for workshop prediction files.

Truth file format expected at:
data-release/round-<n>/truth.csv

Truth CSV columns:
target_week,observed_cases

Optional parameter truth file:
data-release/round-<n>/true_parameters.json

Scoring logic:
- nRMSE on predicted_cases vs observed_cases
- peak-week error in weeks
- total-case relative error
- parameter relative error, if true_parameters.json exists

Round score = average of the available component scores.
Overall score = average of available round scores across rounds.
Lower is better.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from statistics import mean
from typing import Any


PREDICTION_COLUMNS = [
    "team_name",
    "challenge_round",
    "prediction_date",
    "target_week",
    "forecast_target",
    "predicted_cases",
    "lower_95_ci",
    "upper_95_ci",
    "estimated_peak_week",
    "estimated_total_cases",
    "model_name",
    "model_parameters",
]

ROUND_FILE_RE = re.compile(r"^round-(\d+)\.csv$")


class ScoreError(Exception):
    pass


def parse_iso_date(value: str) -> date:
    return date.fromisoformat(value)


def parse_float(value: str) -> float:
    return float(value)


def safe_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if math.isfinite(float(value)):
            return float(value)
        return None
    return None


def load_truth(round_dir: Path) -> dict[str, Any] | None:
    truth_csv = round_dir / "truth.csv"
    if not truth_csv.exists():
        return None

    observed_by_week: dict[str, float] = {}
    observed_series: list[tuple[date, float]] = []

    with truth_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        expected = ["target_week", "observed_cases"]
        if reader.fieldnames != expected:
            raise ScoreError(f"{truth_csv}: header mismatch. Expected {expected}, found {reader.fieldnames}")

        for idx, row in enumerate(reader, start=2):
            target_week = row["target_week"].strip()
            observed_cases = parse_float(row["observed_cases"].strip())

            if not target_week:
                raise ScoreError(f"{truth_csv}: row {idx}: target_week is empty")

            dt = parse_iso_date(target_week)
            observed_by_week[target_week] = observed_cases
            observed_series.append((dt, observed_cases))

    if not observed_series:
        raise ScoreError(f"{truth_csv}: file is empty")

    peak_week = max(observed_series, key=lambda item: item[1])[0]
    total_cases = sum(value for _, value in observed_series)

    true_parameters: dict[str, Any] | None = None
    params_json = round_dir / "true_parameters.json"
    if params_json.exists():
        with params_json.open(encoding="utf-8") as f:
            loaded = json.load(f)
        if isinstance(loaded, dict):
            true_parameters = loaded
        else:
            raise ScoreError(f"{params_json}: must contain a JSON object")

    return {
        "observed_by_week": observed_by_week,
        "peak_week": peak_week,
        "total_cases": total_cases,
        "true_parameters": true_parameters,
    }


def load_prediction_rows(file_path: Path) -> list[dict[str, str]]:
    with file_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != PREDICTION_COLUMNS:
            raise ScoreError(
                f"{file_path}: header mismatch. Expected {PREDICTION_COLUMNS}, found {reader.fieldnames}"
            )
        rows = list(reader)

    if not rows:
        raise ScoreError(f"{file_path}: file is empty")

    return rows


def calculate_round_score(
    prediction_rows: list[dict[str, str]],
    truth: dict[str, Any],
) -> dict[str, float]:
    squared_errors: list[float] = []
    observed_values: list[float] = []
    peak_errors_weeks: list[float] = []
    total_errors_ratio: list[float] = []

    observed_by_week: dict[str, float] = truth["observed_by_week"]
    peak_week: date = truth["peak_week"]
    total_cases: float = truth["total_cases"]
    true_parameters: dict[str, Any] | None = truth["true_parameters"]

    for row in prediction_rows:
        target_week = row["target_week"].strip()
        if target_week not in observed_by_week:
            raise ScoreError(f"Missing truth row for target_week={target_week!r}")

        observed_cases = observed_by_week[target_week]
        predicted_cases = parse_float(row["predicted_cases"].strip())

        squared_errors.append((predicted_cases - observed_cases) ** 2)
        observed_values.append(observed_cases)

        predicted_peak = parse_iso_date(row["estimated_peak_week"].strip())
        peak_errors_weeks.append(abs((predicted_peak - peak_week).days) / 7.0)

        predicted_total = parse_float(row["estimated_total_cases"].strip())
        if total_cases != 0:
            total_errors_ratio.append(abs(predicted_total - total_cases) / abs(total_cases))
        else:
            total_errors_ratio.append(abs(predicted_total - total_cases))

    rmse = math.sqrt(mean(squared_errors))
    mean_observed = mean(observed_values) if observed_values else 1.0
    nrmse = rmse / mean_observed if mean_observed != 0 else rmse

    metric_values: list[float] = [nrmse]

    peak_error_weeks = mean(peak_errors_weeks) if peak_errors_weeks else float("nan")
    if math.isfinite(peak_error_weeks):
        metric_values.append(peak_error_weeks)

    total_error_ratio = mean(total_errors_ratio) if total_errors_ratio else float("nan")
    if math.isfinite(total_error_ratio):
        metric_values.append(total_error_ratio)

    parameter_error_ratio = float("nan")
    if true_parameters:
        first_params_raw = prediction_rows[0]["model_parameters"].strip()
        predicted_params = json.loads(first_params_raw)
        if not isinstance(predicted_params, dict):
            raise ScoreError("model_parameters must be a JSON object")

        rel_errors: list[float] = []
        for key, true_value in true_parameters.items():
            if key not in predicted_params:
                continue

            true_val = safe_float(true_value)
            pred_val = safe_float(predicted_params.get(key))
            if true_val is None or pred_val is None:
                continue

            if true_val != 0:
                rel_errors.append(abs(pred_val - true_val) / abs(true_val))
            else:
                rel_errors.append(abs(pred_val - true_val))

        if rel_errors:
            parameter_error_ratio = mean(rel_errors)
            metric_values.append(parameter_error_ratio)

    round_score = mean(metric_values)

    return {
        "rmse": rmse,
        "nrmse": nrmse,
        "peak_error_weeks": peak_error_weeks,
        "total_error_ratio": total_error_ratio,
        "parameter_error_ratio": parameter_error_ratio,
        "round_score": round_score,
    }


def find_prediction_files(root: Path) -> list[Path]:
    predictions_dir = root / "predictions"
    if not predictions_dir.exists():
        return []

    files: list[Path] = []
    for team_dir in sorted(predictions_dir.iterdir()):
        if not team_dir.is_dir() or team_dir.name == "template":
            continue
        for csv_path in sorted(team_dir.glob("round-*.csv")):
            if ROUND_FILE_RE.match(csv_path.name):
                files.append(csv_path)

    return files


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return ""
        return f"{value:.6f}"
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()

    root = args.root.resolve()
    prediction_files = find_prediction_files(root)

    scoring_dir = root / "scoring"
    results_dir = scoring_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    round_summaries: list[dict[str, Any]] = []
    team_round_scores: dict[str, dict[int, float]] = defaultdict(dict)

    for file_path in prediction_files:
        match = ROUND_FILE_RE.match(file_path.name)
        if not match:
            continue

        round_num = int(match.group(1))
        round_dir = root / "data-release" / f"round-{round_num}"
        truth = load_truth(round_dir)
        if truth is None:
            print(f"Skipping {file_path}: missing truth file at {round_dir / 'truth.csv'}")
            continue

        rows = load_prediction_rows(file_path)
        team_name = file_path.parent.name
        scores = calculate_round_score(rows, truth)

        team_round_scores[team_name][round_num] = scores["round_score"]

        round_summaries.append(
            {
                "team_name": team_name,
                "round": round_num,
                "rmse": scores["rmse"],
                "nrmse": scores["nrmse"],
                "peak_error_weeks": scores["peak_error_weeks"],
                "total_error_ratio": scores["total_error_ratio"],
                "parameter_error_ratio": scores["parameter_error_ratio"],
                "round_score": scores["round_score"],
            }
        )

    # Write per-round score details.
    round_numbers = sorted({int(row["round"]) for row in round_summaries})
    for round_num in round_numbers:
        rows = [
            {
                "team_name": row["team_name"],
                "round": row["round"],
                "rmse": fmt(row["rmse"]),
                "nrmse": fmt(row["nrmse"]),
                "peak_error_weeks": fmt(row["peak_error_weeks"]),
                "total_error_ratio": fmt(row["total_error_ratio"]),
                "parameter_error_ratio": fmt(row["parameter_error_ratio"]),
                "round_score": fmt(row["round_score"]),
            }
            for row in sorted(
                [r for r in round_summaries if int(r["round"]) == round_num],
                key=lambda r: (r["round_score"], r["team_name"]),
            )
        ]

        write_csv(
            results_dir / f"round-{round_num}-scores.csv",
            [
                "team_name",
                "round",
                "rmse",
                "nrmse",
                "peak_error_weeks",
                "total_error_ratio",
                "parameter_error_ratio",
                "round_score",
            ],
            rows,
        )

    # Build overall leaderboard.
    leaderboard_rows: list[dict[str, Any]] = []
    all_teams = sorted(team_round_scores.keys())

    for team in all_teams:
        scores_by_round = team_round_scores[team]
        round_1 = scores_by_round.get(1)
        round_2 = scores_by_round.get(2)
        round_3 = scores_by_round.get(3)
        available_scores = [score for score in [round_1, round_2, round_3] if score is not None]
        overall_score = mean(available_scores) if available_scores else float("nan")

        leaderboard_rows.append(
            {
                "team_name": team,
                "round_1_score": round_1,
                "round_2_score": round_2,
                "round_3_score": round_3,
                "rounds_scored": len(available_scores),
                "overall_score": overall_score,
            }
        )

    leaderboard_rows.sort(key=lambda row: (row["overall_score"], row["team_name"]))

    for rank, row in enumerate(leaderboard_rows, start=1):
        row["rank"] = rank

    write_csv(
        scoring_dir / "leaderboard.csv",
        [
            "rank",
            "team_name",
            "round_1_score",
            "round_2_score",
            "round_3_score",
            "rounds_scored",
            "overall_score",
        ],
        [
            {
                "rank": row["rank"],
                "team_name": row["team_name"],
                "round_1_score": fmt(row["round_1_score"]),
                "round_2_score": fmt(row["round_2_score"]),
                "round_3_score": fmt(row["round_3_score"]),
                "rounds_scored": row["rounds_scored"],
                "overall_score": fmt(row["overall_score"]),
            }
            for row in leaderboard_rows
        ],
    )

    print(f"Scored {len(round_summaries)} submission file(s).")
    print(f"Wrote leaderboard to {scoring_dir / 'leaderboard.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())