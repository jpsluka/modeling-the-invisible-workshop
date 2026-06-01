#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

EXPECTED_COLUMNS = ['week', 'hospitalizations_per_100k', 'r0']
CHALLENGE_RE = re.compile(r'^challenge-(\d{2})$')
ROUND_RE = re.compile(r'^round-(\d{2})\.csv$')


class ValidationError(Exception):
    pass


def read_csv(path: Path):
    with path.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        return reader.fieldnames, rows


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def parse_int(value: str, path: Path, field: str) -> int:
    try:
        return int(value)
    except Exception as exc:
        raise ValidationError(f'{path}: invalid integer in {field}: {value!r}') from exc


def parse_float(value: str, path: Path, field: str) -> float:
    try:
        return float(value)
    except Exception as exc:
        raise ValidationError(f'{path}: invalid numeric value in {field}: {value!r}') from exc


def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / 'data-release').exists() and (candidate / 'predictions').exists():
            return candidate
    raise ValidationError('Could not locate repository root (missing data-release and predictions).')


def validate_prediction_file(root: Path, pred_path: Path) -> None:
    team_name = pred_path.parents[1].name
    challenge_name = pred_path.parents[0].name
    round_name = pred_path.name

    if not team_name.startswith('Team-'):
        raise ValidationError(f'{pred_path}: team folder must use Team-XX naming')

    if not CHALLENGE_RE.match(challenge_name):
        raise ValidationError(f'{pred_path}: challenge folder must use challenge-XX naming')

    if not ROUND_RE.match(round_name):
        raise ValidationError(f'{pred_path}: round file must use round-XX.csv naming')

    challenge_id = int(challenge_name.split('-')[1])
    round_id = int(Path(round_name).stem.split('-')[1])

    release_info_path = root / 'data-release' / challenge_name / f'round-{round_id:02d}' / 'release_info.json'
    if not release_info_path.exists():
        raise ValidationError(f'{pred_path}: missing release metadata {release_info_path}')

    release_info = load_json(release_info_path)
    forecast_start = int(release_info['forecast_start_week'])
    forecast_end = int(release_info['forecast_end_week'])
    released_through = int(release_info['released_through_week'])

    if forecast_start != released_through + 1:
        raise ValidationError(f'{pred_path}: forecast_start_week must equal released_through_week + 1')

    fieldnames, rows = read_csv(pred_path)
    if fieldnames != EXPECTED_COLUMNS:
        raise ValidationError(f'{pred_path}: expected header {EXPECTED_COLUMNS}, found {fieldnames}')

    if not rows:
        raise ValidationError(f'{pred_path}: file is empty')

    weeks = []
    seen = set()
    for row in rows:
        week = parse_int(row['week'], pred_path, 'week')
        hosp = parse_float(row['hospitalizations_per_100k'], pred_path, 'hospitalizations_per_100k')
        r0 = parse_float(row['r0'], pred_path, 'r0')
        if week in seen:
            raise ValidationError(f'{pred_path}: duplicate week {week}')
        seen.add(week)
        weeks.append(week)
        _ = hosp
        _ = r0

    expected_weeks = list(range(1, forecast_end + 1))
    if weeks != expected_weeks:
        raise ValidationError(
            f'{pred_path}: weeks must be exactly 1..{forecast_end} in order; found {weeks[:5]}...{weeks[-5:]}'
        )


def iter_prediction_files(root: Path):
    for team_dir in sorted((root / 'predictions').glob('Team-*')):
        if not team_dir.is_dir():
            continue
        for challenge_dir in sorted(team_dir.glob('challenge-*')):
            if not challenge_dir.is_dir():
                continue
            for pred_file in sorted(challenge_dir.glob('round-*.csv')):
                yield pred_file


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('.'))
    args = parser.parse_args()

    root = find_repo_root(args.root.resolve())
    errors = []
    for pred_file in iter_prediction_files(root):
        try:
            validate_prediction_file(root, pred_file)
        except Exception as exc:
            errors.append(str(exc))

    if errors:
        print('Validation failed:')
        for err in errors:
            print(f'- {err}')
        return 1

    print('Validation passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
