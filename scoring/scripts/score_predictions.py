#!/usr/bin/env python3
"""Score workshop submissions against the reference answers."""

from __future__ import annotations

import argparse
import csv
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

PRED_COLUMNS = [
    "team_name",
    "challenge_round",
    "release_week",
    "forecast_week",
    "hospitalizations_per_100k_pred",
    "r0_pred",
    "model_name",
    "model_parameters",
]
REF_COLUMNS = ["challenge_round", "forecast_week", "hospitalizations_per_100k", "r0"]
ROUND_FILE_RE = re.compile(r"^round-(\d+)\.csv$")
REQUIRED_FUTURE_WEEKS = 4


@dataclass
class RoundResult:
    team_name: str
    challenge_round: int
    release_week: int
    hosp_nrmse: float
    r0_nrmse: float
    round_score: float


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def as_float(value: str) -> float:
    return float(str(value).strip())


def as_int(value: str) -> int:
    return int(str(value).strip())


def nrmse(preds: list[float], truths: list[float]) -> float:
    if len(preds) != len(truths) or not preds:
        raise ValueError('Cannot score empty or mismatched series')
    mse = mean((p - t) ** 2 for p, t in zip(preds, truths))
    rmse = math.sqrt(mse)
    avg_truth = mean(truths)
    return rmse if avg_truth == 0 else rmse / avg_truth


def load_reference(reference_csv: Path) -> dict[tuple[int, int], dict[str, float]]:
    if not reference_csv.exists():
        raise FileNotFoundError(f'Reference file not found: {reference_csv}')
    rows = read_csv(reference_csv)
    ref: dict[tuple[int, int], dict[str, float]] = {}
    for row in rows:
        key = (as_int(row['challenge_round']), as_int(row['forecast_week']))
        ref[key] = {
            'hospitalizations_per_100k': as_float(row['hospitalizations_per_100k']),
            'r0': as_float(row['r0']),
        }
    return ref


def score_submission(pred_path: Path, ref: dict[tuple[int, int], dict[str, float]]) -> RoundResult:
    rows = read_csv(pred_path)
    if len(rows) != REQUIRED_FUTURE_WEEKS:
        raise ValueError(f'{pred_path}: expected {REQUIRED_FUTURE_WEEKS} rows')

    team_name = rows[0]['team_name'].strip()
    challenge_round = as_int(rows[0]['challenge_round'])
    release_week = as_int(rows[0]['release_week'])

    rows = sorted(rows, key=lambda r: as_int(r['forecast_week']))
    hosp_preds: list[float] = []
    r0_preds: list[float] = []
    hosp_truth: list[float] = []
    r0_truth: list[float] = []

    expected_weeks = [release_week + i for i in range(1, REQUIRED_FUTURE_WEEKS + 1)]
    actual_weeks = [as_int(r['forecast_week']) for r in rows]
    if actual_weeks != expected_weeks:
        raise ValueError(f'{pred_path}: forecast_week values must be {expected_weeks}')

    for row in rows:
        wk = as_int(row['forecast_week'])
        key = (challenge_round, wk)
        if key not in ref:
            raise ValueError(f'{pred_path}: missing reference row for round {challenge_round}, week {wk}')
        truth_row = ref[key]
        hosp_preds.append(as_float(row['hospitalizations_per_100k_pred']))
        r0_preds.append(as_float(row['r0_pred']))
        hosp_truth.append(truth_row['hospitalizations_per_100k'])
        r0_truth.append(truth_row['r0'])

    hosp_score = nrmse(hosp_preds, hosp_truth)
    r0_score = nrmse(r0_preds, r0_truth)
    round_score = mean([hosp_score, r0_score])
    return RoundResult(team_name, challenge_round, release_week, hosp_score, r0_score, round_score)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def fmt(x: float | None) -> str:
    if x is None:
        return ''
    return f'{x:.6f}'


def find_prediction_files(root: Path) -> list[Path]:
    pred_dir = root / 'predictions'
    if not pred_dir.exists():
        return []
    files: list[Path] = []
    for team_dir in sorted(pred_dir.iterdir()):
        if not team_dir.is_dir() or team_dir.name == 'template':
            continue
        for p in sorted(team_dir.glob('round-*.csv')):
            if ROUND_FILE_RE.match(p.name):
                files.append(p)
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('.'))
    args = parser.parse_args()

    root = args.root.resolve()
    reference_csv = root / 'scoring' / 'reference_answers.csv'
    ref = load_reference(reference_csv)

    pred_files = find_prediction_files(root)
    results: list[RoundResult] = []
    for pred_path in pred_files:
        results.append(score_submission(pred_path, ref))

    scoring_dir = root / 'scoring'
    results_dir = scoring_dir / 'results'
    results_dir.mkdir(parents=True, exist_ok=True)

    # Round detail files and score log.
    score_log_rows: list[dict[str, object]] = []
    for round_num in (1, 2, 3):
        round_rows = [r for r in results if r.challenge_round == round_num]
        round_rows.sort(key=lambda r: (r.round_score, r.team_name))
        write_csv(
            results_dir / f'round-{round_num}-scores.csv',
            ['team_name', 'challenge_round', 'release_week', 'hosp_nrmse', 'r0_nrmse', 'round_score'],
            [
                {
                    'team_name': r.team_name,
                    'challenge_round': r.challenge_round,
                    'release_week': r.release_week,
                    'hosp_nrmse': fmt(r.hosp_nrmse),
                    'r0_nrmse': fmt(r.r0_nrmse),
                    'round_score': fmt(r.round_score),
                }
                for r in round_rows
            ],
        )
        score_log_rows.extend(
            {
                'team_name': r.team_name,
                'challenge_round': r.challenge_round,
                'release_week': r.release_week,
                'hosp_nrmse': fmt(r.hosp_nrmse),
                'r0_nrmse': fmt(r.r0_nrmse),
                'round_score': fmt(r.round_score),
            }
            for r in round_rows
        )

    write_csv(
        scoring_dir / 'score_log.csv',
        ['team_name', 'challenge_round', 'release_week', 'hosp_nrmse', 'r0_nrmse', 'round_score'],
        score_log_rows,
    )

    # Leaderboard.
    by_team: dict[str, dict[int, RoundResult]] = defaultdict(dict)
    for r in results:
        by_team[r.team_name][r.challenge_round] = r

    leaderboard_rows: list[dict[str, object]] = []
    for team_name in sorted(by_team):
        team_rounds = by_team[team_name]
        round_scores = [team_rounds[k].round_score for k in sorted(team_rounds)]
        overall = mean(round_scores) if round_scores else None
        leaderboard_rows.append(
            {
                'team_name': team_name,
                'round_1_score': fmt(team_rounds[1].round_score) if 1 in team_rounds else '',
                'round_2_score': fmt(team_rounds[2].round_score) if 2 in team_rounds else '',
                'round_3_score': fmt(team_rounds[3].round_score) if 3 in team_rounds else '',
                'rounds_scored': len(round_scores),
                'overall_score': fmt(overall),
            }
        )

    leaderboard_rows.sort(key=lambda r: (float(r['overall_score']) if r['overall_score'] else float('inf'), r['team_name']))
    for i, row in enumerate(leaderboard_rows, start=1):
        row['rank'] = i

    write_csv(
        scoring_dir / 'leaderboard.csv',
        ['rank', 'team_name', 'round_1_score', 'round_2_score', 'round_3_score', 'rounds_scored', 'overall_score'],
        leaderboard_rows,
    )

    print(f'Scored {len(results)} submission file(s).')
    print(f'Wrote leaderboard to {scoring_dir / "leaderboard.csv"}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
