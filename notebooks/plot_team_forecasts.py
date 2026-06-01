# %%
from __future__ import annotations

import json
import math
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# %%
def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / 'data-release').exists() and (candidate / 'predictions').exists():
            return candidate
    raise FileNotFoundError('Could not find repo root.')


BASE_DIR = find_repo_root(Path.cwd())
DATA_RELEASE_DIR = BASE_DIR / 'data-release'
PREDICTIONS_DIR = BASE_DIR / 'predictions'
PLOTS_DIR = BASE_DIR / 'notebooks' / 'plots'
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

ROUND_RE = re.compile(r'^round-(\d{2})\.csv$')

# %%
def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    return df


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def last_released_week(challenge: str, round_id: int) -> int:
    info = load_json(DATA_RELEASE_DIR / challenge / f'round-{round_id:02d}' / 'release_info.json')
    return int(info['released_through_week'])


def round_id_from_path(path: Path) -> int:
    return int(path.stem.split('-')[1])


# %%
def plot_team_challenge(team_dir: Path, challenge: str) -> None:
    round_files = sorted((team_dir / challenge).glob('round-*.csv'), key=round_id_from_path)
    if not round_files:
        return

    latest_round = round_id_from_path(round_files[-1])
    released = load_csv(DATA_RELEASE_DIR / challenge / f'round-{latest_round:02d}' / 'released.csv')
    cutoff = last_released_week(challenge, latest_round)

    latest = load_csv(round_files[-1])

    fig, axes = plt.subplots(1, 3, figsize=(15, 3))

    # Latest only
    axes[0].plot(released['week'], released['hospitalizations_per_100k'], marker='o', markersize=3, linewidth=1, label='Released data')
    axes[0].axvline(cutoff, linestyle=':', linewidth=1)
    axes[0].plot(latest['week'], latest['hospitalizations_per_100k'], marker='o', markersize=3, linewidth=1, linestyle='--', label=f'Latest (R{latest_round:02d})')
    axes[0].set_title(f'{team_dir.name} {challenge} latest')
    axes[0].set_xlabel('Week')
    axes[0].set_ylabel('Hosp / 100k')
    axes[0].grid(alpha=0.3)
    axes[0].legend(fontsize=6)

    # All forecasts
    axes[1].plot(released['week'], released['hospitalizations_per_100k'], marker='o', markersize=3, linewidth=1, label='Released data')
    axes[1].axvline(cutoff, linestyle=':', linewidth=1)
    for rf in round_files:
        df = load_csv(rf)
        rid = round_id_from_path(rf)
        axes[1].plot(df['week'], df['hospitalizations_per_100k'], marker='o', markersize=3, linewidth=1, linestyle='--', label=f'R{rid:02d}')
    axes[1].set_title(f'{team_dir.name} {challenge} all rounds')
    axes[1].set_xlabel('Week')
    axes[1].set_ylabel('Hosp / 100k')
    axes[1].grid(alpha=0.3)
    axes[1].legend(fontsize=6)

    # R0 panel
    if 'r0' in latest.columns:
        axes[2].axvline(cutoff, linestyle=':', linewidth=1)
        for rf in round_files:
            df = load_csv(rf)
            if 'r0' not in df.columns:
                continue
            rid = round_id_from_path(rf)
            axes[2].plot(df['week'], df['r0'], marker='o', markersize=3, linewidth=1, linestyle='--', label=f'R{rid:02d}')
        axes[2].set_title(f'{team_dir.name} {challenge} R0')
        axes[2].set_xlabel('Week')
        axes[2].set_ylabel('R0')
        axes[2].grid(alpha=0.3)
        axes[2].legend(fontsize=6)
    else:
        axes[2].axis('off')
        axes[2].set_title(f'{team_dir.name} {challenge} R0 missing')

    fig.tight_layout()
    out = PLOTS_DIR / f'{team_dir.name}_{challenge}.png'
    fig.savefig(out, dpi=200, bbox_inches='tight')
    plt.show()
    plt.close(fig)


# %%
def plot_aggregate_for_current_release(challenge: str) -> None:
    team_dirs = sorted([d for d in PREDICTIONS_DIR.glob('Team-*') if d.is_dir()])
    round_ids = []
    for team_dir in team_dirs:
        rf = sorted((team_dir / challenge).glob('round-*.csv'), key=round_id_from_path)
        if rf:
            round_ids.append(round_id_from_path(rf[-1]))
    if not round_ids:
        return
    current_round = max(round_ids)
    released = load_csv(DATA_RELEASE_DIR / challenge / f'round-{current_round:02d}' / 'released.csv')
    cutoff = last_released_week(challenge, current_round)

    merged = None
    for team_dir in team_dirs:
        rf = team_dir / challenge / f'round-{current_round:02d}.csv'
        if not rf.exists():
            continue
        df = load_csv(rf)[['week', 'hospitalizations_per_100k']].rename(columns={'hospitalizations_per_100k': team_dir.name})
        merged = df if merged is None else merged.merge(df, on='week', how='inner')
    if merged is None:
        return
    merged = merged.sort_values('week')
    team_cols = [c for c in merged.columns if c != 'week']
    mean = merged[team_cols].mean(axis=1)
    std = merged[team_cols].std(axis=1, ddof=1).fillna(0)

    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(released['week'], released['hospitalizations_per_100k'], marker='o', markersize=3, linewidth=1, label='Released data')
    ax.axvline(cutoff, linestyle=':', linewidth=1)
    ax.errorbar(merged['week'], mean, yerr=std, fmt='o-', markersize=3, linewidth=1, capsize=2, label=f'Mean prediction (n={len(team_cols)})')
    ax.set_title(f'Aggregate {challenge} round {current_round:02d}')
    ax.set_xlabel('Week')
    ax.set_ylabel('Hosp / 100k')
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)
    out = PLOTS_DIR / f'aggregate_{challenge}_round-{current_round:02d}.png'
    fig.tight_layout()
    fig.savefig(out, dpi=200, bbox_inches='tight')
    plt.show()
    plt.close(fig)


# %%
for team_dir in sorted([d for d in PREDICTIONS_DIR.glob('Team-*') if d.is_dir()]):
    for challenge in ['challenge-01', 'challenge-02']:
        if (team_dir / challenge).exists():
            plot_team_challenge(team_dir, challenge)

for challenge in ['challenge-01', 'challenge-02']:
    plot_aggregate_for_current_release(challenge)

print('Plotting complete.')
