from __future__ import annotations

from pathlib import Path
import csv
import json
import re

import matplotlib.pyplot as plt


ROOT = Path.cwd()
DATA_RELEASE_ROOT = ROOT / "data-release"
PREDICTIONS_ROOT = ROOT / "predictions"
PLOTS_ROOT = ROOT / "scoring" / "plots"

TEAM_RE = re.compile(r"^Team-\d{2}$")
CHALLENGE_RE = re.compile(r"^challenge-\d{2}$")
RELEASE_RE = re.compile(r"^release-\d{2}$")
ROUND_RE = re.compile(r"^round-\d{2}\.csv$")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def find_release_for_round(challenge_dir: Path, round_num: int) -> tuple[Path, dict]:
    for release_dir in sorted(challenge_dir.iterdir()):
        if not release_dir.is_dir() or not RELEASE_RE.match(release_dir.name):
            continue
        info_path = release_dir / "release_info.json"
        if not info_path.exists():
            continue
        try:
            info = json.loads(info_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if info.get("scores_round_id") == round_num:
            return release_dir, info
    raise FileNotFoundError(f"No release found in {challenge_dir} that scores round {round_num}")


def load_public_data(release_dir: Path) -> list[dict[str, str]]:
    public_path = release_dir / "public.csv"
    if not public_path.exists():
        raise FileNotFoundError(f"Missing public data file: {public_path}")
    return read_csv(public_path)


def latest_round_file(challenge_dir: Path) -> Path | None:
    round_files = sorted(
        [p for p in challenge_dir.glob("round-*.csv") if ROUND_RE.match(p.name)],
        key=lambda p: int(p.stem.split("-")[1]),
    )
    return round_files[-1] if round_files else None


def plot_team_challenge(team_dir: Path, challenge_dir: Path) -> None:
    round_files = sorted(
        [p for p in challenge_dir.glob("round-*.csv") if ROUND_RE.match(p.name)],
        key=lambda p: int(p.stem.split("-")[1]),
    )
    if not round_files:
        return

    latest_round_num = max(int(p.stem.split("-")[1]) for p in round_files)
    challenge_release_dir = DATA_RELEASE_ROOT / challenge_dir.name
    release_dir, release_info = find_release_for_round(challenge_release_dir, latest_round_num)
    public_rows = load_public_data(release_dir)

    public_weeks = [int(r["week"]) for r in public_rows]
    public_hosp = [float(r["hospitalizations_per_100k"]) for r in public_rows]

    fig, ax = plt.subplots(figsize=(7, 3))

    ax.plot(
        public_weeks,
        public_hosp,
        linewidth=1.2,
        marker="o",
        markersize=3,
        label=f"Released data ({release_dir.name})",
    )

    for pred_file in round_files:
        rows = read_csv(pred_file)
        weeks = [int(r["week"]) for r in rows]
        hosp = [float(r["hospitalizations_per_100k"]) for r in rows]
        ax.plot(
            weeks,
            hosp,
            linewidth=1.0,
            markersize=2,
            marker="o",
            linestyle="--",
            label=pred_file.stem,
        )

    forecast_start_week = release_info.get("forecast_start_week")
    if forecast_start_week is not None:
        ax.axvline(
            int(forecast_start_week),
            linestyle=":",
            linewidth=1.0,
            alpha=0.7,
            label="Forecast start",
        )

    ax.set_title(f"{team_dir.name} - {challenge_dir.name}")
    ax.set_xlabel("Week")
    ax.set_ylabel("Hosp / 100k")
    ax.legend(fontsize=6)
    ax.grid(True, alpha=0.3)

    out_dir = PLOTS_ROOT / challenge_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_dir / f"{team_dir.name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_all_teams_for_challenge(challenge_name: str) -> None:
    challenge_release_dir = DATA_RELEASE_ROOT / challenge_name
    release_dirs = sorted(
        [p for p in challenge_release_dir.iterdir() if p.is_dir() and RELEASE_RE.match(p.name)],
        key=lambda p: int(p.name.split("-")[1]),
    )
    if not release_dirs:
        raise FileNotFoundError(f"No releases found for {challenge_name}")

    latest_release_dir = release_dirs[-1]
    public_rows = load_public_data(latest_release_dir)
    public_weeks = [int(r["week"]) for r in public_rows]
    public_hosp = [float(r["hospitalizations_per_100k"]) for r in public_rows]

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(
        public_weeks,
        public_hosp,
        linewidth=1.4,
        label=f"Released data ({latest_release_dir.name})",
    )

    for team_dir in sorted([p for p in PREDICTIONS_ROOT.iterdir() if p.is_dir() and TEAM_RE.match(p.name)]):
        challenge_dir = team_dir / challenge_name
        if not challenge_dir.exists():
            continue

        pred_file = latest_round_file(challenge_dir)
        if pred_file is None:
            continue

        rows = read_csv(pred_file)
        weeks = [int(r["week"]) for r in rows]
        hosp = [float(r["hospitalizations_per_100k"]) for r in rows]

        ax.plot(
            weeks,
            hosp,
            linewidth=1.0,
            label=f"{team_dir.name} ({pred_file.stem})",
        )

    ax.set_title(f"All teams - {challenge_name}")
    ax.set_xlabel("Week")
    ax.set_ylabel("Hosp / 100k")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=6)

    out_dir = PLOTS_ROOT / challenge_name
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_dir / "all-teams.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    if not PREDICTIONS_ROOT.exists():
        raise FileNotFoundError(f"Missing predictions folder: {PREDICTIONS_ROOT}")

    challenge_names = sorted(
        {
            p.name
            for team_dir in PREDICTIONS_ROOT.iterdir()
            if team_dir.is_dir() and TEAM_RE.match(team_dir.name)
            for p in team_dir.iterdir()
            if p.is_dir() and CHALLENGE_RE.match(p.name)
        }
    )

    for team_dir in sorted([p for p in PREDICTIONS_ROOT.iterdir() if p.is_dir()]):
        if not TEAM_RE.match(team_dir.name):
            continue

        for challenge_dir in sorted([p for p in team_dir.iterdir() if p.is_dir()]):
            if not CHALLENGE_RE.match(challenge_dir.name):
                continue

            plot_team_challenge(team_dir, challenge_dir)

    for challenge_name in challenge_names:
        plot_all_teams_for_challenge(challenge_name)


if __name__ == "__main__":
    main()
