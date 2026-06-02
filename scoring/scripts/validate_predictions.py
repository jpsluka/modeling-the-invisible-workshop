from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

TEAM_RE = re.compile(r"^Team-\d{2}$")
ROUND_RE = re.compile(r"^round-(\d{2})\.csv$")


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    errors = []

    for team_dir in sorted((root / "predictions").glob("Team-*")):
        if not team_dir.is_dir() or not TEAM_RE.match(team_dir.name):
            errors.append(f"Invalid team folder: {team_dir.name}")
            continue
        for challenge_dir in sorted(team_dir.glob("challenge-*")):
            if not challenge_dir.is_dir():
                continue
            for pred_file in sorted(challenge_dir.glob("round-*.csv")):
                m = ROUND_RE.match(pred_file.name)
                if not m:
                    errors.append(f"Invalid prediction filename: {pred_file}")
                    continue
                round_id = int(m.group(1))
                release_dir = root / "data-release" / challenge_dir.name / f"release-{round_id:02d}"
                info_path = release_dir / "release_info.json"
                if not info_path.exists():
                    errors.append(f"Missing release info for {pred_file}: {info_path}")
                    continue
                info = json.loads(info_path.read_text(encoding="utf-8"))
                if "forecast_end_week" not in info:
                    # final release does not open a new round
                    continue
                forecast_end = int(info["forecast_end_week"])
                rows = read_csv(pred_file)
                if not rows:
                    errors.append(f"Empty prediction file: {pred_file}")
                    continue
                try:
                    weeks = [int(r["week"]) for r in rows]
                    hosp = [float(r["hospitalizations_per_100k"]) for r in rows]
                    r0 = [float(r["r0"]) for r in rows]
                except Exception:
                    errors.append(f"Non-numeric data in {pred_file}")
                    continue
                if weeks != list(range(1, forecast_end + 1)):
                    errors.append(f"{pred_file} must contain weeks 1..{forecast_end} in order")
                if any(x != x for x in hosp + r0):
                    errors.append(f"NaN values found in {pred_file}")
    if errors:
        print("Prediction validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Prediction validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
