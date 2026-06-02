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
    """
    Return the release folder and JSON metadata for the release that closes/opens
    the requested round. If a round is being scored by the next release, this
    script uses the release whose `scores_round_id` matches the round number.
    """
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

    raise FileNotFoundError(
        f"No release found in {challenge_dir} that scores round {round_num}"
    )


def load_public_data(release_dir: Path) -> list[dict[str, str]]:
    public_path = release_dir / "public.csv"
    if not public_path.exists():
        raise FileNotFoundError(f"Missing public data file: {public_path}")
    return read_csv(public_path)


def plot_team_challenge(team_dir: Path, challenge_dir: Path) -> None:
    """
    Plot all rounds for one team within one challenge, overlayed with the public
    release data from the latest release that scores a round for that challenge.
    """
    round_files = sorted(
        [p for p in challenge_dir.glob("round-*.csv") if ROUND_RE.match(p.name)],
        key=lambda p: int(p.stem.split("-")[1]),
    )

    if not round_files:
        return

    # Use the latest scored release for this challenge to get the public curve.
    latest_round_num = max(int(p.stem.split("-")[1]) for p in round_files)
    release_dir, release_info = find_release_for_round(challenge_dir.parent.parent / challenge_dir.name, latest_round_num)  # challenge_dir is predictions/Team-XX/challenge-YY
    public_rows = load_public_data(release_dir)

    public_weeks = [int(r["week"]) for r in public_rows]
    public_hosp = [float(r["hospitalizations_per_100k"]) for r in public_rows]

    fig, ax = plt.subplots(figsize=(7, 3))

    # Released/public data
    ax.plot(
        public_weeks,
        public_hosp,
        linewidth=1.2,
        marker="o",
        markersize=3,
        label=f"Released data ({release_dir.name})",
    )

    # Team prediction rounds
    for pred_file in round_files:
        rows = read_csv(pred_file)
        weeks = [int(r["week"]) for r in rows]
        hosp = [float(r["hospitalizations_per_100k"]) for r in rows]
        round_label = pred_file.stem
        ax.plot(
            weeks,
            hosp,
            linewidth=1.0,
            markersize=2,
            marker="o",
            linestyle="--",
            label=round_label,
        )

    # Forecast boundary line, if available
    forecast_end_week = release_info.get("forecast_end_week")
    released_through_week = release_info.get("released_through_week")
    if released_through_week is not None:
        ax.axvline(
            int(released_through_week),
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

    PLOTS_ROOT.mkdir(parents=True, exist_ok=True)
    out_dir = PLOTS_ROOT / challenge_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_dir / f"{team_dir.name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    if not PREDICTIONS_ROOT.exists():
        raise FileNotFoundError(f"Missing predictions folder: {PREDICTIONS_ROOT}")

    for team_dir in sorted([p for p in PREDICTIONS_ROOT.iterdir() if p.is_dir()]):
        if not TEAM_RE.match(team_dir.name):
            continue

        for challenge_dir in sorted([p for p in team_dir.iterdir() if p.is_dir()]):
            if not CHALLENGE_RE.match(challenge_dir.name):
                continue

            plot_team_challenge(team_dir, challenge_dir)


if __name__ == "__main__":
    main()
