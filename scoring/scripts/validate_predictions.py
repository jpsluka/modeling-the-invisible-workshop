#!/usr/bin/env python3
"""
Validate team prediction files for the release-driven workshop repository.

Expected layout:

predictions/Team-XX/challenge-YY/round-ZZ.csv

Expected prediction CSV columns:

week,hospitalizations_per_100k,r0

Validation rules:
- Team folder must be Team-XX
- Challenge folder must be challenge-YY
- Filename must be round-ZZ.csv
- The matching release info must exist at:
  data-release/challenge-YY/release-ZZ/release_info.json
- The prediction file must include all weeks from 1 through forecast_end_week
- Week values must be strictly increasing integers
- hospitalizations_per_100k and r0 must be numeric
- Blank lines at the end of the file are allowed
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


EXPECTED_COLUMNS = ["week", "hospitalizations_per_100k", "r0"]

TEAM_RE = re.compile(r"^Team-\d{2}$")
CHALLENGE_RE = re.compile(r"^challenge-\d{2}$")
ROUND_RE = re.compile(r"^round-\d{2}\.csv$")


def _clean(value: Any) -> str:
    """Normalize CSV cell values for validation."""
    if value is None:
        return ""
    return str(value).strip()


def parse_int(value: Any, field_name: str, file_path: Path, row_num: int) -> int:
    value_str = _clean(value)
    try:
        return int(value_str)
    except Exception as exc:
        raise ValueError(
            f"{file_path}: row {row_num}: invalid integer in '{field_name}': {value_str!r}"
        ) from exc


def parse_float(value: Any, field_name: str, file_path: Path, row_num: int) -> float:
    value_str = _clean(value)
    try:
        return float(value_str)
    except Exception as exc:
        raise ValueError(
            f"{file_path}: row {row_num}: invalid number in '{field_name}': {value_str!r}"
        ) from exc


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def validate_prediction_file(pred_file: Path, root: Path) -> list[str]:
    errors: list[str] = []

    # Expected path:
    # predictions/Team-XX/challenge-YY/round-ZZ.csv
    try:
        challenge_dir = pred_file.parent
        team_dir = challenge_dir.parent
        predictions_dir = team_dir.parent
    except Exception:
        errors.append(f"{pred_file}: invalid path structure")
        return errors

    if predictions_dir.name != "predictions":
        errors.append(f"{pred_file}: must be inside predictions/Team-XX/challenge-YY/")
        return errors

    if not TEAM_RE.match(team_dir.name):
        errors.append(f"{pred_file}: invalid team folder name '{team_dir.name}'")
    if not CHALLENGE_RE.match(challenge_dir.name):
        errors.append(f"{pred_file}: invalid challenge folder name '{challenge_dir.name}'")
    if not ROUND_RE.match(pred_file.name):
        errors.append(f"{pred_file}: invalid round filename '{pred_file.name}'")

    if errors:
        return errors

    round_num = int(pred_file.stem.split("-")[1])
    challenge_num = int(challenge_dir.name.split("-")[1])

    # Matching release folder:
    # data-release/challenge-YY/release-ZZ/release_info.json
    release_dir = (
        root
        / "data-release"
        / challenge_dir.name
        / f"release-{round_num:02d}"
    )
    release_info_path = release_dir / "release_info.json"

    if not release_info_path.exists():
        errors.append(f"{pred_file}: missing release info file {release_info_path}")
        return errors

    try:
        release_info = json.loads(release_info_path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{pred_file}: could not parse {release_info_path}: {exc}")
        return errors

    # Basic consistency checks against release metadata.
    release_challenge_id = release_info.get("challenge_id")
    if release_challenge_id is not None:
        try:
            release_challenge_num = int(str(release_challenge_id).split("-")[-1]) if isinstance(release_challenge_id, str) else int(release_challenge_id)
            if release_challenge_num != challenge_num:
                errors.append(
                    f"{pred_file}: challenge folder does not match release_info.json "
                    f"({challenge_dir.name} vs {release_challenge_id})"
                )
        except Exception:
            errors.append(f"{pred_file}: invalid challenge_id in {release_info_path}")

    release_round_id = release_info.get("release_id")
    if release_round_id is not None:
        try:
            if int(release_round_id) != round_num:
                errors.append(
                    f"{pred_file}: round file does not match release_info.json "
                    f"({round_num} vs {release_round_id})"
                )
        except Exception:
            errors.append(f"{pred_file}: invalid release_id in {release_info_path}")

    if "forecast_end_week" not in release_info:
        errors.append(f"{pred_file}: missing forecast_end_week in {release_info_path}")
        return errors

    try:
        forecast_end_week = int(release_info["forecast_end_week"])
    except Exception:
        errors.append(f"{pred_file}: forecast_end_week must be an integer in {release_info_path}")
        return errors

    rows = read_csv_rows(pred_file)
    if not rows:
        errors.append(f"{pred_file}: file is empty")
        return errors

    if list(rows[0].keys()) != EXPECTED_COLUMNS:
        # DictReader preserves header order.
        found = list(rows[0].keys())
        errors.append(
            f"{pred_file}: header mismatch. Expected {EXPECTED_COLUMNS}, found {found}"
        )
        return errors

    parsed_weeks: list[int] = []

    for row_num, row in enumerate(rows, start=2):
        # Allow completely blank trailing lines.
        if not any(_clean(v) for v in row.values()):
            continue

        # Extra columns appear in DictReader rows under the None key.
        if None in row and any(_clean(v) for v in (row[None] or [])):
            errors.append(f"{pred_file}: row {row_num}: unexpected extra columns")
            continue

        try:
            week = parse_int(row.get("week"), "week", pred_file, row_num)
            hosp = parse_float(row.get("hospitalizations_per_100k"), "hospitalizations_per_100k", pred_file, row_num)
            r0 = parse_float(row.get("r0"), "r0", pred_file, row_num)
        except ValueError as exc:
            errors.append(str(exc))
            continue

        if week < 1:
            errors.append(f"{pred_file}: row {row_num}: week must be >= 1")
            continue

        parsed_weeks.append(week)

        # Keep parsed values referenced so the checks are explicit and visible.
        _ = hosp
        _ = r0

    if not parsed_weeks:
        errors.append(f"{pred_file}: no valid prediction rows found")
        return errors

    expected_weeks = list(range(1, forecast_end_week + 1))

    if parsed_weeks != expected_weeks:
        errors.append(
            f"{pred_file}: weeks must be strictly increasing and cover 1..{forecast_end_week}"
        )

    return errors


def find_prediction_files(root: Path) -> list[Path]:
    pred_root = root / "predictions"
    if not pred_root.exists():
        return []

    files: list[Path] = []
    for team_dir in sorted(pred_root.iterdir()):
        if not team_dir.is_dir() or not TEAM_RE.match(team_dir.name):
            continue
        for challenge_dir in sorted(team_dir.iterdir()):
            if not challenge_dir.is_dir() or not CHALLENGE_RE.match(challenge_dir.name):
                continue
            for pred_file in sorted(challenge_dir.glob("round-*.csv")):
                if ROUND_RE.match(pred_file.name):
                    files.append(pred_file)
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()

    root = args.root.resolve()
    prediction_files = find_prediction_files(root)

    if not prediction_files:
        print("No prediction files found. Nothing to validate.")
        return 0

    all_errors: list[str] = []

    for pred_file in prediction_files:
        all_errors.extend(validate_prediction_file(pred_file, root))

    if all_errors:
        print("Prediction validation failed:")
        for err in all_errors:
            print(f"- {err}")
        return 1

    print("Prediction validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
