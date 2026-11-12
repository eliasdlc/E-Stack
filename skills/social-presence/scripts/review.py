#!/usr/bin/env python3
"""Compare a week of posting with the goals, so the plan changes on numbers, not on feel.

Three CSV files in the data folder, filled from what Elias pastes or exports:

    ledger.csv     one row per thing he published: date, platform, kind, campaign, url,
                   first_line, impressions, likes, replies, reposts, profile_visits, follows, link_clicks, lang
                   (lang is en or es, so the language split can be measured)
    followers.csv  one snapshot per platform per review: date, platform, followers
    leads.csv      one row per inbound lead, no names: date, channel, kind, status

Goals live in profile.json under `goals`: a baseline and checkpoints by date,
each with followers per platform, weekly impressions and leads. Pace is the
straight line from the baseline to the next checkpoint.

    review.py --init                 # create the three files with their headers
    review.py --week 2026-11-02      # the seven days starting that Monday
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

DATA = Path.home() / "Documents/Personal/dev/social-presence"
HEADERS = {
    "ledger.csv": ["date", "platform", "kind", "campaign", "url", "first_line", "impressions", "likes",
                   "replies", "reposts", "profile_visits", "follows", "link_clicks", "lang"],
    "followers.csv": ["date", "platform", "followers"],
    "leads.csv": ["date", "channel", "kind", "status"],
}
NUMBERS = ("impressions", "likes", "replies", "reposts", "profile_visits", "follows", "link_clicks")


def read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(value: str) -> int:
    try:
        return int(float((value or "0").replace(",", "")))
    except ValueError:
        return 0


def in_week(row: dict, start: dt.date) -> bool:
    day = dt.date.fromisoformat(row["date"][:10])
    return start <= day < start + dt.timedelta(days=7)


def pace(goals: dict, metric: str, day: dt.date) -> float | None:
    """Where the metric should be on `day`, on the line from the baseline to the next checkpoint."""
    base = goals.get("baseline", {})
    points = sorted((dt.date.fromisoformat(k), v) for k, v in goals.get("checkpoints", {}).items())
    start_day, start_value = dt.date.fromisoformat(base["date"]), base.get(metric)
    for target_day, target in points:
        if metric not in target or start_value is None:
            continue
        if day <= target_day:
            span = (target_day - start_day).days or 1
            return start_value + (target[metric] - start_value) * (day - start_day).days / span
        start_day, start_value = target_day, target[metric]
    return None


def review(data: Path, start: dt.date) -> str:
    profile = json.loads((data / "profile.json").read_text())
    goals = profile.get("goals", {})
    ledger = [r for r in read(data / "ledger.csv") if in_week(r, start)]
    followers = read(data / "followers.csv")
    leads = [r for r in read(data / "leads.csv") if in_week(r, start)]
    end = start + dt.timedelta(days=6)
    lines = [f"# Week of {start} to {end}", ""]

    lines.append("## Followers against pace")
    latest: dict[str, tuple[str, int]] = {}
    for row in followers:
        if dt.date.fromisoformat(row["date"][:10]) <= end:
            latest[row["platform"]] = max(latest.get(row["platform"], ("", 0)), (row["date"], number(row["followers"])))
    if not latest:
        lines.append("No follower snapshot yet: add one row per platform to followers.csv.")
    for platform, (day, count) in sorted(latest.items()):
        target = pace(goals, f"{platform}_followers", dt.date.fromisoformat(day[:10]))
        verdict = "no goal" if target is None else ("on pace" if count >= target else f"behind by {target - count:.0f}")
        lines.append(f"- {platform}: {count} on {day[:10]}, pace {target:.0f}, {verdict}" if target is not None
                     else f"- {platform}: {count} on {day[:10]}, {verdict}")

    lines += ["", "## What was published"]
    if not ledger:
        lines.append("Nothing logged this week: paste the week's posts and their numbers into ledger.csv.")
    totals = {k: sum(number(r[k]) for r in ledger) for k in NUMBERS}
    by_kind: dict[str, list[dict]] = defaultdict(list)
    for row in ledger:
        by_kind[f"{row['platform']} {row['kind']}"].append(row)
    for kind, rows in sorted(by_kind.items()):
        imp = [number(r["impressions"]) for r in rows]
        fol = sum(number(r["follows"]) for r in rows)
        lines.append(f"- {kind}: {len(rows)} posts, median {statistics.median(imp):.0f} impressions, {fol} follows")
    if ledger:
        weekly_goal = pace(goals, "weekly_impressions", end)
        goal_text = f" (pace {weekly_goal:.0f})" if weekly_goal is not None else ""
        lines.append(f"- total: {len(ledger)} posts, {totals['impressions']} impressions{goal_text}, "
                     f"{totals['follows']} follows, {totals['profile_visits']} profile visits, {totals['link_clicks']} link clicks")

    lines += ["", "## By language"]
    by_lang: dict[str, list[dict]] = defaultdict(list)
    for row in ledger:
        by_lang[f"{row['platform']} {row.get('lang') or 'unset'}"].append(row)
    for key, rows in sorted(by_lang.items()):
        imp = [number(r["impressions"]) for r in rows]
        visits = sum(number(r["profile_visits"]) for r in rows) / len(rows)
        follows = sum(number(r["follows"]) for r in rows) / len(rows)
        lines.append(f"- {key}: {len(rows)} posts, median {statistics.median(imp):.0f} impressions, "
                     f"{visits:.1f} profile visits and {follows:.1f} follows per post")

    lines += ["", "## Best and worst by engagement rate"]
    def rate(r: dict) -> float:
        imp = number(r["impressions"])
        return (number(r["likes"]) + number(r["replies"]) * 2 + number(r["reposts"]) * 2 + number(r["follows"]) * 5) / imp if imp else 0
    ranked = sorted((r for r in ledger if number(r["impressions"])), key=rate, reverse=True)
    for label, rows in (("best", ranked[:3]), ("worst", ranked[-2:] if len(ranked) > 3 else [])):
        for r in rows:
            lines.append(f"- {label}: {r['platform']} {r['kind']} {rate(r):.1%} \"{r['first_line'][:70]}\" {r['url']}")

    lines += ["", "## Leads"]
    lead_goal = pace(goals, "leads", end)
    lines.append(f"- {len(leads)} this week" + (f", pace {lead_goal:.1f} cumulative" if lead_goal is not None else ""))
    for kind, count in sorted(Counter(lead["kind"] for lead in leads).items()):
        lines.append(f"  - {kind}: {count}")

    lines += ["", "## Campaign split"]
    by_campaign: dict[str, list[dict]] = defaultdict(list)
    for row in ledger:
        by_campaign[row["campaign"] or "none"].append(row)
    for campaign, rows in sorted(by_campaign.items()):
        lines.append(f"- {campaign}: {len(rows)} posts, {sum(number(r['impressions']) for r in rows)} impressions, "
                     f"{sum(number(r['follows']) for r in rows)} follows")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--week", help="ISO date of the first day of the week")
    args = parser.parse_args()
    if args.init:
        for name, header in HEADERS.items():
            path = args.data / name
            if not path.exists():
                path.write_text(",".join(header) + "\n", encoding="utf-8")
                print(f"created {path}")
        return 0
    if not args.week:
        parser.error("--week or --init")
    report = review(args.data, dt.date.fromisoformat(args.week))
    out = args.data / "reviews" / f"{args.week}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(report, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
