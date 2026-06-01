#!/usr/bin/env python3
"""Validate prediction CSV files against the public release data and release metadata."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

EXPECTED_COLUMNS = ["week", "hospitalizations_per_100k", "r0"]
TOL = 1e-6


@dataclass
class ReleaseInfo:
    round_num: int
    released_through_week: int
    forecast_start_week: int
    forecast_end_week: int


class ValidationError(Exception):
    pass


def load_release_info(root: Path, round_num: int) -> ReleaseInfo:
    path = root / "data-release" / f"round-{round_num}" / "release_info.json"
    if not path.exists():
        raise ValidationError(f"Missing release metadata: {path}")
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    required = ["round", "released_through_week", "forecast_start_week", "forecast_end_week"]
    for key in required:
        if key not in data:
            raise ValidationError(f"{path}: missing key '{key}'")
    if int(data["round"]) != round_num:
        raise ValidationError(f"{path}: round number does not match filename round-{round_num}.csv")
    return ReleaseInfo(
        round_num=round_num,
        released_through_week=int(data["released_through_week"]),
        forecast_start_week=int(data["forecast_start_week"]),
        forecast_end_week=int(data["forecast_end_week"]),
    )


def load_public_release(root: Path, round_num: int) -> dict[int, float]:
    path = root / "data-release" / f"round-{round_num}" / "release.csv"
    if not path.exists():
        raise ValidationError(f"Missing public release file: {path}")
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ["week", "hospitalizations_per_100k"]:
            raise ValidationError(
                f"{path}: expected columns ['week', 'hospitalizations_per_100k'], found {reader.fieldnames}"
            )
        data: dict[int, float] = {}
        for idx, row in enumerate(reader, start=2):
            try:
                week = int(row["week"])
                hosp = float(row["hospitalizations_per_100k"])
            except Exception as exc:
                raise ValidationError(f"{path}: row {idx}: invalid numeric value") from exc
            if week in data:
                raise ValidationError(f"{path}: duplicate week {week}")
            data[week] = hosp
    if not data:
        raise ValidationError(f"{path}: file is empty")
    expected = list(range(1, max(data) + 1))
    if sorted(data) != expected:
        raise ValidationError(f"{path}: weeks must be contiguous from 1 through {max(data)}")
    return data


def find_prediction_files(root: Path) -> list[Path]:
    pred_dir = root / "predictions"
    if not pred_dir.exists():
        return []
    files: list[Path] = []
    for team_dir in sorted(p for p in pred_dir.iterdir() if p.is_dir() and p.name != "template"):
        for path in sorted(team_dir.glob("round-*.csv")):
            files.append(path)
    return files


def validate_file(root: Path, path: Path) -> list[str]:
    errors: list[str] = []
    round_num = None
    try:
        round_num = int(path.stem.split("-")[-1])
    except Exception:
        errors.append(f"{path}: filename must be round-N.csv")
        return errors

    try:
        info = load_release_info(root, round_num)
        release = load_public_release(root, round_num)
    except ValidationError as exc:
        return [str(exc)]

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != EXPECTED_COLUMNS:
            return [
                f"{path}: expected columns {EXPECTED_COLUMNS}, found {reader.fieldnames}"
            ]
        rows = list(reader)

    if not rows:
        return [f"{path}: file is empty"]

    weeks: list[int] = []
    seen = set()
    parsed_rows: dict[int, tuple[float, float]] = {}
    for idx, row in enumerate(rows, start=2):
        try:
            week = int(row["week"])
            hosp = float(row["hospitalizations_per_100k"])
            r0 = float(row["r0"])
        except Exception as exc:
            errors.append(f"{path}: row {idx}: non-numeric value")
            continue
        if week in seen:
            errors.append(f"{path}: row {idx}: duplicate week {week}")
        seen.add(week)
        weeks.append(week)
        parsed_rows[week] = (hosp, r0)

    expected_weeks = list(range(1, info.forecast_end_week + 1))
    if weeks != expected_weeks:
        errors.append(
            f"{path}: weeks must run exactly from 1 through {info.forecast_end_week} in ascending order"
        )

    if info.forecast_start_week != info.released_through_week + 1:
        errors.append(
            f"{path}: forecast_start_week should equal released_through_week + 1"
        )

    for week in range(1, info.released_through_week + 1):
        if week not in parsed_rows:
            errors.append(f"{path}: missing released week {week}")
            continue
        pred_hosp, _ = parsed_rows[week]
        if abs(pred_hosp - release[week]) > TOL:
            errors.append(
                f"{path}: week {week} hospitalizations_per_100k does not match released data"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()

    root = args.root.resolve()
    files = find_prediction_files(root)
    if not files:
        print("No prediction files found.")
        return 0

    errors: list[str] = []
    for path in files:
        errors.extend(validate_file(root, path))

    if errors:
        print("Validation failed:\n")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"Validated {len(files)} prediction file(s) successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
