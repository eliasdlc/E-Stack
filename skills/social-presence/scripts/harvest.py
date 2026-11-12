#!/usr/bin/env python3
"""Find what Elias shipped since the last run that is worth telling in public.

Reads GitHub through the authenticated `gh` CLI (merged PRs, releases, new
public repositories) and the project documents under ~/Documents/Proyectos,
then prints a short ranked list of stories, each with its evidence link.

What may be shown is decided by the profile (profile.json in the data folder):
`harvest.exclude_owners` and `harvest.exclude_repos` drop work that is not his
to show (the internship, class assignments), and `harvest.doc_projects` names
the Documents projects that are his own. A private repository yields a story
without its link and without internals, marked so the draft tells the outcome
only. Client projects are never read.

    harvest.py                      # since the last run, then remember this run
    harvest.py --since 2026-10-01   # explicit window, state untouched
    harvest.py --json               # machine-readable
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path

DATA = Path.home() / "Documents/Personal/dev/social-presence"
DOCUMENTS = Path.home() / "Documents/Proyectos"
# Conventional Commit types that never make a story on their own.
CHORE = re.compile(r"^(chore|ci|build|test|style|docs|refactor|revert)(\(|:|!)", re.I)
FEATURE = re.compile(r"^feat(\(|:|!)", re.I)
FIX = re.compile(r"^(fix|perf)(\(|:|!)", re.I)
DOC_SIGNAL = re.compile(r"decision|launch|lanzamiento|release|roadmap|demo|press|prensa", re.I)


@dataclass
class Story:
    score: int
    kind: str
    title: str
    evidence: str
    repo: str = ""
    private: bool = False
    details: list[str] = field(default_factory=list)


def gh_graphql(query: str, **variables: str) -> dict:
    args = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        args += ["-F", f"{key}={value}"]
    out = subprocess.run(args, capture_output=True, text=True, check=True).stdout
    return json.loads(out)["data"]


PRS = """query($q: String!, $after: String) {
  search(query: $q, type: ISSUE, first: 100, after: $after) {
    pageInfo { hasNextPage endCursor }
    nodes { ... on PullRequest { title url mergedAt additions deletions
      repository { nameWithOwner isPrivate url } } }
  }
}"""

REPOS = """query($after: String) {
  viewer { repositories(first: 100, after: $after, orderBy: {field: PUSHED_AT, direction: DESC},
      ownerAffiliations: [OWNER, ORGANIZATION_MEMBER, COLLABORATOR]) {
    pageInfo { hasNextPage endCursor }
    nodes { nameWithOwner isPrivate url homepageUrl createdAt pushedAt description stargazerCount
      releases(first: 5, orderBy: {field: CREATED_AT, direction: DESC}) {
        nodes { name tagName publishedAt url isPrerelease } } }
  } }
}"""


def merged_prs(login: str, since: str) -> list[dict]:
    rows, after = [], None
    while True:
        variables = {"q": f"author:{login} is:pr is:merged merged:>={since}"}
        if after:
            variables["after"] = after
        page = gh_graphql(PRS, **variables)["search"]
        rows += [n for n in page["nodes"] if n]
        if not page["pageInfo"]["hasNextPage"] or len(rows) >= 1000:
            return rows
        after = page["pageInfo"]["endCursor"]


def repositories(since: str) -> list[dict]:
    rows, after = [], None
    while True:
        page = gh_graphql(REPOS, **({"after": after} if after else {}))["viewer"]["repositories"]
        rows += page["nodes"]
        oldest = page["nodes"][-1]["pushedAt"] if page["nodes"] else since
        if not page["pageInfo"]["hasNextPage"] or oldest < since:
            return rows
        after = page["pageInfo"]["endCursor"]


def allowed(repo: str, profile: dict) -> bool:
    rules = profile.get("harvest", {})
    owner = repo.split("/")[0]
    return owner not in rules.get("exclude_owners", []) and repo not in rules.get("exclude_repos", [])


def pr_stories(prs: list[dict], profile: dict) -> list[Story]:
    """One story per repository: its features and fixes, ranked by how much shipped."""
    by_repo: dict[str, list[dict]] = defaultdict(list)
    for pr in prs:
        if allowed(pr["repository"]["nameWithOwner"], profile) and not CHORE.match(pr["title"]):
            by_repo[pr["repository"]["nameWithOwner"]].append(pr)
    stories = []
    for repo, items in by_repo.items():
        private = items[0]["repository"]["isPrivate"]
        features = [p for p in items if FEATURE.match(p["title"])]
        fixes = [p for p in items if FIX.match(p["title"])]
        if not features and not fixes:
            continue
        top = sorted(features or fixes, key=lambda p: p["additions"] + p["deletions"], reverse=True)
        score = 3 * len(features) + len(fixes) + (2 if not private else 0)
        title = f"{repo}: {len(features)} features and {len(fixes)} fixes merged"
        evidence = "private repository, link withheld" if private else f"{items[0]['repository']['url']}/pulls?q=is%3Amerged"
        details = [p["title"] if private else f"{p['title']} ({p['url']})" for p in top[:5]]
        stories.append(Story(score, "shipped", title, evidence, repo, private, details))
    return stories


def repo_stories(repos: list[dict], since: str, profile: dict) -> list[Story]:
    stories = []
    for repo in repos:
        name = repo["nameWithOwner"]
        if not allowed(name, profile):
            continue
        for release in repo["releases"]["nodes"]:
            if release["publishedAt"] and release["publishedAt"] >= since and not release["isPrerelease"]:
                link = "private repository, link withheld" if repo["isPrivate"] else release["url"]
                stories.append(Story(8 if not repo["isPrivate"] else 5, "release",
                                     f"{name} released {release['name'] or release['tagName']}", link, name, repo["isPrivate"]))
        if not repo["isPrivate"] and repo["createdAt"] >= since:
            stories.append(Story(6, "new-public-repo", f"New public repository {name}", repo["url"], name, False,
                                 [repo["description"] or "no description yet"]))
        if not repo["isPrivate"] and repo["homepageUrl"] and repo["pushedAt"] >= since:
            stories.append(Story(2, "live-demo", f"{name} has a live site", repo["homepageUrl"], name, False))
    return stories


def doc_stories(since: str, profile: dict) -> list[Story]:
    """Decision, launch and release documents of his own projects changed in the window."""
    stamp = dt.datetime.fromisoformat(since).timestamp()
    stories = []
    for project in profile.get("harvest", {}).get("doc_projects", []):
        root = DOCUMENTS / project
        if not root.is_dir():
            continue
        for path in root.rglob("*.md"):
            if DOC_SIGNAL.search(path.name) and path.stat().st_mtime >= stamp:
                changed = dt.datetime.fromtimestamp(path.stat().st_mtime).date().isoformat()
                stories.append(Story(4, "project-doc", f"{project}: {path.stem} updated {changed}",
                                     str(path).replace(str(Path.home()), "~"), project, True))
    return stories


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--since", help="ISO date; default is the last run, or 14 days ago")
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    profile = json.loads((args.data / "profile.json").read_text())
    state_file = args.data / "harvest/state.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    since = args.since or state.get("last_run") or (dt.date.today() - dt.timedelta(days=14)).isoformat()

    login = profile["accounts"]["github"]
    stories = pr_stories(merged_prs(login, since), profile)
    stories += repo_stories(repositories(since), since, profile)
    stories += doc_stories(since, profile)
    stories.sort(key=lambda s: s.score, reverse=True)
    stories = stories[: args.limit]

    if args.json:
        print(json.dumps({"since": since, "stories": [asdict(s) for s in stories]}, indent=1))
    else:
        print(f"Stories since {since}: {len(stories)}")
        for s in stories:
            flag = " [private: outcome only]" if s.private else ""
            print(f"\n{s.score:>3}  {s.kind}: {s.title}{flag}\n     evidence: {s.evidence}")
            for d in s.details:
                print(f"     - {d}")
    if not args.since:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps({"last_run": dt.date.today().isoformat()}) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
