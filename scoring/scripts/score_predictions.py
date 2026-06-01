#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import pandas as pd

EXPECTED_COLUMNS = ['week', 'hospitalizations_per_100k', 'r0']


def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / 'data-release').exists() and (candidate / 'predictions').exists():
            return candidate
    raise FileNotFoundError('Could not locate repository root.')


def read_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    return df


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def challenge_key(path: Path) -> str:
    return path.parents[0].name


def round_key(path: Path) -> int:
    return int(path.stem.split('-')[1])


def team_name_from_path(path: Path) -> str:
    return path.parents[1].name


def load_truth(root: Path, challenge_name: str, round_id: int) -> pd.DataFrame:
    return read_csv(root / 'scoring' / challenge_name / 'reference_answers' / f'round-{round_id:02d}.csv')


def load_release_info(root: Path, challenge_name: str, round_id: int) -> dict:
    return read_json(root / 'data-release' / challenge_name / f'round-{round_id:02d}' / 'release_info.json')


def score_round(pred_df: pd.DataFrame, truth_df: pd.DataFrame, forecast_start: int, forecast_end: int) -> dict:
    pred = pred_df[(pred_df['week'] >= forecast_start) & (pred_df['week'] <= forecast_end)].copy()
    truth = truth_df[(truth_df['week'] >= forecast_start) & (truth_df['week'] <= forecast_end)].copy()

    merged = pred.merge(truth, on='week', suffixes=('_pred', '_truth'))
    if merged.empty:
        raise ValueError('No overlapping forecast weeks to score.')

    hosp_rmse = math.sqrt(((merged['hospitalizations_per_100k_pred'] - merged['hospitalizations_per_100k_truth']) ** 2).mean())
    hosp_mean = merged['hospitalizations_per_100k_truth'].mean()
    hosp_nrmse = hosp_rmse / hosp_mean if hosp_mean else hosp_rmse

    r0_err = []
    for pred_v, truth_v in zip(merged['r0_pred'], merged['r0_truth']):
        if truth_v == 0:
            r0_err.append(abs(pred_v - truth_v))
        else:
            r0_err.append(abs(pred_v - truth_v) / abs(truth_v))
    r0_mape = sum(r0_err) / len(r0_err)

    round_score = (hosp_nrmse + r0_mape) / 2.0
    return {
        'hosp_rmse': hosp_rmse,
        'hosp_nrmse': hosp_nrmse,
        'r0_mape': r0_mape,
        'round_score': round_score,
    }


def prediction_files(root: Path):
    yield from sorted((root / 'predictions').glob('Team-*/challenge-*/round-*.csv'))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('.'))
    args = parser.parse_args()

    root = find_repo_root(args.root.resolve())

    by_team_challenge = {}
    for pred_path in prediction_files(root):
        team = team_name_from_path(pred_path)
        challenge = challenge_key(pred_path)
        round_id = round_key(pred_path)
        by_team_challenge.setdefault(team, {}).setdefault(challenge, {})[round_id] = pred_path

    # Per-round and per-challenge results
    challenge_scores = {}
    for challenge in ['challenge-01', 'challenge-02']:
        challenge_dir = root / 'scoring' / challenge
        (challenge_dir / 'round-scores').mkdir(parents=True, exist_ok=True)
        round_tables = []

        for round_id in [1, 2, 3]:
            rows = []
            for team in sorted(by_team_challenge.keys()):
                pred_path = by_team_challenge.get(team, {}).get(challenge, {}).get(round_id)
                if pred_path is None:
                    continue
                pred_df = read_csv(pred_path)
                truth_df = load_truth(root, challenge, round_id)
                release_info = load_release_info(root, challenge, round_id)
                scores = score_round(pred_df, truth_df, int(release_info['forecast_start_week']), int(release_info['forecast_end_week']))
                rows.append({
                    'team_id': team,
                    'challenge_id': challenge,
                    'round_id': f'{round_id:02d}',
                    **scores,
                })
            rows.sort(key=lambda r: (r['round_score'], r['team_id']))
            with (challenge_dir / 'round-scores' / f'round-{round_id:02d}.csv').open('w', newline='', encoding='utf-8') as fh:
                writer = csv.DictWriter(fh, fieldnames=['team_id', 'challenge_id', 'round_id', 'hosp_rmse', 'hosp_nrmse', 'r0_mape', 'round_score'])
                writer.writeheader()
                for row in rows:
                    writer.writerow({k: (f'{v:.6f}' if isinstance(v, float) else v) for k, v in row.items()})
            round_tables.append(pd.DataFrame(rows))

        if round_tables:
            combined = pd.concat(round_tables, ignore_index=True)
            combined['round_score'] = pd.to_numeric(combined['round_score'])
            challenge_scores[challenge] = combined.groupby('team_id', as_index=False)['round_score'].mean().rename(columns={'round_score': 'challenge_score'})
            challenge_scores[challenge] = challenge_scores[challenge].sort_values(['challenge_score', 'team_id'])
            challenge_scores[challenge].insert(0, 'rank', range(1, len(challenge_scores[challenge]) + 1))
            challenge_scores[challenge].to_csv(challenge_dir / 'leaderboard.csv', index=False)

    # Overall leaderboard
    all_rows = None
    for challenge, df in challenge_scores.items():
        d = df[['team_id', 'challenge_score']].rename(columns={'challenge_score': challenge.replace('-', '_')})
        all_rows = d if all_rows is None else all_rows.merge(d, on='team_id', how='outer')

    if all_rows is None:
        raise RuntimeError('No score data generated.')

    all_rows['challenge_01'] = pd.to_numeric(all_rows['challenge_01'])
    all_rows['challenge_02'] = pd.to_numeric(all_rows['challenge_02'])
    all_rows['overall_score'] = all_rows[['challenge_01', 'challenge_02']].mean(axis=1)
    all_rows = all_rows.sort_values(['overall_score', 'team_id']).reset_index(drop=True)
    all_rows.insert(0, 'rank', range(1, len(all_rows) + 1))
    all_rows = all_rows[['rank', 'team_id', 'challenge_01', 'challenge_02', 'overall_score']]
    all_rows.to_csv(root / 'scoring' / 'overall-leaderboard.csv', index=False)
    print('Scoring complete.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
