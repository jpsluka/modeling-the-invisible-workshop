#!/usr/bin/env python3
"""Score prediction CSV files using organizer-held truth data."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

EXPECTED_COLUMNS = ["week", "hospitalizations_per_100k", "r0"]


@dataclass
class ReleaseInfo:
    round_num: int
    released_through_week: int
    forecast_start_week: int
    forecast_end_week: int


class ScoreError(Exception):
    pass


def load_release_info(root: Path, round_num: int) -> ReleaseInfo:
    path = root / "data-release" / f"round-{round_num}" / "release_info.json"
    if not path.exists():
        raise ScoreError(f"Missing release metadata: {path}")
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return ReleaseInfo(
        round_num=round_num,
        released_through_week=int(data["released_through_week"]),
        forecast_start_week=int(data["forecast_start_week"]),
        forecast_end_week=int(data["forecast_end_week"]),
    )


def load_truth(root: Path) -> dict[int, dict[int, tuple[float, float]]]:
    truth_path = root / "scoring" / "reference_answers.csv"
    if not truth_path.exists():
        truth_path = root / "scoring" / "reference_answers.example.csv"
    if not truth_path.exists():
        raise ScoreError("No reference_answers.csv or reference_answers.example.csv found")

    truth: dict[int, dict[int, tuple[float, float]]] = defaultdict(dict)
    with truth_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        expected = ["round", "week", "hospitalizations_per_100k", "r0"]
        if reader.fieldnames != expected:
            raise ScoreError(f"{truth_path}: expected {expected}, found {reader.fieldnames}")
        for idx, row in enumerate(reader, start=2):
            try:
                rnd = int(row["round"])
                week = int(row["week"])
                hosp = float(row["hospitalizations_per_100k"])
                r0 = float(row["r0"])
            except Exception as exc:
                raise ScoreError(f"{truth_path}: row {idx}: invalid numeric value") from exc
            truth[rnd][week] = (hosp, r0)
    return truth


def find_prediction_files(root: Path) -> list[Path]:
    pred_dir = root / "predictions"
    if not pred_dir.exists():
        return []
    files: list[Path] = []
    for team_dir in sorted(p for p in pred_dir.iterdir() if p.is_dir() and p.name != "template"):
        for path in sorted(team_dir.glob("round-*.csv")):
            files.append(path)
    return files


def read_prediction_file(path: Path) -> dict[int, tuple[float, float]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != EXPECTED_COLUMNS:
            raise ScoreError(f"{path}: expected columns {EXPECTED_COLUMNS}, found {reader.fieldnames}")
        rows = list(reader)
    data: dict[int, tuple[float, float]] = {}
    for idx, row in enumerate(rows, start=2):
        try:
            week = int(row["week"])
            hosp = float(row["hospitalizations_per_100k"])
            r0 = float(row["r0"])
        except Exception as exc:
            raise ScoreError(f"{path}: row {idx}: invalid numeric value") from exc
        data[week] = (hosp, r0)
    return data


def rmse(pred: list[float], truth: list[float]) -> float:
    if not pred:
        return float("nan")
    return math.sqrt(mean((p - t) ** 2 for p, t in zip(pred, truth)))


def nrmse(pred: list[float], truth: list[float]) -> float:
    base = mean(truth)
    err = rmse(pred, truth)
    return err / base if base else err


def score_round(pred: dict[int, tuple[float, float]], truth: dict[int, tuple[float, float]], info: ReleaseInfo) -> tuple[float, float, float]:
    forecast_weeks = list(range(info.released_through_week + 1, info.forecast_end_week + 1))
    pred_h = []
    truth_h = []
    pred_r0 = []
    truth_r0 = []
    for week in forecast_weeks:
        if week not in pred:
            raise ScoreError(f"Missing forecast week {week}")
        if week not in truth:
            raise ScoreError(f"Missing truth week {week}")
        ph, pr = pred[week]
        th, tr = truth[week]
        pred_h.append(ph)
        truth_h.append(th)
        pred_r0.append(pr)
        truth_r0.append(tr)
    hosp_nrmse = nrmse(pred_h, truth_h)
    r0_rmse = rmse(pred_r0, truth_r0)
    round_score = mean([hosp_nrmse, r0_rmse])
    return hosp_nrmse, r0_rmse, round_score


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()

    root = args.root.resolve()
    files = find_prediction_files(root)
    if not files:
        print("No prediction files found.")
        return 0

    truth = load_truth(root)
    results_dir = root / "scoring" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    per_round_rows: dict[int, list[dict[str, Any]]] = defaultdict(list)
    team_round_scores: dict[str, dict[int, float]] = defaultdict(dict)

    for path in files:
        team_name = path.parent.name
        try:
            round_num = int(path.stem.split("-")[-1])
        except Exception:
            raise ScoreError(f"{path}: filename must be round-N.csv")

        info = load_release_info(root, round_num)
        pred = read_prediction_file(path)
        hosp_nrmse, r0_rmse, round_score = score_round(pred, truth[round_num], info)
        team_round_scores[team_name][round_num] = round_score
        per_round_rows[round_num].append(
            {
                "team_name": team_name,
                "hospitalization_nrmse": f"{hosp_nrmse:.6f}",
                "r0_rmse": f"{r0_rmse:.6f}",
                "round_score": f"{round_score:.6f}",
            }
        )

    for round_num, rows in per_round_rows.items():
        rows.sort(key=lambda r: (float(r["round_score"]), float(r["hospitalization_nrmse"]), float(r["r0_rmse"]), r["team_name"]))
        write_csv(
            results_dir / f"round-{round_num}-scores.csv",
            ["team_name", "hospitalization_nrmse", "r0_rmse", "round_score"],
            rows,
        )

    leaderboard_rows = []
    for team_name, scores_by_round in sorted(team_round_scores.items()):
        round_scores = [scores_by_round[r] for r in sorted(scores_by_round)]
        overall = mean(round_scores)
        leaderboard_rows.append(
            {
                "team_name": team_name,
                "round_1_score": f"{scores_by_round.get(1, float('nan')):.6f}" if 1 in scores_by_round else "",
                "round_2_score": f"{scores_by_round.get(2, float('nan')):.6f}" if 2 in scores_by_round else "",
                "round_3_score": f"{scores_by_round.get(3, float('nan')):.6f}" if 3 in scores_by_round else "",
                "rounds_scored": str(len(round_scores)),
                "overall_score": f"{overall:.6f}",
            }
        )

    leaderboard_rows.sort(key=lambda r: (float(r["overall_score"]), r["team_name"]))
    for rank, row in enumerate(leaderboard_rows, start=1):
        row["rank"] = str(rank)

    write_csv(
        root / "scoring" / "leaderboard.csv",
        ["rank", "team_name", "round_1_score", "round_2_score", "round_3_score", "rounds_scored", "overall_score"],
        leaderboard_rows,
    )

    print(f"Scored {len(files)} prediction file(s).")
    print(f"Wrote leaderboard to {root / 'scoring' / 'leaderboard.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
