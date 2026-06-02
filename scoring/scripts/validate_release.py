#!/usr/bin/env python3
"""
Validate organizer release folders for the release-driven workshop repository.

Expected layout:

data-release/challenge-XX/release-YY/
    release_info.json
    public.csv
    truth_previous_round.csv   # only for releases that close a previous round

Validation goals:
- report precise file/field errors
- ensure folder names match the metadata
- ensure public.csv has the correct weeks and columns
- ensure truth_previous_round.csv exists only when expected
- ensure truth_previous_round.csv has the correct weeks and columns
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


CHALLENGE_RE = re.compile(r"^challenge-(\d{2})$")
RELEASE_RE = re.compile(r"^release-(\d{2})$")

PUBLIC_COLUMNS = ["week", "hospitalizations_per_100k"]
TRUTH_COLUMNS = ["week", "hospitalizations_per_100k", "r0"]


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def parse_int(value: Any, field_name: str, file_path: Path) -> int:
    value_str = _clean(value)
    try:
        return int(value_str)
    except Exception as exc:
        raise ValueError(
            f"{file_path}: invalid integer in '{field_name}': {value_str!r}"
        ) from exc


def parse_float(value: Any, field_name: str, file_path: Path) -> float:
    value_str = _clean(value)
    try:
        return float(value_str)
    except Exception as exc:
        raise ValueError(
            f"{file_path}: invalid number in '{field_name}': {value_str!r}"
        ) from exc


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def validate_release_info(
    info_path: Path,
    challenge_dir_name: str,
    release_dir_name: str,
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []

    if not info_path.exists():
        return None, [f"{info_path}: missing file"]

    try:
        info = json.loads(info_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [f"{info_path}: could not parse JSON: {exc}"]

    if not isinstance(info, dict):
        return None, [f"{info_path}: JSON root must be an object"]

    # Required fields
    required_fields = [
        "challenge_id",
        "release_id",
        "released_through_week",
        "forecast_start_week",
        "forecast_end_week",
    ]
    for field in required_fields:
        if field not in info:
            errors.append(f"{info_path}: missing required key '{field}'")

    if errors:
        return None, errors

    # Parse and validate challenge_id
    challenge_id = _clean(info.get("challenge_id"))
    if challenge_id != challenge_dir_name:
        errors.append(
            f"{info_path}: challenge_id '{challenge_id}' does not match folder '{challenge_dir_name}'"
        )

    # Parse and validate release_id
    try:
        release_id_int = int(info.get("release_id"))
    except Exception:
        errors.append(f"{info_path}: release_id must be an integer")
        release_id_int = None

    if release_id_int is not None:
        expected_release_id = int(release_dir_name.split("-")[1])
        if release_id_int != expected_release_id:
            errors.append(
                f"{info_path}: release_id {release_id_int} does not match folder '{release_dir_name}'"
            )

    # Parse week values
    try:
        released_through_week = int(info.get("released_through_week"))
    except Exception:
        errors.append(f"{info_path}: released_through_week must be an integer")
        released_through_week = None

    try:
        forecast_start_week = int(info.get("forecast_start_week"))
    except Exception:
        errors.append(f"{info_path}: forecast_start_week must be an integer")
        forecast_start_week = None

    try:
        forecast_end_week = int(info.get("forecast_end_week"))
    except Exception:
        errors.append(f"{info_path}: forecast_end_week must be an integer")
        forecast_end_week = None

    if (
        released_through_week is not None
        and forecast_start_week is not None
        and forecast_end_week is not None
    ):
        if forecast_start_week != released_through_week + 1:
            errors.append(
                f"{info_path}: forecast_start_week ({forecast_start_week}) must equal released_through_week + 1 ({released_through_week + 1})"
            )
        if forecast_end_week < forecast_start_week:
            errors.append(
                f"{info_path}: forecast_end_week ({forecast_end_week}) must be >= forecast_start_week ({forecast_start_week})"
            )

    # Optional scoring metadata
    scores_round_id = info.get("scores_round_id")
    scores_start_week = info.get("scores_round_start_week")
    scores_end_week = info.get("scores_round_end_week")

    if scores_round_id is not None:
        try:
            scores_round_id_int = int(scores_round_id)
        except Exception:
            errors.append(f"{info_path}: scores_round_id must be an integer if present")
            scores_round_id_int = None

        try:
            scores_start_week_int = int(scores_start_week)
        except Exception:
            errors.append(f"{info_path}: scores_round_start_week must be an integer if present")
            scores_start_week_int = None

        try:
            scores_end_week_int = int(scores_end_week)
        except Exception:
            errors.append(f"{info_path}: scores_round_end_week must be an integer if present")
            scores_end_week_int = None

        if (
            scores_round_id_int is not None
            and scores_start_week_int is not None
            and scores_end_week_int is not None
        ):
            if scores_start_week_int > scores_end_week_int:
                errors.append(
                    f"{info_path}: scores_round_start_week ({scores_start_week_int}) must be <= scores_round_end_week ({scores_end_week_int})"
                )

    return info, errors


def validate_public_csv(public_path: Path, released_through_week: int) -> list[str]:
    errors: list[str] = []

    if not public_path.exists():
        return [f"{public_path}: missing file"]

    rows = read_csv_rows(public_path)
    if not rows:
        return [f"{public_path}: file is empty"]

    found_columns = list(rows[0].keys())
    if found_columns != PUBLIC_COLUMNS:
        return [
            f"{public_path}: header mismatch. Expected {PUBLIC_COLUMNS}, found {found_columns}"
        ]

    parsed_weeks: list[int] = []

    for row_num, row in enumerate(rows, start=2):
        if not any(_clean(v) for v in row.values()):
            continue

        if None in row and any(_clean(v) for v in (row[None] or [])):
            errors.append(f"{public_path}: row {row_num}: unexpected extra columns")
            continue

        try:
            week = parse_int(row.get("week"), "week", public_path)
        except ValueError as exc:
            errors.append(f"{public_path}: row {row_num}: {exc}")
            continue

        try:
            hosp = parse_float(
                row.get("hospitalizations_per_100k"),
                "hospitalizations_per_100k",
                public_path,
            )
        except ValueError as exc:
            errors.append(f"{public_path}: row {row_num}: {exc}")
            continue

        if week < 1:
            errors.append(f"{public_path}: row {row_num}: week must be >= 1")
            continue

        parsed_weeks.append(week)
        _ = hosp

    expected_weeks = list(range(1, released_through_week + 1))
    if parsed_weeks != expected_weeks:
        errors.append(
            f"{public_path}: weeks must be exactly 1..{released_through_week} in order"
        )

    return errors


def validate_truth_csv(
    truth_path: Path,
    scores_start_week: int,
    scores_end_week: int,
) -> list[str]:
    errors: list[str] = []

    if not truth_path.exists():
        return [f"{truth_path}: missing file"]

    rows = read_csv_rows(truth_path)
    if not rows:
        return [f"{truth_path}: file is empty"]

    found_columns = list(rows[0].keys())
    if found_columns != TRUTH_COLUMNS:
        return [
            f"{truth_path}: header mismatch. Expected {TRUTH_COLUMNS}, found {found_columns}"
        ]

    parsed_weeks: list[int] = []

    for row_num, row in enumerate(rows, start=2):
        if not any(_clean(v) for v in row.values()):
            continue

        if None in row and any(_clean(v) for v in (row[None] or [])):
            errors.append(f"{truth_path}: row {row_num}: unexpected extra columns")
            continue

        try:
            week = parse_int(row.get("week"), "week", truth_path)
        except ValueError as exc:
            errors.append(f"{truth_path}: row {row_num}: {exc}")
            continue

        try:
            hosp = parse_float(
                row.get("hospitalizations_per_100k"),
                "hospitalizations_per_100k",
                truth_path,
            )
            r0 = parse_float(row.get("r0"), "r0", truth_path)
        except ValueError as exc:
            errors.append(f"{truth_path}: row {row_num}: {exc}")
            continue

        if week < 1:
            errors.append(f"{truth_path}: row {row_num}: week must be >= 1")
            continue

        parsed_weeks.append(week)
        _ = hosp
        _ = r0

    expected_weeks = list(range(scores_start_week, scores_end_week + 1))
    if parsed_weeks != expected_weeks:
        errors.append(
            f"{truth_path}: weeks must be exactly {scores_start_week}..{scores_end_week} in order"
        )

    return errors


def validate_release_folder(release_dir: Path, root: Path) -> list[str]:
    errors: list[str] = []

    challenge_dir = release_dir.parent
    release_dir_name = release_dir.name
    challenge_dir_name = challenge_dir.name

    if not CHALLENGE_RE.match(challenge_dir_name):
        errors.append(f"{challenge_dir}: invalid challenge folder name")
        return errors

    if not RELEASE_RE.match(release_dir_name):
        errors.append(f"{release_dir}: invalid release folder name")
        return errors

    info_path = release_dir / "release_info.json"
    public_path = release_dir / "public.csv"
    truth_path = release_dir / "truth_previous_round.csv"

    info, info_errors = validate_release_info(
        info_path=info_path,
        challenge_dir_name=challenge_dir_name,
        release_dir_name=release_dir_name,
    )
    errors.extend(info_errors)

    if info is None:
        return errors

    try:
        released_through_week = int(info["released_through_week"])
    except Exception:
        errors.append(f"{info_path}: released_through_week must be an integer")
        return errors

    try:
        forecast_start_week = int(info["forecast_start_week"])
        forecast_end_week = int(info["forecast_end_week"])
    except Exception:
        errors.append(f"{info_path}: forecast_start_week and forecast_end_week must be integers")
        return errors

    # Validate public.csv
    errors.extend(validate_public_csv(public_path, released_through_week))

    # Validate truth_previous_round.csv only when the release is supposed to close a round.
    scores_round_id = info.get("scores_round_id")
    if scores_round_id is not None:
        if not truth_path.exists():
            errors.append(
                f"{truth_path}: missing file, but this release is configured to score a previous round"
            )
        else:
            try:
                scores_start_week = int(info["scores_round_start_week"])
                scores_end_week = int(info["scores_round_end_week"])
            except Exception:
                errors.append(
                    f"{info_path}: scores_round_start_week and scores_round_end_week must be integers when scores_round_id is present"
                )
                scores_start_week = None
                scores_end_week = None

            if scores_start_week is not None and scores_end_week is not None:
                errors.extend(
                    validate_truth_csv(
                        truth_path=truth_path,
                        scores_start_week=scores_start_week,
                        scores_end_week=scores_end_week,
                    )
                )
    else:
        # For release 01, truth_previous_round.csv should not be present.
        if truth_path.exists():
            errors.append(
                f"{truth_path}: file should not exist for an opening release that does not score a previous round"
            )

    # Extra sanity check: ensure the forecast horizon is plausible.
    if forecast_end_week < forecast_start_week:
        errors.append(
            f"{info_path}: forecast_end_week ({forecast_end_week}) must be >= forecast_start_week ({forecast_start_week})"
        )

    return errors


def find_release_folders(root: Path) -> list[Path]:
    release_root = root / "data-release"
    if not release_root.exists():
        return []

    folders: list[Path] = []
    for challenge_dir in sorted([p for p in release_root.iterdir() if p.is_dir()]):
        for release_dir in sorted([p for p in challenge_dir.iterdir() if p.is_dir()]):
            if RELEASE_RE.match(release_dir.name):
                folders.append(release_dir)
    return folders


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()

    root = args.root.resolve()
    release_folders = find_release_folders(root)

    if not release_folders:
        print("No release folders found. Nothing to validate.")
        return 0

    all_errors: list[str] = []

    for release_dir in release_folders:
        all_errors.extend(validate_release_folder(release_dir, root))

    if all_errors:
        print("Release validation failed:")
        for err in all_errors:
            print(f"- {err}")
        return 1

    print("Release validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
