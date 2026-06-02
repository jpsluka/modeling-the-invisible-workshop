from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    errors = []

    for challenge_dir in sorted((root / "data-release").glob("challenge-*")):
        if not challenge_dir.is_dir():
            continue
        for release_dir in sorted(challenge_dir.glob("release-*")):
            info_path = release_dir / "release_info.json"
            if not info_path.exists():
                errors.append(f"Missing {info_path}")
                continue
            info = json.loads(info_path.read_text(encoding="utf-8"))
            public_path = release_dir / "public.csv"
            if public_path.exists() and "released_through_week" in info:
                rows = read_csv(public_path)
                weeks = [int(r["week"]) for r in rows]
                exp = int(info["released_through_week"])
                if weeks != list(range(1, exp + 1)):
                    errors.append(f"{public_path} weeks must be 1..{exp}")
            truth_path = release_dir / "truth_previous_round.csv"
            if info.get("scores_round_id") is not None:
                if not truth_path.exists():
                    errors.append(f"Missing {truth_path}")
                else:
                    rows = read_csv(truth_path)
                    weeks = [int(r["week"]) for r in rows]
                    start = int(info["scores_round_start_week"])
                    end = int(info["scores_round_end_week"])
                    if weeks != list(range(start, end + 1)):
                        errors.append(f"{truth_path} weeks must be {start}..{end}")
    if errors:
        print("Release validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Release validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
