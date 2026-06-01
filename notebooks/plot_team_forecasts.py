# %%
"""Plot team forecasts against released data and aggregate forecasts.

This script is notebook-friendly and can be run from Jupyter or as a plain Python file.
It expects the repository root to contain `data-release/` and `predictions/`.
"""

from pathlib import Path
import re

import pandas as pd
import matplotlib.pyplot as plt

# %%
NOTEBOOK_DIR = Path.cwd()
if not (NOTEBOOK_DIR / "data-release").exists() and (NOTEBOOK_DIR.parent / "data-release").exists():
    NOTEBOOK_DIR = NOTEBOOK_DIR.parent

DATA_ROOT = NOTEBOOK_DIR
RELEASED_DATA_DIR = DATA_ROOT / "data-release"
TEAM_PREDICTIONS_DIR = DATA_ROOT / "predictions"
OUTPUT_DIR = DATA_ROOT / "notebooks" / "plots"
ROUND_FILE_RE = re.compile(r"^round-(\d+)\.csv$")
LINEWIDTH = 1.0
MARKERSIZE = 3

# %%
def get_round_number(path: Path) -> int:
    match = ROUND_FILE_RE.match(path.name)
    if not match:
        raise ValueError(f"Invalid round filename: {path.name}")
    return int(match.group(1))


def find_last_released_week(release_df: pd.DataFrame) -> int:
    if "week" not in release_df.columns:
        raise KeyError("Released data must contain a 'week' column.")
    return int(release_df["week"].max())


def load_release_data(round_num: int) -> pd.DataFrame:
    path = RELEASED_DATA_DIR / f"round-{round_num}" / "release.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing released data file: {path}")
    df = pd.read_csv(path)
    required = ["week", "hospitalizations_per_100k"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"{path} missing required columns: {missing}")
    return df.sort_values("week")


def load_team_rounds(team_dir: Path):
    round_files = sorted(team_dir.glob("round-*.csv"), key=lambda p: get_round_number(p))
    if not round_files:
        raise FileNotFoundError(f"No round CSV files found in {team_dir}")
    loaded = []
    for path in round_files:
        round_num = get_round_number(path)
        df = pd.read_csv(path)
        required = ["week", "hospitalizations_per_100k", "r0"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise KeyError(f"{path} missing required columns: {missing}")
        df = df.sort_values("week")
        loaded.append((round_num, path, df))
    return loaded


def draw_latest_prediction(ax, team_name: str, team_rounds):
    latest_round_num, _, latest_df = max(team_rounds, key=lambda item: item[0])
    release_df = load_release_data(latest_round_num)
    last_released_week = find_last_released_week(release_df)
    ax.plot(release_df["week"], release_df["hospitalizations_per_100k"], linewidth=LINEWIDTH, marker="o", markersize=MARKERSIZE, label="Released data")
    ax.axvline(last_released_week, linestyle=":", linewidth=LINEWIDTH, alpha=0.7, label="Forecast start")
    ax.plot(latest_df["week"], latest_df["hospitalizations_per_100k"], linestyle="--", marker="o", markersize=MARKERSIZE, linewidth=LINEWIDTH, label=f"Latest forecast (Round {latest_round_num})")
    ax.set_title(f"{team_name} - Latest")
    ax.set_xlabel("Week")
    ax.set_ylabel("Hosp / 100k")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=6)


def draw_all_predictions(ax, team_name: str, team_rounds):
    latest_round_num = max(r for r, _, _ in team_rounds)
    release_df = load_release_data(latest_round_num)
    last_released_week = find_last_released_week(release_df)
    ax.plot(release_df["week"], release_df["hospitalizations_per_100k"], linewidth=LINEWIDTH, marker="o", markersize=MARKERSIZE, label="Released data")
    ax.axvline(last_released_week, linestyle=":", linewidth=LINEWIDTH, alpha=0.7, label="Forecast start")
    for round_num, _, df in team_rounds:
        ax.plot(df["week"], df["hospitalizations_per_100k"], linestyle="--", marker="o", markersize=MARKERSIZE, linewidth=LINEWIDTH, label=f"Round {round_num}")
    ax.set_title(f"{team_name} - All forecasts")
    ax.set_xlabel("Week")
    ax.set_ylabel("Hosp / 100k")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=6)


def draw_r0(ax, team_name: str, team_rounds):
    has_r0 = any("r0" in df.columns for _, _, df in team_rounds)
    if not has_r0:
        ax.set_title(f"{team_name} - R0")
        ax.text(0.5, 0.5, "No R0 column found", ha="center", va="center", transform=ax.transAxes)
        ax.axis("off")
        return
    latest_round_num = max(r for r, _, _ in team_rounds)
    release_df = load_release_data(latest_round_num)
    last_released_week = find_last_released_week(release_df)
    ax.axvline(last_released_week, linestyle=":", linewidth=LINEWIDTH, alpha=0.7, label="Forecast start")
    plotted_any = False
    for round_num, _, df in team_rounds:
        if "r0" not in df.columns:
            continue
        ax.plot(df["week"], df["r0"], linestyle="--", marker="o", markersize=MARKERSIZE, linewidth=LINEWIDTH, label=f"Round {round_num}")
        plotted_any = True
    if not plotted_any:
        ax.set_title(f"{team_name} - R0")
        ax.text(0.5, 0.5, "No R0 data found", ha="center", va="center", transform=ax.transAxes)
        ax.axis("off")
        return
    ax.set_title(f"{team_name} - R0")
    ax.set_xlabel("Week")
    ax.set_ylabel("R0")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=6)


def plot_team(team_name: str, team_rounds):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(15, 3))
    draw_latest_prediction(axes[0], team_name, team_rounds)
    draw_all_predictions(axes[1], team_name, team_rounds)
    draw_r0(axes[2], team_name, team_rounds)
    fig.tight_layout()
    output_path = OUTPUT_DIR / f"{team_name}_combined.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.show()
    plt.close(fig)
    print(f"Saved: {output_path}")


def plot_aggregate_current_release(team_dirs):
    all_team_data = {}
    for team_dir in team_dirs:
        team_name = team_dir.name
        team_rounds = load_team_rounds(team_dir)
        latest_round_num = max(r for r, _, _ in team_rounds)
        latest_round_df = next(df for r, _, df in team_rounds if r == latest_round_num)
        all_team_data[team_name] = (latest_round_num, latest_round_df)
    current_round = max(round_num for round_num, _ in all_team_data.values())
    release_df = load_release_data(current_round)
    last_released_week = find_last_released_week(release_df)
    current_team_frames = []
    for team_name, (round_num, df) in all_team_data.items():
        if round_num != current_round:
            continue
        current_team_frames.append(df[["week", "hospitalizations_per_100k"]].rename(columns={"hospitalizations_per_100k": team_name}))
    if not current_team_frames:
        raise RuntimeError("No team data available for the current release round.")
    merged = current_team_frames[0]
    for frame in current_team_frames[1:]:
        merged = merged.merge(frame, on="week", how="inner")
    merged = merged.sort_values("week")
    team_value_cols = [c for c in merged.columns if c != "week"]
    mean_series = merged[team_value_cols].mean(axis=1)
    std_series = merged[team_value_cols].std(axis=1, ddof=1)
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(release_df["week"], release_df["hospitalizations_per_100k"], linewidth=LINEWIDTH + 0.3, marker="o", markersize=MARKERSIZE, label="Released data")
    ax.axvline(last_released_week, linestyle=":", linewidth=LINEWIDTH, alpha=0.7, label="Forecast start")
    ax.errorbar(merged["week"], mean_series, yerr=std_series.fillna(0), fmt="o-", linewidth=LINEWIDTH, markersize=MARKERSIZE, capsize=2, label=f"Team mean (n={len(team_value_cols)})")
    ax.set_title(f"Aggregate forecast - Round {current_round}")
    ax.set_xlabel("Week")
    ax.set_ylabel("Hosp / 100k")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"aggregate_round-{current_round}.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.show()
    plt.close(fig)
    print(f"Saved: {output_path}")

# %%
if not TEAM_PREDICTIONS_DIR.exists():
    raise FileNotFoundError(f"Team prediction directory not found: {TEAM_PREDICTIONS_DIR}")

team_dirs = sorted([p for p in TEAM_PREDICTIONS_DIR.iterdir() if p.is_dir() and p.name != "template"])
if not team_dirs:
    raise FileNotFoundError(f"No team folders found in {TEAM_PREDICTIONS_DIR}")

for team_dir in team_dirs:
    team_name = team_dir.name
    team_rounds = load_team_rounds(team_dir)
    plot_team(team_name, team_rounds)

plot_aggregate_current_release(team_dirs)
print("Finished plotting all teams.")
