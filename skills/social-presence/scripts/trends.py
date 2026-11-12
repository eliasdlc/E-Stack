#!/usr/bin/env python3
"""What developers, AI and indie builders, and the Dominican tech scene talk about this week.

Free, keyless sources that answer from this machine: Hacker News (Algolia),
GitHub trending, Reddit RSS, dev.to, Lobsters, Product Hunt, Google News RSS,
Bluesky search and Hugging Face. X and LinkedIn have no free legitimate read
path, so their conversation reaches the radar only through these mirrors.

    trends.py              # digest; an unfiltered run is saved to the data folder as trends/<date>.json
    trends.py --prove      # fetch every source once and print status, count and first item
    trends.py --group ai   # one group only

Every item carries its link, so a draft can quote or reply to the real thing.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

DATA = Path.home() / "Documents/Personal/dev/social-presence"
UA = "Mozilla/5.0 (X11; Linux x86_64) decruce-social-presence/1.0 (+https://decruce.dev)"
WEEK = 7 * 24 * 3600
ATOM = "{http://www.w3.org/2005/Atom}"


@dataclass
class Item:
    source: str
    group: str
    title: str
    url: str
    score: float  # the source's own signal (points, stars, reactions), not comparable across sources
    discussion: str = ""


def fetch(url: str, timeout: int = 20, retries: int = 2) -> bytes:
    """GET with a backoff on 429, because Reddit and dev.to rate-limit anonymous clients within seconds."""
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == retries:
                raise
            wait = int(error.headers.get("Retry-After") or 0) or 10 * (attempt + 1)
            time.sleep(min(wait, 30))
    raise AssertionError("unreachable")


def fetch_json(url: str):
    return json.loads(fetch(url))


def since_epoch() -> int:
    return int(time.time()) - WEEK


# Searches per group. Groups map to what Elias builds and who he wants to reach.
HN_QUERIES = {"ai": ["claude", "AI agent", "LLM"], "flutter": ["flutter"], "web": ["next.js", "typescript"],
              "indie": ["show hn"]}
# Five subreddits: anonymous Reddit allows roughly one feed every few seconds, and more means minutes of backoff.
REDDIT = {"ai": ["ClaudeAI"], "flutter": ["FlutterDev"], "web": ["webdev"], "indie": ["SideProject"], "dr-latam": ["Dominican"]}
DEVTO_TAGS = {"ai": "ai", "flutter": "flutter", "web": "nextjs", "indie": "startup"}
NEWS = {"dr-latam": ["tecnología República Dominicana", "startup dominicana", "Barcamp RD",
                     "Dominicana tech week", "Hackers and Founders Santo Domingo"],
        "ai": ["Claude Code", "AI coding agents"]}
BSKY = {"ai": ["claude code", "ai agents"], "flutter": ["flutter dev"], "web": ["nextjs"],
        "indie": ["buildinpublic"]}


def hn() -> list[Item]:
    items = []
    for group, queries in HN_QUERIES.items():
        for q in queries:
            url = ("https://hn.algolia.com/api/v1/search?" + urllib.parse.urlencode(
                {"query": q, "tags": "story", "typoTolerance": "false", "restrictSearchableAttributes": "title",
                 "numericFilters": f"created_at_i>{since_epoch()},points>40", "hitsPerPage": 8}))
            for hit in fetch_json(url)["hits"]:
                link = f"https://news.ycombinator.com/item?id={hit['objectID']}"
                items.append(Item("hn", group, hit["title"], hit.get("url") or link, hit.get("points", 0), link))
    front = fetch_json("https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=15")["hits"]
    items += [Item("hn", "general", h["title"], h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}",
                   h.get("points", 0), f"https://news.ycombinator.com/item?id={h['objectID']}") for h in front]
    return items


def github_trending() -> list[Item]:
    items = []
    for group, path in (("general", ""), ("flutter", "/dart"), ("web", "/typescript")):
        page = fetch(f"https://github.com/trending{path}?since=weekly").decode("utf-8", "replace")
        for article in re.findall(r"<article class=\"Box-row\">(.*?)</article>", page, re.S):
            repo = re.search(r"<h2[^>]*>\s*<a[^>]*href=\"/([^\"]+)\"", article)
            if not repo:
                continue
            desc = re.search(r"<p class=\"col-9[^\"]*\">(.*?)</p>", article, re.S)
            stars = re.search(r"([\d,]+) stars this week", article)
            text = html.unescape(re.sub(r"\s+", " ", desc.group(1)).strip()) if desc else ""
            items.append(Item("github", group, f"{repo.group(1)}: {text}"[:200], f"https://github.com/{repo.group(1)}",
                              float(stars.group(1).replace(",", "")) if stars else 0))
    return items


def reddit() -> list[Item]:
    """Reddit answers RSS to an anonymous client and refuses its JSON; it rate-limits fast, so calls are spaced."""
    items = []
    for group, subs in REDDIT.items():
        for sub in subs:
            try:
                feed = ET.fromstring(fetch(f"https://www.reddit.com/r/{sub}/top/.rss?t=week&limit=8"))
            except Exception as error:  # one sub refusing should not sink the rest
                print(f"reddit r/{sub}: {error}", file=sys.stderr)
                continue
            finally:
                time.sleep(6)
            for rank, entry in enumerate(feed.findall(f"{ATOM}entry")):
                link = entry.find(f"{ATOM}link").get("href")
                items.append(Item("reddit", group, f"r/{sub}: {entry.findtext(f'{ATOM}title')}", link, 10 - rank, link))
    return items


def devto() -> list[Item]:
    items = []
    for group, tag in DEVTO_TAGS.items():
        for a in fetch_json(f"https://dev.to/api/articles?top=7&tag={tag}&per_page=8"):
            items.append(Item("devto", group, a["title"], a["url"], a.get("public_reactions_count", 0), a["url"]))
        time.sleep(2)
    return items


def lobsters() -> list[Item]:
    return [Item("lobsters", "general", s["title"], s.get("url") or s["short_id_url"], s.get("score", 0), s["short_id_url"])
            for s in fetch_json("https://lobste.rs/hottest.json")[:15]]


def producthunt() -> list[Item]:
    feed = ET.fromstring(fetch("https://www.producthunt.com/feed"))
    return [Item("producthunt", "indie", e.findtext(f"{ATOM}title"), e.find(f"{ATOM}link").get("href"), 20 - rank)
            for rank, e in enumerate(feed.findall(f"{ATOM}entry")[:20])]


def google_news() -> list[Item]:
    items = []
    for group, queries in NEWS.items():
        for q in queries:
            url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
                {"q": f"{q} when:7d", "hl": "es-419", "gl": "DO", "ceid": "DO:es-419"})
            channel = ET.fromstring(fetch(url)).find("channel")
            for rank, item in enumerate(channel.findall("item")[:6]):
                items.append(Item("news", group, item.findtext("title"), item.findtext("link"), 6 - rank))
    return items


def bluesky() -> list[Item]:
    items = []
    for group, queries in BSKY.items():
        for q in queries:
            url = "https://api.bsky.app/xrpc/app.bsky.feed.searchPosts?" + urllib.parse.urlencode(
                {"q": q, "sort": "top", "since": dt.datetime.fromtimestamp(since_epoch(), dt.timezone.utc).isoformat(), "limit": 8})
            for post in fetch_json(url).get("posts", []):
                handle, rkey = post["author"]["handle"], post["uri"].rsplit("/", 1)[-1]
                link = f"https://bsky.app/profile/{handle}/post/{rkey}"
                text = re.sub(r"\s+", " ", post["record"].get("text", ""))[:180]
                items.append(Item("bluesky", group, f"@{handle}: {text}", link,
                                  post.get("likeCount", 0) + 2 * post.get("repostCount", 0), link))
    return items


def huggingface() -> list[Item]:
    data = fetch_json("https://huggingface.co/api/trending?limit=15")
    rows = data.get("recentlyTrending", data if isinstance(data, list) else [])
    items = []
    for row in rows[:15]:
        repo = row.get("repoData", row)
        rid = repo.get("id", "")
        kind = row.get("repoType", "model")
        prefix = "" if kind == "model" else f"{kind}s/"
        items.append(Item("huggingface", "ai", f"{rid} ({kind})", f"https://huggingface.co/{prefix}{rid}", repo.get("likes", 0)))
    return items


SOURCES: dict[str, Callable[[], list[Item]]] = {
    "hn": hn, "github": github_trending, "reddit": reddit, "devto": devto, "lobsters": lobsters,
    "producthunt": producthunt, "news": google_news, "bluesky": bluesky, "huggingface": huggingface,
}


def collect(names: list[str]) -> tuple[list[Item], dict[str, str]]:
    items, status = [], {}
    for name in names:
        started = time.time()
        try:
            got = SOURCES[name]()
            status[name] = f"ok {len(got)} items in {time.time() - started:.1f}s"
            items += got
        except Exception as error:
            status[name] = f"failed: {type(error).__name__}: {error}"[:160]
    return items, status


def digest(items: list[Item], group: str | None, per_group: int) -> dict[str, list[Item]]:
    """Top items per group, ranked within each source first so one loud source cannot fill a group."""
    seen, by_group = set(), {}
    for item in items:
        if group and item.group != group:
            continue
        key = re.sub(r"\W+", "", item.title.lower())[:60]
        if key in seen:
            continue
        seen.add(key)
        by_group.setdefault(item.group, []).append(item)
    ranked = {}
    for name, group_items in by_group.items():
        per_source: dict[str, list[Item]] = {}
        for item in sorted(group_items, key=lambda i: i.score, reverse=True):
            per_source.setdefault(item.source, []).append(item)
        interleaved = []
        while any(per_source.values()) and len(interleaved) < per_group:
            for queue in per_source.values():
                if queue and len(interleaved) < per_group:
                    interleaved.append(queue.pop(0))
        ranked[name] = interleaved
    return ranked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--prove", action="store_true", help="fetch each source once and report what came back")
    parser.add_argument("--source", action="append", choices=sorted(SOURCES), help="limit to these sources")
    parser.add_argument("--group", help="ai, flutter, web, indie, dr-latam or general")
    parser.add_argument("--per-group", type=int, default=8)
    parser.add_argument("--data", type=Path, default=DATA)
    args = parser.parse_args()

    names = args.source or list(SOURCES)
    items, status = collect(names)

    if args.prove:
        for name in names:
            first = next((i for i in items if i.source == name), None)
            print(f"{name:12} {status[name]}")
            if first:
                print(f"{'':12} first: {first.title[:90]} <{first.url}>")
        return 0 if all(s.startswith("ok") and not s.startswith("ok 0 ") for s in status.values()) else 1

    ranked = digest(items, args.group, args.per_group)
    saved = ""
    if not args.source and not args.group:  # a filtered run must not overwrite the day's full digest
        out = args.data / "trends" / f"{dt.date.today().isoformat()}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"status": status, "groups": {g: [asdict(i) for i in v] for g, v in ranked.items()}},
                                  indent=1, ensure_ascii=False))
        saved = f" ({out})"
    print(f"Trends {dt.date.today().isoformat()}{saved}")
    for name, state in status.items():
        if not state.startswith("ok"):
            print(f"  source down: {name}: {state}")
    for name, group_items in ranked.items():
        print(f"\n## {name}")
        for item in group_items:
            extra = f" | discuss: {item.discussion}" if item.discussion and item.discussion != item.url else ""
            print(f"- [{item.source} {item.score:g}] {item.title[:110]}\n  {item.url}{extra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
