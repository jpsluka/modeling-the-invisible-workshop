#!/usr/bin/env python3
"""Validate workshop forecast submissions."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

EXPECTED_COLUMNS = [
    "team_name",
    "challenge_round",
    "release_week",
    "forecast_week",
    "hospitalizations_per_100k_pred",
    "r0_pred",
    "model_name",
    "model_parameters",
]
ROUND_FILE_RE = re.compile(r"^round-(\d+)\.csv$")
SEASON_WEEKS = 40
REQUIRED_FUTURE_WEEKS = 4


class ValidationError(Exception):
    pass


def parse_int(value: str, field: str, file_path: Path, row_num: int) -> int:
    try:
        return int(str(value).strip())
    except Exception as exc:
        raise ValidationError(f"{file_path}: row {row_num}: {field} must be an integer") from exc


def parse_float(value: str, field: str, file_path: Path, row_num: int) -> float:
    try:
        return float(str(value).strip())
    except Exception as exc:
        raise ValidationError(f"{file_path}: row {row_num}: {field} must be numeric") from exc


def parse_json_object(value: str, file_path: Path, row_num: int) -> dict:
    try:
        parsed = json.loads(value)
    except Exception as exc:
        raise ValidationError(f"{file_path}: row {row_num}: model_parameters must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ValidationError(f"{file_path}: row {row_num}: model_parameters must be a JSON object")
    return parsed


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    match = ROUND_FILE_RE.match(path.name)
    if not match:
        return [f"{path}: filename must be round-<n>.csv"]

    round_from_name = int(match.group(1))
    if round_from_name not in {1, 2, 3}:
        errors.append(f"{path}: round number must be 1, 2, or 3")
        return errors

    try:
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != EXPECTED_COLUMNS:
                return [
                    f"{path}: header mismatch. Expected {EXPECTED_COLUMNS}, found {reader.fieldnames}"
                ]

            rows = list(reader)
            if len(rows) != REQUIRED_FUTURE_WEEKS:
                errors.append(f"{path}: expected exactly {REQUIRED_FUTURE_WEEKS} data rows")
                return errors

            team_name = None
            challenge_round = None
            release_week = None
            model_name = None
            model_parameters = None
            seen_forecast_weeks: set[int] = set()

            for row_num, row in enumerate(rows, start=2):
                row_team = str(row["team_name"]).strip()
                row_round = parse_int(row["challenge_round"], "challenge_round", path, row_num)
                row_release = parse_int(row["release_week"], "release_week", path, row_num)
                row_forecast = parse_int(row["forecast_week"], "forecast_week", path, row_num)
                hosp = parse_float(row["hospitalizations_per_100k_pred"], "hospitalizations_per_100k_pred", path, row_num)
                r0 = parse_float(row["r0_pred"], "r0_pred", path, row_num)
                row_model = str(row["model_name"]).strip()
                row_params = parse_json_object(str(row["model_parameters"]), path, row_num)

                if not row_team:
                    errors.append(f"{path}: row {row_num}: team_name is blank")
                if row_team != path.parent.name:
                    errors.append(f"{path}: row {row_num}: team_name must match the parent folder name")
                if row_round != round_from_name:
                    errors.append(f"{path}: row {row_num}: challenge_round must match the filename round number")
                if row_release < 1 or row_release > 36:
                    errors.append(f"{path}: row {row_num}: release_week must be between 1 and 36")
                if row_forecast <= row_release:
                    errors.append(f"{path}: row {row_num}: forecast_week must be after release_week")
                if row_forecast > SEASON_WEEKS:
                    errors.append(f"{path}: row {row_num}: forecast_week must be between 1 and {SEASON_WEEKS}")
                if not row_model:
                    errors.append(f"{path}: row {row_num}: model_name is blank")

                if team_name is None:
                    team_name = row_team
                elif row_team != team_name:
                    errors.append(f"{path}: row {row_num}: team_name must be constant within a file")

                if challenge_round is None:
                    challenge_round = row_round
                elif row_round != challenge_round:
                    errors.append(f"{path}: row {row_num}: challenge_round must be constant within a file")

                if release_week is None:
                    release_week = row_release
                elif row_release != release_week:
                    errors.append(f"{path}: row {row_num}: release_week must be constant within a file")

                if model_name is None:
                    model_name = row_model
                elif row_model != model_name:
                    errors.append(f"{path}: row {row_num}: model_name must be constant within a file")

                if model_parameters is None:
                    model_parameters = row_params
                elif row_params != model_parameters:
                    errors.append(f"{path}: row {row_num}: model_parameters must be constant within a file")

                if row_forecast in seen_forecast_weeks:
                    errors.append(f"{path}: row {row_num}: duplicate forecast_week {row_forecast}")
                seen_forecast_weeks.add(row_forecast)

            if release_week is not None:
                expected_forecasts = {release_week + i for i in range(1, REQUIRED_FUTURE_WEEKS + 1)}
                if seen_forecast_weeks != expected_forecasts:
                    errors.append(
                        f"{path}: forecast_week values must be exactly {sorted(expected_forecasts)}"
                    )

    except OSError as exc:
        errors.append(f"{path}: could not read file: {exc}")

    return errors


def find_prediction_files(root: Path) -> list[Path]:
    pred_dir = root / 'predictions'
    if not pred_dir.exists():
        return []
    files: list[Path] = []
    for team_dir in sorted(pred_dir.iterdir()):
        if not team_dir.is_dir() or team_dir.name == 'template':
            continue
        files.extend(sorted(team_dir.glob('round-*.csv')))
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('.'))
    args = parser.parse_args()

    root = args.root.resolve()
    files = find_prediction_files(root)
    if not files:
        print('No prediction files found. Nothing to validate.')
        return 0

    all_errors: list[str] = []
    for file_path in files:
        all_errors.extend(validate_file(file_path))

    if all_errors:
        print('Validation failed:\n')
        for err in all_errors:
            print(f'- {err}')
        return 1

    print(f'Validated {len(files)} prediction file(s) successfully.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
