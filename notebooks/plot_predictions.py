from __future__ import annotations

from pathlib import Path
import csv

import matplotlib.pyplot as plt

ROOT = Path.cwd()
TEAM_ROOT = ROOT / 'predictions'
OUT = ROOT / 'plots'


def read_csv(path: Path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for team_dir in sorted([p for p in TEAM_ROOT.iterdir() if p.is_dir()]):
        fig, ax = plt.subplots(figsize=(7, 3))
        for challenge_dir in sorted([p for p in team_dir.iterdir() if p.is_dir()]):
            for pred_file in sorted(challenge_dir.glob('round-*.csv')):
                rows = read_csv(pred_file)
                weeks = [int(r['week']) for r in rows]
                hosp = [float(r['hospitalizations_per_100k']) for r in rows]
                ax.plot(weeks, hosp, linewidth=1.0, markersize=2, marker='o', label=f'{challenge_dir.name} {pred_file.stem}')
        ax.set_title(team_dir.name)
        ax.set_xlabel('Week')
        ax.set_ylabel('Hosp / 100k')
        ax.legend(fontsize=6)
        fig.tight_layout()
        fig.savefig(OUT / f'{team_dir.name}.png', dpi=150)
        plt.close(fig)


if __name__ == '__main__':
    main()
