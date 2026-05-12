#!/usr/bin/env python3
"""Validate a workshop forecast submission CSV."""

from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path

REQUIRED_COLUMNS = [
    "team_name",
    "challenge_id",
    "release_id",
    "target_date",
    "predicted_severe_cases",
]
OPTIONAL_NUMERIC_COLUMNS = [
    "predicted_total_cases",
    "r0",
    "vaccination_effectiveness",
    "cross_protection_days",
]


def _parse_float(value: str, column: str) -> tuple[bool, str]:
    if value == "" or value is None:
        return True, ""
    try:
        float(value)
        return True, ""
    except ValueError:
        return False, f"Column '{column}' must be numeric when provided"


def main(path: str) -> int:
    submission = Path(path)
    if not submission.exists():
        print(f"Missing file: {submission}", file=sys.stderr)
        return 1

    with submission.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLUMNS if c not in fields]
        if missing:
            print(f"Missing required columns: {', '.join(missing)}", file=sys.stderr)
            return 1

        row_count = 0
        for row_num, row in enumerate(reader, start=2):
            row_count += 1
            for col in REQUIRED_COLUMNS:
                if not str(row.get(col, "")).strip():
                    print(f"Row {row_num}: required column '{col}' is blank", file=sys.stderr)
                    return 1
            try:
                datetime.fromisoformat(row["target_date"])
            except ValueError:
                print(f"Row {row_num}: target_date must be ISO-8601 date/time", file=sys.stderr)
                return 1
            for col in ["predicted_severe_cases", *OPTIONAL_NUMERIC_COLUMNS]:
                ok, err = _parse_float(row.get(col, ""), col)
                if not ok:
                    print(f"Row {row_num}: {err}", file=sys.stderr)
                    return 1

        if row_count == 0:
            print("Submission file contains no data rows", file=sys.stderr)
            return 1

    print(f"Submission format looks OK: {submission}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
