from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

# Weighted round score:
#   80% hospitalization forecast accuracy
#   20% R0 forecast accuracy
HOSP_WEIGHT = 0.8
R0_WEIGHT = 0.2

def write_csv(path: Path, header: list[str], rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        w.writerows(rows)


def rmse(xs, ys):
    if not xs:
        return float("nan")
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(xs, ys)) / len(xs))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()

    pred_root = root / "predictions"
    release_root = root / "data-release"
    scoring_root = root / "scoring"

    challenge_round_scores = defaultdict(lambda: defaultdict(list))
    team_challenge_scores = defaultdict(lambda: defaultdict(list))

    for challenge_dir in sorted(release_root.glob("challenge-*")):
        if not challenge_dir.is_dir():
            continue
        for release_dir in sorted(challenge_dir.glob("release-*")):
            info_path = release_dir / "release_info.json"
            truth_path = release_dir / "truth_previous_round.csv"
            if not info_path.exists() or not truth_path.exists():
                continue
            info = json.loads(info_path.read_text(encoding="utf-8"))
            round_id = info.get("scores_round_id")
            if round_id is None:
                continue
            start = int(info["scores_round_start_week"])
            end = int(info["scores_round_end_week"])
            target_weeks = list(range(start, end + 1))
            truth_rows = read_csv(truth_path)
            truth_map = {int(r["week"]): r for r in truth_rows}
            hosp_truth = [float(truth_map[w]["hospitalizations_per_100k"]) for w in target_weeks]
            r0_truth = [float(truth_map[w]["r0"]) for w in target_weeks]

            round_rows = []
            for team_dir in sorted(pred_root.glob("Team-*")):
                pred_file = team_dir / challenge_dir.name / f"round-{round_id:02d}.csv"
                if not pred_file.exists():
                    continue
                pred_rows = read_csv(pred_file)
                pred_map = {int(r["week"]): r for r in pred_rows}
                pred_h = [float(pred_map[w]["hospitalizations_per_100k"]) for w in target_weeks]
                pred_r0 = [float(pred_map[w]["r0"]) for w in target_weeks]
                hosp_rmse = rmse(pred_h, hosp_truth)
                r0_rmse = rmse(pred_r0, r0_truth)
                scale = sum(hosp_truth) / len(hosp_truth)
                hosp_nrmse = hosp_rmse / scale if scale else hosp_rmse
                #round_score = (hosp_nrmse + r0_rmse) / 2.0
                round_score = (HOSP_WEIGHT * hosp_nrmse) + (R0_WEIGHT * r0_rmse)
                
                row = {
                    "team_id": team_dir.name,
                    "round_id": round_id,
                    "hosp_rmse": round(hosp_rmse, 6),
                    "hosp_nrmse": round(hosp_nrmse, 6),
                    "r0_rmse": round(r0_rmse, 6),
                    "round_score": round(round_score, 6),
                }
                round_rows.append(row)
                team_challenge_scores[team_dir.name][challenge_dir.name].append(round_score)
                challenge_round_scores[challenge_dir.name][round_id].append(row)

            round_rows.sort(key=lambda r: (r["round_score"], r["team_id"]))
            write_csv(
                scoring_root / challenge_dir.name / "round-scores" / f"round-{round_id:02d}.csv",
                ["team_id", "round_id", "hosp_rmse", "hosp_nrmse", "r0_rmse", "round_score"],
                round_rows,
            )

    for challenge_name in sorted(challenge_round_scores.keys()):
        rows = []
        for team_id, per_challenge in team_challenge_scores.items():
            if challenge_name not in per_challenge:
                continue
            vals = per_challenge[challenge_name]
            rows.append({
                "team_id": team_id,
                "challenge_id": challenge_name,
                "challenge_score": round(sum(vals) / len(vals), 6),
                "rounds_scored": len(vals),
            })
        rows.sort(key=lambda r: (r["challenge_score"], r["team_id"]))
        write_csv(scoring_root / challenge_name / "leaderboard.csv", ["team_id", "challenge_id", "challenge_score", "rounds_scored"], rows)

    overall_rows = []
    for team_id, per_challenge in team_challenge_scores.items():
        vals = [sum(v) / len(v) for v in per_challenge.values() if v]
        if not vals:
            continue
        overall_rows.append({
            "team_id": team_id,
            "overall_score": round(sum(vals) / len(vals), 6),
            "challenges_scored": len(vals),
        })
    overall_rows.sort(key=lambda r: (r["overall_score"], r["team_id"]))
    write_csv(scoring_root / "overall-leaderboard.csv", ["team_id", "overall_score", "challenges_scored"], overall_rows)

    print("Scoring complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
