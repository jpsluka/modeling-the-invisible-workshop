#!/usr/bin/env python3
"""
Validate workshop prediction CSV files.

Expected prediction format:
team_name,challenge_round,prediction_date,target_week,forecast_target,
predicted_cases,lower_95_ci,upper_95_ci,estimated_peak_week,
estimated_total_cases,model_name,model_parameters

Rules:
- File path: predictions/<team-name>/round-<n>.csv
- team_name must match <team-name>
- challenge_round must match <n>
- forecast_target must be "overall"
- header must match exactly
- dates must be ISO-8601 (YYYY-MM-DD)
- numeric columns must parse as numbers
- lower_95_ci <= predicted_cases <= upper_95_ci
- duplicate target_week rows are not allowed
- model_parameters must be valid JSON object
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


EXPECTED_COLUMNS = [
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


class ValidationError(Exception):
    pass


def parse_iso_date(value: str, field_name: str, file_path: Path, row_num: int) -> date:
    try:
        return date.fromisoformat(value)
    except Exception as exc:
        raise ValidationError(
            f"{file_path}: row {row_num}: invalid {field_name} date '{value}'"
        ) from exc


def parse_float(value: str, field_name: str, file_path: Path, row_num: int) -> float:
    try:
        return float(value)
    except Exception as exc:
        raise ValidationError(
            f"{file_path}: row {row_num}: invalid {field_name} number '{value}'"
        ) from exc


def parse_int(value: str, field_name: str, file_path: Path, row_num: int) -> int:
    try:
        return int(value)
    except Exception as exc:
        raise ValidationError(
            f"{file_path}: row {row_num}: invalid {field_name} integer '{value}'"
        ) from exc


def parse_json_object(value: str, file_path: Path, row_num: int) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
    except Exception as exc:
        raise ValidationError(
            f"{file_path}: row {row_num}: model_parameters is not valid JSON"
        ) from exc

    if not isinstance(parsed, dict):
        raise ValidationError(
            f"{file_path}: row {row_num}: model_parameters must be a JSON object"
        )

    return parsed


def validate_prediction_file(file_path: Path, team_dir_name: str, round_num: int) -> list[str]:
    errors: list[str] = []

    try:
        with file_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != EXPECTED_COLUMNS:
                errors.append(
                    f"{file_path}: header mismatch.\n"
                    f"Expected: {EXPECTED_COLUMNS}\n"
                    f"Found:    {reader.fieldnames}"
                )
                return errors

            rows = list(reader)
            if not rows:
                errors.append(f"{file_path}: file is empty")
                return errors

            seen_target_weeks: set[str] = set()
            first_team_name: str | None = None
            first_prediction_date: str | None = None
            first_model_name: str | None = None
            first_model_parameters: dict[str, Any] | None = None

            for idx, row in enumerate(rows, start=2):
                row_team = row["team_name"].strip()
                row_round = parse_int(row["challenge_round"].strip(), "challenge_round", file_path, idx)
                prediction_date = row["prediction_date"].strip()
                target_week = row["target_week"].strip()
                forecast_target = row["forecast_target"].strip()
                model_name = row["model_name"].strip()
                model_parameters_raw = row["model_parameters"].strip()

                if row_team != team_dir_name:
                    errors.append(
                        f"{file_path}: row {idx}: team_name '{row_team}' does not match folder '{team_dir_name}'"
                    )

                if row_round != round_num:
                    errors.append(
                        f"{file_path}: row {idx}: challenge_round {row_round} does not match filename round-{round_num}.csv"
                    )

                if forecast_target != "overall":
                    errors.append(
                        f"{file_path}: row {idx}: forecast_target must be 'overall'"
                    )

                if not target_week:
                    errors.append(f"{file_path}: row {idx}: target_week is empty")
                else:
                    parse_iso_date(target_week, "target_week", file_path, idx)

                parse_iso_date(prediction_date, "prediction_date", file_path, idx)
                parse_iso_date(row["estimated_peak_week"].strip(), "estimated_peak_week", file_path, idx)

                predicted_cases = parse_float(row["predicted_cases"].strip(), "predicted_cases", file_path, idx)
                lower_95_ci = parse_float(row["lower_95_ci"].strip(), "lower_95_ci", file_path, idx)
                upper_95_ci = parse_float(row["upper_95_ci"].strip(), "upper_95_ci", file_path, idx)
                parse_float(row["estimated_total_cases"].strip(), "estimated_total_cases", file_path, idx)

                if lower_95_ci > predicted_cases:
                    errors.append(
                        f"{file_path}: row {idx}: lower_95_ci ({lower_95_ci}) > predicted_cases ({predicted_cases})"
                    )

                if upper_95_ci < predicted_cases:
                    errors.append(
                        f"{file_path}: row {idx}: upper_95_ci ({upper_95_ci}) < predicted_cases ({predicted_cases})"
                    )

                if not model_name:
                    errors.append(f"{file_path}: row {idx}: model_name is empty")

                model_parameters = parse_json_object(model_parameters_raw, file_path, idx)

                if target_week in seen_target_weeks:
                    errors.append(f"{file_path}: row {idx}: duplicate target_week '{target_week}'")
                seen_target_weeks.add(target_week)

                if first_team_name is None:
                    first_team_name = row_team
                elif row_team != first_team_name:
                    errors.append(f"{file_path}: row {idx}: team_name varies within the file")

                if first_prediction_date is None:
                    first_prediction_date = prediction_date
                elif prediction_date != first_prediction_date:
                    errors.append(f"{file_path}: row {idx}: prediction_date varies within the file")

                if first_model_name is None:
                    first_model_name = model_name
                elif model_name != first_model_name:
                    errors.append(f"{file_path}: row {idx}: model_name varies within the file")

                if first_model_parameters is None:
                    first_model_parameters = model_parameters
                elif model_parameters != first_model_parameters:
                    errors.append(f"{file_path}: row {idx}: model_parameters varies within the file")

    except OSError as exc:
        errors.append(f"{file_path}: could not read file: {exc}")

    return errors


def find_prediction_files(root: Path) -> list[Path]:
    predictions_dir = root / "predictions"
    if not predictions_dir.exists():
        return []

    files: list[Path] = []
    for team_dir in sorted(predictions_dir.iterdir()):
        if not team_dir.is_dir() or team_dir.name == "template":
            continue
        for csv_path in sorted(team_dir.glob("round-*.csv")):
            files.append(csv_path)

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

    for file_path in prediction_files:
        match = ROUND_FILE_RE.match(file_path.name)
        if not match:
            all_errors.append(f"{file_path}: filename must match round-<n>.csv")
            continue

        round_num = int(match.group(1))
        team_dir_name = file_path.parent.name
        all_errors.extend(validate_prediction_file(file_path, team_dir_name, round_num))

    if all_errors:
        print("Validation failed:\n")
        for error in all_errors:
            print(f"- {error}")
        print(f"\n{len(all_errors)} issue(s) found.")
        return 1

    print(f"Validated {len(prediction_files)} prediction file(s) successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())