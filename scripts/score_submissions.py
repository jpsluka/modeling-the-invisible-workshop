#!/usr/bin/env python3
"""Score workshop submissions against a reference answer key.

This is intentionally simple so organizers can adapt the metrics later.
"""

from __future__ import annotations

import csv
import math
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

KEY_FIELDS = ["team_name", "challenge_id", "release_id"]
PRED_FIELDS = ["predicted_severe_cases", "predicted_total_cases", "r0", "vaccination_effectiveness", "cross_protection_days"]
ACTUAL_FIELDS = ["actual_severe_cases", "actual_total_cases", "actual_r0", "actual_vaccination_effectiveness", "actual_cross_protection_days"]


@dataclass
class ScoreRow:
    team_name: str
    challenge_id: str
    release_id: str
    season_total_error: float
    rmse: float
    early_final_state_score: float
    parameter_estimation_score: float
    final_total_score: float


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def as_float(value: str | None) -> float | None:
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    return float(value)


def group_key(row: dict[str, str]) -> tuple[str, str, str]:
    return row["team_name"].strip(), row["challenge_id"].strip(), row["release_id"].strip()


def compute_score(pred_rows: list[dict[str, str]], ref_rows: list[dict[str, str]]) -> ScoreRow:
    pred_rows = sorted(pred_rows, key=lambda r: r["target_date"])
    ref_rows = sorted(ref_rows, key=lambda r: r["target_date"])

    team_name, challenge_id, release_id = group_key(pred_rows[0])

    pred_severe = [as_float(r.get("predicted_severe_cases")) for r in pred_rows]
    ref_severe = [as_float(r.get("actual_severe_cases")) for r in ref_rows]
    paired = [(p, a) for p, a in zip(pred_severe, ref_severe) if p is not None and a is not None]

    if not paired:
        raise ValueError(f"No overlapping prediction/actual severe-case values for {team_name} {challenge_id} {release_id}")

    diffs = [p - a for p, a in paired]
    rmse = math.sqrt(sum(d * d for d in diffs) / len(diffs))
    season_total_error = abs(sum(p for p, _ in paired) - sum(a for _, a in paired))

    final_actual = ref_severe[-1]
    first_pred = pred_severe[0]
    if final_actual is None or first_pred is None:
        early_final_state_score = 0.0
    else:
        early_final_state_score = 100.0 / (1.0 + abs(first_pred - final_actual))

    # Parameter estimation score uses whichever of the modeled parameters are supplied.
    param_pairs: list[tuple[float, float]] = []
    param_map = [
        ("r0", "actual_r0"),
        ("vaccination_effectiveness", "actual_vaccination_effectiveness"),
        ("cross_protection_days", "actual_cross_protection_days"),
    ]
    for pred_col, actual_col in param_map:
        pred_val = as_float(pred_rows[0].get(pred_col))
        actual_val = as_float(ref_rows[0].get(actual_col))
        if pred_val is not None and actual_val is not None:
            param_pairs.append((pred_val, actual_val))

    if param_pairs:
        param_error = sum(abs(p - a) / (abs(a) + 1e-9) for p, a in param_pairs) / len(param_pairs)
        parameter_estimation_score = max(0.0, 100.0 * (1.0 - param_error))
    else:
        parameter_estimation_score = 0.0

    # Lower errors should produce higher final scores.
    total_penalty = (0.04 * season_total_error) + (2.0 * rmse) + (100.0 - early_final_state_score) + (100.0 - parameter_estimation_score)
    final_total_score = max(0.0, 100.0 - total_penalty)

    return ScoreRow(
        team_name=team_name,
        challenge_id=challenge_id,
        release_id=release_id,
        season_total_error=season_total_error,
        rmse=rmse,
        early_final_state_score=early_final_state_score,
        parameter_estimation_score=parameter_estimation_score,
        final_total_score=final_total_score,
    )


def write_outputs(scores: Iterable[ScoreRow], leaderboard_path: Path, log_path: Path) -> None:
    scores = list(scores)
    leaderboard_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with leaderboard_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'team_name', 'challenge_id', 'release_id', 'final_total_score',
            'season_total_error', 'rmse', 'early_final_state_score',
            'parameter_estimation_score', 'last_updated',
        ])
        from datetime import datetime, timezone
        stamp = datetime.now(timezone.utc).isoformat()
        for row in sorted(scores, key=lambda r: (r.challenge_id, -r.final_total_score, r.team_name)):
            writer.writerow([
                row.team_name,
                row.challenge_id,
                row.release_id,
                f'{row.final_total_score:.4f}',
                f'{row.season_total_error:.4f}',
                f'{row.rmse:.4f}',
                f'{row.early_final_state_score:.4f}',
                f'{row.parameter_estimation_score:.4f}',
                stamp,
            ])

    with log_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['team_name', 'challenge_id', 'release_id', 'metric', 'score', 'notes'])
        for row in scores:
            writer.writerow([row.team_name, row.challenge_id, row.release_id, 'season_total_error', f'{row.season_total_error:.4f}', 'lower is better'])
            writer.writerow([row.team_name, row.challenge_id, row.release_id, 'rmse', f'{row.rmse:.4f}', 'lower is better'])
            writer.writerow([row.team_name, row.challenge_id, row.release_id, 'early_final_state_score', f'{row.early_final_state_score:.4f}', 'higher is better'])
            writer.writerow([row.team_name, row.challenge_id, row.release_id, 'parameter_estimation_score', f'{row.parameter_estimation_score:.4f}', 'higher is better'])
            writer.writerow([row.team_name, row.challenge_id, row.release_id, 'final_total_score', f'{row.final_total_score:.4f}', 'combined score'])


def main(reference_csv: str, submissions_dir: str, out_dir: str) -> int:
    ref_path = Path(reference_csv)
    sub_dir = Path(submissions_dir)
    out_path = Path(out_dir)

    if not ref_path.exists():
        print(f'Reference file not found: {ref_path}', file=sys.stderr)
        return 1
    if not sub_dir.exists():
        print(f'Submissions directory not found: {sub_dir}', file=sys.stderr)
        return 1

    ref_rows = read_csv(ref_path)
    ref_groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in ref_rows:
        ref_groups[group_key(row)].append(row)

    scores: list[ScoreRow] = []
    for submission in sorted(sub_dir.rglob('*.csv')):
        if submission.name.startswith('.'):
            continue
        pred_rows = read_csv(submission)
        if not pred_rows:
            continue
        key = group_key(pred_rows[0])
        if key not in ref_groups:
            print(f'Skipping {submission} (no matching reference rows)', file=sys.stderr)
            continue
        scores.append(compute_score(pred_rows, ref_groups[key]))

    write_outputs(scores, out_path / 'leaderboard.csv', out_path / 'score_log.csv')
    print(f'Wrote {len(scores)} scored submission(s) to {out_path}')
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: score_submissions.py <reference_csv> <submissions_dir> <output_dir>', file=sys.stderr)
        raise SystemExit(1)
    raise SystemExit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
