#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import time
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import requests

from mobile_digest_helpers import (
    REPO_KEYWORDS_DEFAULT,
    assign_report_paths,
    build_markdown_digest,
    build_mobile_digest,
    compact_whitespace,
    enrich_paper_item,
    enrich_repo_item,
    join_url,
    keyword_in_text,
    strip_tags,
    write_site,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WATCHLIST = ROOT / "config" / "default_watchlist.json"
DEFAULT_OUTDIR = ROOT / "artifacts"
DEFAULT_SITE_DIR = ROOT / "site"
GITHUB_TRENDING_BASE = "https://github.com/trending"
GITHUB_SEARCH_API = "https://api.github.com/search/repositories"
ARXIV_API = "https://export.arxiv.org/api/query"
PUSHPLUS_URL = "https://www.pushplus.plus/send"
REQUEST_TIMEOUT = 30
DEFAULT_GITHUB_MIN_RELEVANCE_SCORE = 4
DEFAULT_GITHUB_FALLBACK_MIN_RELEVANCE_SCORE = 3
DEFAULT_GITHUB_ALLOWED_LABELS = ("直接相关", "中度相关")
DEFAULT_GITHUB_REQUIRED_KEYWORDS = (
    "robot",
    "robotics",
    "embodied",
    "grasp",
    "locomotion",
    "humanoid",
    "sim2real",
    "tactile",
    "ros",
    "ros2",
    "gazebo",
    "moveit",
    "isaac",
    "mujoco",
    "pinocchio",
)
DEFAULT_PAPER_PER_VENUE_CAP = 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect and push a mobile-first robotics digest.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_generate_options(target: argparse.ArgumentParser) -> None:
        target.add_argument("--watchlist", default=str(DEFAULT_WATCHLIST))
        target.add_argument("--outdir", default=str(DEFAULT_OUTDIR))
        target.add_argument("--site-dir", default=str(DEFAULT_SITE_DIR))
        target.add_argument("--public-base-url", default=os.getenv("PUBLIC_BASE_URL", ""))
        target.add_argument("--days", type=int, default=1)
        target.add_argument("--date", help="Reference date in YYYY-MM-DD format.")
        target.add_argument("--timezone", default="Asia/Shanghai")
        target.add_argument("--max-papers", type=int, default=10)
        target.add_argument("--max-repos", type=int, default=8)
        target.add_argument("--push-paper-count", type=int, default=2)
        target.add_argument("--push-repo-count", type=int, default=3)
        target.add_argument("--mailto", default=os.getenv("CROSSREF_MAILTO", ""))

    collect = subparsers.add_parser("collect", help="Collect signals and generate digest files.")
    add_generate_options(collect)

    push = subparsers.add_parser("push", help="Push an existing mobile digest file.")
    push.add_argument("--provider", choices=["pushplus", "wecom_bot"], required=True)
    push.add_argument("--title", required=True)
    push.add_argument("--content-file", required=True)
    push.add_argument("--token", default=os.getenv("PUSHPLUS_TOKEN", ""))
    push.add_argument("--webhook", default=os.getenv("WECOM_BOT_WEBHOOK", ""))
    push.add_argument("--dry-run", action="store_true")

    run = subparsers.add_parser("run", help="Collect, generate, and optionally push in one command.")
    add_generate_options(run)
    run.add_argument("--push-provider", choices=["pushplus", "wecom_bot"])
    run.add_argument("--push-title", default="")
    run.add_argument("--token", default=os.getenv("PUSHPLUS_TOKEN", ""))
    run.add_argument("--webhook", default=os.getenv("WECOM_BOT_WEBHOOK", ""))
    run.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def load_watchlist(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parse_reference_date(raw: str | None, timezone_name: str) -> date:
    if raw:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    return datetime.now(ZoneInfo(timezone_name)).date()


def build_headers(mailto: str = "") -> dict[str, str]:
    agent = "robotics-digest-cloud/3.0"
    if mailto:
        agent = f"{agent} (mailto:{mailto})"
    return {"User-Agent": agent, "Accept": "application/json, text/html;q=0.9"}


def score_text(text: str, keyword_weights: dict[str, int]) -> tuple[int, list[str]]:
    lowered = text.lower()
    score = 0
    hits: list[str] = []
    for keyword, weight in keyword_weights.items():
        if keyword_in_text(lowered, keyword):
            score += weight
            hits.append(keyword)
    return score, hits


def http_get(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    max_attempts: int = 4,
) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        response = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
        if response.status_code != 429:
            response.raise_for_status()
            return response
        retry_after = response.headers.get("Retry-After", "").strip()
        wait_seconds = int(retry_after) if retry_after.isdigit() else attempt * 2
        last_error = requests.HTTPError(f"429 rate limited for {url}", response=response)
        time.sleep(wait_seconds)
    if last_error:
        raise last_error
    raise RuntimeError(f"Failed to fetch {url}")


def get_crossref_date_parts(item: dict[str, Any]) -> list[int]:
    for key in ("published-print", "published-online", "published", "issued", "created"):
        parts = item.get(key, {}).get("date-parts")
        if parts and parts[0]:
            return parts[0]
    return []


def render_date(parts: list[int]) -> str:
    if not parts:
        return ""
    return "-".join(str(value).zfill(2) if index else str(value) for index, value in enumerate(parts))


def date_for_compare(parts: list[int]) -> date | None:
    if not parts:
        return None
    try:
        year = parts[0]
        month = parts[1] if len(parts) > 1 else 1
        day = parts[2] if len(parts) > 2 else 1
        return date(year, month, day)
    except ValueError:
        return None


def fetch_crossref_journal(
    source: dict[str, Any],
    start_date: date,
    max_items: int,
    mailto: str,
    keyword_weights: dict[str, int],
) -> list[dict[str, Any]]:
    response = http_get(
        f"https://api.crossref.org/journals/{source['issn']}/works",
        params={"filter": f"from-pub-date:{start_date.isoformat()}", "sort": "published", "order": "desc", "rows": max_items},
        headers=build_headers(mailto),
    )
    items = response.json()["message"]["items"]
    results: list[dict[str, Any]] = []
    for item in items:
        title = compact_whitespace((item.get("title") or [""])[0])
        abstract = strip_tags(item.get("abstract", ""))
        date_parts = get_crossref_date_parts(item)
        comparable = date_for_compare(date_parts)
        if comparable and comparable < start_date:
            continue
        score, hits = score_text(f"{title} {abstract}", keyword_weights)
        results.append(
            {
                "type": "paper",
                "title": title,
                "venue": source["name"],
                "published": render_date(date_parts),
                "doi": item.get("DOI", ""),
                "url": item.get("URL", ""),
                "abstract": abstract,
                "source_homepage": source.get("homepage", ""),
                "keyword_hits": hits,
                "relevance_score": score + (2 if abstract else 0),
            }
        )
    return results


def fetch_arxiv_candidates(reference_date: date, watchlist: dict[str, Any], keyword_weights: dict[str, int]) -> list[dict[str, Any]]:
    query = watchlist.get("paper_fallback_arxiv_query", "cat:cs.RO")
    max_results = int(watchlist.get("paper_fallback_arxiv_max_results", 12))
    recent_days = int(watchlist.get("paper_fallback_arxiv_recent_days", 14))
    cutoff = reference_date - timedelta(days=recent_days)
    response = http_get(
        ARXIV_API,
        params={
            "search_query": query,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": max_results,
        },
        headers={"User-Agent": "robotics-digest-cloud/3.0"},
    )
    root = ET.fromstring(response.text)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    candidates: list[dict[str, Any]] = []
    for entry in root.findall("atom:entry", namespace):
        published_raw = (entry.findtext("atom:published", default="", namespaces=namespace) or "").strip()
        try:
            published_dt = datetime.fromisoformat(published_raw.replace("Z", "+00:00"))
        except ValueError:
            continue
        if published_dt.date() < cutoff:
            continue
        title = compact_whitespace(entry.findtext("atom:title", default="", namespaces=namespace))
        abstract = compact_whitespace(entry.findtext("atom:summary", default="", namespaces=namespace))
        url = ""
        pdf_url = ""
        for link in entry.findall("atom:link", namespace):
            href = link.attrib.get("href", "")
            rel = link.attrib.get("rel", "")
            link_type = link.attrib.get("type", "")
            if rel == "alternate" and not url:
                url = href
            if link_type == "application/pdf" and not pdf_url:
                pdf_url = href
        score, hits = score_text(f"{title} {abstract}", keyword_weights)
        candidates.append(
            {
                "type": "paper",
                "title": title,
                "venue": "arXiv cs.RO",
                "published": published_dt.date().isoformat(),
                "doi": "",
                "url": url,
                "abstract": abstract,
                "pdf_url": pdf_url,
                "oa_url": pdf_url or url,
                "source_homepage": "https://arxiv.org/list/cs.RO/recent",
                "keyword_hits": hits,
                "relevance_score": score + 1,
            }
        )
    return sorted(candidates, key=lambda item: (item.get("relevance_score", 0), item.get("published", "")), reverse=True)


def select_diverse_papers(candidates: list[dict[str, Any]], max_papers: int, per_venue_cap: int) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in sorted(candidates, key=lambda entry: (entry.get("relevance_score", 0), entry.get("published", "")), reverse=True):
        grouped[item.get("venue", "未知来源")].append(item)

    venue_order = sorted(
        grouped.keys(),
        key=lambda venue: (grouped[venue][0].get("relevance_score", 0), grouped[venue][0].get("published", "")),
        reverse=True,
    )
    selected: list[dict[str, Any]] = []
    venue_counts: Counter[str] = Counter()
    added = True
    while len(selected) < max_papers and added:
        added = False
        for venue in venue_order:
            if venue_counts[venue] >= per_venue_cap:
                continue
            if not grouped[venue]:
                continue
            selected.append(grouped[venue].pop(0))
            venue_counts[venue] += 1
            added = True
            if len(selected) >= max_papers:
                break
    return selected


def parse_github_repo_block(block: str) -> dict[str, Any] | None:
    repo_match = re.search(r'<h2[^>]*>\s*<a[^>]*href="/([^"]+)"', block, re.IGNORECASE)
    if not repo_match:
        return None
    repo = compact_whitespace(repo_match.group(1))
    desc_match = re.search(r'<p[^>]*class="[^"]*color-fg-muted[^"]*"[^>]*>(.*?)</p>', block, re.I | re.S)
    lang_match = re.search(r'<span[^>]*itemprop="programmingLanguage"[^>]*>(.*?)</span>', block, re.I | re.S)
    stars_match = re.search(rf'href="/{re.escape(repo)}/stargazers"[^>]*>(.*?)</a>', block, re.I | re.S)
    forks_match = re.search(rf'href="/{re.escape(repo)}/forks"[^>]*>(.*?)</a>', block, re.I | re.S)
    today_match = re.search(r"([\d,]+)\s+stars today", block, re.I)
    return {
        "type": "repo",
        "repo": repo,
        "url": f"https://github.com/{repo}",
        "description": desc_match and strip_tags(desc_match.group(1)) or "",
        "language": lang_match and strip_tags(lang_match.group(1)) or "",
        "total_stars": stars_match and strip_tags(stars_match.group(1)).replace(",", "") or "0",
        "forks": forks_match and strip_tags(forks_match.group(1)).replace(",", "") or "0",
        "stars_today": today_match.group(1).replace(",", "") if today_match else "0",
        "source_kind": "trending",
    }


def fetch_github_trending(config: dict[str, Any], max_candidates: int) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for language in config.get("languages") or [""]:
        path = GITHUB_TRENDING_BASE if not language else f"{GITHUB_TRENDING_BASE}/{language}"
        response = http_get(f"{path}?{urlencode({'since': config.get('since', 'daily')})}", headers=build_headers(""))
        blocks = re.findall(r'<article class="Box-row".*?</article>', response.text, re.I | re.S)
        for block in blocks:
            parsed = parse_github_repo_block(block)
            if not parsed:
                continue
            existing = seen.get(parsed["repo"])
            if not existing or int(parsed["stars_today"] or "0") > int(existing["stars_today"] or "0"):
                seen[parsed["repo"]] = parsed
    repos = sorted(seen.values(), key=lambda item: (int(item.get("stars_today") or "0"), int(item.get("total_stars") or "0")), reverse=True)
    return repos[:max_candidates]


def fetch_github_search_candidates(watchlist: dict[str, Any], reference_date: date, headers: dict[str, str]) -> list[dict[str, Any]]:
    queries = watchlist.get("github_fallback_queries", [])
    if not queries:
        return []
    recent_days = int(watchlist.get("github_fallback_recent_days", 365))
    per_query = int(watchlist.get("github_fallback_per_query", 6))
    cutoff = reference_date - timedelta(days=recent_days)
    seen: dict[str, dict[str, Any]] = {}
    for entry in queries:
        query = entry.get("q", "") if isinstance(entry, dict) else str(entry)
        label = entry.get("label", query) if isinstance(entry, dict) else str(entry)
        if not query:
            continue
        response = http_get(
            GITHUB_SEARCH_API,
            params={
                "q": f"{query} pushed:>={cutoff.isoformat()} archived:false fork:false",
                "sort": "stars",
                "order": "desc",
                "per_page": per_query,
            },
            headers={**headers, "Accept": "application/vnd.github+json"},
        )
        for item in response.json().get("items", []):
            repo = item.get("full_name", "")
            if not repo or repo in seen:
                continue
            seen[repo] = {
                "type": "repo",
                "repo": repo,
                "url": item.get("html_url", ""),
                "description": item.get("description", "") or "",
                "language": item.get("language", "") or "",
                "total_stars": str(item.get("stargazers_count", 0)),
                "forks": str(item.get("forks_count", 0)),
                "stars_today": "0",
                "source_kind": "research_pick",
                "search_label": label,
            }
    return list(seen.values())


def select_relevant_repos(
    repos: list[dict[str, Any]],
    watchlist: dict[str, Any],
    max_repos: int,
    *,
    fallback_mode: bool = False,
) -> list[dict[str, Any]]:
    min_score = int(
        watchlist.get(
            "github_fallback_min_relevance_score" if fallback_mode else "github_min_relevance_score",
            DEFAULT_GITHUB_FALLBACK_MIN_RELEVANCE_SCORE if fallback_mode else DEFAULT_GITHUB_MIN_RELEVANCE_SCORE,
        )
    )
    allowed_labels = set(watchlist.get("github_allowed_relevance_labels", DEFAULT_GITHUB_ALLOWED_LABELS))
    required_keywords = set(watchlist.get("github_required_keywords_any", DEFAULT_GITHUB_REQUIRED_KEYWORDS))
    filtered = [
        item
        for item in repos
        if item.get("relevance_label") in allowed_labels
        and item.get("relevance_score", 0) >= min_score
        and (not required_keywords or required_keywords.intersection(item.get("keyword_hits", [])))
    ]
    return sorted(
        filtered,
        key=lambda item: (
            item.get("relevance_score", 0),
            1 if item.get("source_kind") == "trending" else 0,
            int(item.get("stars_today") or "0"),
            int(item.get("total_stars") or "0"),
        ),
        reverse=True,
    )[:max_repos]


def trim_for_push(markdown: str, limit: int = 3800) -> str:
    if len(markdown) <= limit:
        return markdown
    suffix = "\n\n内容过长，已截断；完整中文小文请看今日详情页。"
    return markdown[: limit - len(suffix)] + suffix


def push_message(provider: str, title: str, content: str, token: str = "", webhook: str = "", dry_run: bool = False) -> dict[str, Any]:
    if provider == "pushplus":
        if not token:
            raise ValueError("Missing PushPlus token.")
        payload = {"token": token, "title": title, "content": trim_for_push(content), "template": "markdown"}
        if dry_run:
            return {"provider": provider, "payload": payload, "dry_run": True}
        response = requests.post(PUSHPLUS_URL, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    if provider == "wecom_bot":
        if not webhook:
            raise ValueError("Missing Enterprise WeCom bot webhook.")
        payload = {"msgtype": "markdown", "markdown": {"content": trim_for_push(content)}}
        if dry_run:
            return {"provider": provider, "payload": payload, "dry_run": True}
        response = requests.post(webhook, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    raise ValueError(f"Unsupported provider: {provider}")


def collect_digest(args: argparse.Namespace) -> tuple[dict[str, Any], Path, Path, Path]:
    watchlist = load_watchlist(args.watchlist)
    reference_date = parse_reference_date(args.date, args.timezone)
    start_date = reference_date - timedelta(days=max(args.days - 1, 0))
    paper_weights = watchlist.get("paper_keywords", {})
    repo_weights = watchlist.get("github_keywords", REPO_KEYWORDS_DEFAULT)
    headers = build_headers(args.mailto)
    errors: list[dict[str, str]] = []

    papers: list[dict[str, Any]] = []
    paper_pool_per_journal = int(watchlist.get("paper_candidate_pool_per_journal", max(args.max_papers, 6)))
    for source in watchlist.get("journals", []):
        try:
            papers.extend(fetch_crossref_journal(source, start_date, paper_pool_per_journal, args.mailto, paper_weights))
        except requests.RequestException as exc:
            errors.append({"source": source["name"], "error": str(exc)})
        time.sleep(1.0)
    papers = select_diverse_papers(papers, args.max_papers, int(watchlist.get("paper_per_venue_cap", DEFAULT_PAPER_PER_VENUE_CAP)))

    target_venue_count = int(watchlist.get("paper_target_venue_count", 2))
    if len({item.get("venue", "") for item in papers}) < target_venue_count or len(papers) < args.max_papers:
        try:
            arxiv_candidates = fetch_arxiv_candidates(reference_date, watchlist, paper_weights)
        except requests.RequestException as exc:
            errors.append({"source": "arXiv cs.RO", "error": str(exc)})
            arxiv_candidates = []
        existing_titles = {item["title"] for item in papers}
        for candidate in arxiv_candidates:
            if candidate["title"] in existing_titles:
                continue
            papers.append(candidate)
            existing_titles.add(candidate["title"])
            if len(papers) >= args.max_papers:
                break
            if len({item.get("venue", "") for item in papers}) >= target_venue_count and len(papers) >= min(args.max_papers, target_venue_count):
                break

    papers = select_diverse_papers(papers, args.max_papers, int(watchlist.get("paper_per_venue_cap", DEFAULT_PAPER_PER_VENUE_CAP)))
    papers = [enrich_paper_item(item, headers) for item in papers[: args.max_papers]]

    trending_candidates: list[dict[str, Any]] = []
    fallback_candidates: list[dict[str, Any]] = []
    try:
        trending_candidates = fetch_github_trending(
            watchlist.get("github_trending", {}),
            int(watchlist.get("github_candidate_pool_size", max(args.max_repos * 8, 40))),
        )
    except requests.RequestException as exc:
        errors.append({"source": "GitHub Trending", "error": str(exc)})
    try:
        fallback_candidates = fetch_github_search_candidates(watchlist, reference_date, build_headers(""))
    except requests.RequestException as exc:
        errors.append({"source": "GitHub Search", "error": str(exc)})

    trending_enriched = [enrich_repo_item(item, build_headers(""), repo_weights) for item in trending_candidates]
    fallback_enriched = [enrich_repo_item(item, build_headers(""), repo_weights) for item in fallback_candidates]

    repos = select_relevant_repos(trending_enriched, watchlist, args.max_repos)
    if len(repos) < args.max_repos:
        existing = {item["repo"] for item in repos}
        needed = args.max_repos - len(repos)
        extras = [
            item
            for item in select_relevant_repos(fallback_enriched, watchlist, args.max_repos * 2, fallback_mode=True)
            if item["repo"] not in existing
        ][:needed]
        repos.extend(extras)

    report = {
        "generated_at": datetime.now(ZoneInfo(args.timezone)).isoformat(timespec="seconds"),
        "reference_date": reference_date.isoformat(),
        "window_start": start_date.isoformat(),
        "timezone": args.timezone,
        "papers": papers,
        "repos": repos,
        "errors": errors,
    }
    assign_report_paths(report)

    full_md = build_markdown_digest(report, args.public_base_url)
    mobile_md = build_mobile_digest(report, args.public_base_url, args.push_paper_count, args.push_repo_count)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    base = f"{reference_date.isoformat()}-robotics-digest"
    json_path = outdir / f"{base}.json"
    full_md_path = outdir / f"{base}.md"
    mobile_md_path = outdir / f"{base}-mobile.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    full_md_path.write_text(full_md, encoding="utf-8")
    mobile_md_path.write_text(mobile_md, encoding="utf-8")

    site_dir = Path(args.site_dir)
    write_site(report, site_dir)
    day_dir = site_dir / "daily" / report["reference_date"]
    (day_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (day_dir / "full.md").write_text(full_md, encoding="utf-8")
    (day_dir / "mobile.md").write_text(mobile_md, encoding="utf-8")
    return report, full_md_path, mobile_md_path, site_dir


def default_push_title(reference_date: str) -> str:
    return f"今日具身智能快报 {reference_date}"


def run_collect(args: argparse.Namespace) -> int:
    report, full_md_path, mobile_md_path, site_dir = collect_digest(args)
    print(f"Saved full digest markdown to {full_md_path}")
    print(f"Saved mobile digest markdown to {mobile_md_path}")
    print(f"Built static site to {site_dir}")
    print(f"Daily page URL: {join_url(args.public_base_url, report['daily_relpath']) or report['daily_relpath']}")
    print(f"Collected {len(report['papers'])} papers and {len(report['repos'])} repos.")
    return 0


def run_push(args: argparse.Namespace) -> int:
    content = Path(args.content_file).read_text(encoding="utf-8")
    result = push_message(args.provider, args.title, content, args.token, args.webhook, args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def run_all(args: argparse.Namespace) -> int:
    report, full_md_path, mobile_md_path, site_dir = collect_digest(args)
    print(f"Saved full digest markdown to {full_md_path}")
    print(f"Saved mobile digest markdown to {mobile_md_path}")
    print(f"Built static site to {site_dir}")
    print(f"Daily page URL: {join_url(args.public_base_url, report['daily_relpath']) or report['daily_relpath']}")
    print(f"Collected {len(report['papers'])} papers and {len(report['repos'])} repos.")
    if not args.push_provider:
        return 0
    result = push_message(
        args.push_provider,
        args.push_title or default_push_title(report["reference_date"]),
        mobile_md_path.read_text(encoding="utf-8"),
        args.token,
        args.webhook,
        args.dry_run,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "collect":
        return run_collect(args)
    if args.command == "push":
        return run_push(args)
    if args.command == "run":
        return run_all(args)
    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
