from __future__ import annotations

import json
import re
from html import escape, unescape
from pathlib import Path
from typing import Any

import requests


OPENALEX_BASE = "https://api.openalex.org/works"
GITHUB_REPO_BASE = "https://github.com"
REQUEST_TIMEOUT = 30

REPO_KEYWORDS_DEFAULT = {
    "robot": 4,
    "robotics": 4,
    "embodied": 4,
    "grasp": 3,
    "locomotion": 3,
    "humanoid": 3,
    "simulation": 3,
    "sim2real": 4,
    "ros": 3,
    "ros2": 4,
    "gazebo": 3,
    "moveit": 4,
    "isaac": 3,
    "mujoco": 2,
    "pinocchio": 2,
    "manipulation": 3,
    "navigation": 2,
    "planning": 2,
    "control": 2,
    "reinforcement": 2,
    "rl": 2,
    "dataset": 1,
    "benchmark": 1,
    "vision": 1,
    "multimodal": 1,
    "agent": 1,
    "policy": 2,
}

SITE_CSS = """
:root{--bg:#f6f2ea;--fg:#171512;--muted:#5e584f;--line:#d8cec0;--accent:#b5552d;--max:920px}
*{box-sizing:border-box}body{margin:0;background:linear-gradient(180deg,#faf7f0,#f4eee4);color:var(--fg);font:16px/1.7 "Segoe UI","PingFang SC","Noto Sans SC",sans-serif}
.page{width:min(100%,var(--max));margin:0 auto;padding:24px 18px 72px}.hero{padding:8px 0 24px;border-bottom:1px solid var(--line);margin-bottom:24px}
.eyebrow{color:var(--accent);font-size:12px;letter-spacing:.1em;text-transform:uppercase}.lead{color:var(--muted);max-width:42rem}
h1,h2,h3{font-family:"Iowan Old Style","Palatino Linotype",Georgia,serif;line-height:1.1;margin:0}
h1{font-size:clamp(34px,8vw,62px);letter-spacing:-.03em}h2{font-size:clamp(24px,5vw,34px);letter-spacing:-.02em}
.section{padding:22px 0;border-bottom:1px solid var(--line)}.entry{padding:18px 0;border-top:1px dashed var(--line)}.entry:first-child{border-top:0;padding-top:0}
.meta,.links,.tags{display:flex;flex-wrap:wrap;gap:10px 14px;color:var(--muted);font-size:14px}.links a{color:#8e3d20;font-weight:600}
.pill,.tag{display:inline-flex;padding:5px 10px;border-radius:999px;border:1px solid var(--line);font-size:12px}.pill{background:#f2dfd3;border-color:#e2c2af;color:#8e3d20}
.grid{display:grid;gap:12px;margin-top:12px}.block{padding-left:12px;border-left:2px solid #ecd6c8}.k{display:block;color:var(--accent);font-size:12px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px}
.quote{padding:14px 16px;border-left:3px solid var(--accent);background:rgba(255,255,255,.4);color:var(--muted);margin-top:14px}
.facts{display:grid;gap:10px}.fact{display:grid;grid-template-columns:110px 1fr;gap:10px;padding:8px 0;border-top:1px dashed var(--line)}.fact:first-child{border-top:0}
a{color:#8e3d20;text-underline-offset:.18em}.back{display:inline-block;margin-top:10px}
@media(min-width:760px){.grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
"""

PAPER_DIRECTION_RULES = [
    (("manipulation", "grasp", "contact", "gripper"), "机械臂操控"),
    (("tactile", "touch", "visuotactile"), "触觉与接触感知"),
    (("locomotion", "humanoid", "legged", "biped", "quadruped", "gait"), "足式与人形运动"),
    (("navigation", "planning", "parkour"), "导航与规划"),
    (("sim2real", "simulation", "sim-to-real"), "仿真到真实迁移"),
    (("language model", "llm", "agent", "ros"), "大模型机器人系统"),
    (("surgery", "surgical"), "手术机器人"),
]

METHOD_RULES = [
    (("reinforcement learning", " rl "), "强化学习"),
    (("transformer",), "Transformer"),
    (("diffusion",), "Diffusion"),
    (("constraint", "constrained"), "约束建模"),
    (("sim2real", "sim-to-real"), "Sim2Real"),
    (("tactile", "touch"), "触觉反馈"),
    (("world model",), "世界模型"),
    (("rag", "retrieval"), "检索增强"),
    (("language model", "llm"), "语言模型"),
    (("depth", "geometry"), "几何/深度估计"),
]


def compact_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def keyword_in_text(text: str, keyword: str) -> bool:
    if not text or not keyword:
        return False
    lowered_text = text.lower()
    lowered_keyword = keyword.lower()
    return bool(re.search(rf"(?<![a-z0-9]){re.escape(lowered_keyword)}(?![a-z0-9])", lowered_text))


def strip_tags(text: str) -> str:
    if not text:
        return ""
    return compact_whitespace(unescape(re.sub(r"<[^>]+>", " ", text)))


def strip_html_to_text(text: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.I | re.S)
    return strip_tags(text)


def shorten(text: str, max_length: int) -> str:
    text = compact_whitespace(text)
    if len(text) <= max_length:
        return text
    return text[: max_length - 1].rstrip() + "…"


def slugify(text: str, max_length: int = 72) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    slug = slug[:max_length].strip("-")
    return slug or "item"


def join_url(base_url: str, relpath: str) -> str:
    if not base_url:
        return ""
    return f"{base_url.rstrip('/')}/{relpath.lstrip('/')}"


def select_sentences(text: str) -> list[str]:
    raw_parts = re.split(r"(?<=[.!?])\s+", text)
    return [compact_whitespace(part) for part in raw_parts if compact_whitespace(part)]


def pick_sentence(text: str, keywords: tuple[str, ...]) -> str:
    for sentence in select_sentences(text):
        lowered = sentence.lower()
        if any(keyword in lowered for keyword in keywords):
            return sentence
    return ""


def reconstruct_openalex_abstract(abstract_inverted_index: dict[str, list[int]] | None) -> str:
    if not abstract_inverted_index:
        return ""
    slots: dict[int, str] = {}
    for word, positions in abstract_inverted_index.items():
        for position in positions:
            slots[position] = word
    if not slots:
        return ""
    return compact_whitespace(" ".join(slots[index] for index in range(max(slots) + 1) if index in slots))


def fetch_openalex_metadata(doi: str, headers: dict[str, str]) -> dict[str, Any]:
    if not doi:
        return {}
    try:
        response = requests.get(
            OPENALEX_BASE,
            params={"filter": f"doi:{doi}", "per-page": 1},
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        results = response.json().get("results") or []
        if not results:
            return {}
        item = results[0]
        return {
            "abstract": reconstruct_openalex_abstract(item.get("abstract_inverted_index")),
            "cited_by_count": item.get("cited_by_count"),
            "primary_topic": (item.get("primary_topic") or {}).get("display_name", ""),
            "concepts": [entry.get("display_name", "") for entry in item.get("concepts", [])[:6] if entry.get("display_name")],
            "oa_url": ((item.get("open_access") or {}).get("oa_url") or ""),
            "oa_status": ((item.get("open_access") or {}).get("oa_status") or ""),
        }
    except requests.RequestException:
        return {}


def fetch_repo_page_details(repo: str, headers: dict[str, str]) -> dict[str, Any]:
    details = {"description": "", "readme_excerpt": "", "topics": []}
    try:
        response = requests.get(f"{GITHUB_REPO_BASE}/{repo}", headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException:
        return details

    html = response.text
    meta_match = re.search(r'<meta name="description" content="([^"]+)"', html)
    if meta_match:
        details["description"] = compact_whitespace(unescape(meta_match.group(1))).replace(f" - {repo}", "")

    readme_match = re.search(r'<article[^>]*class="[^"]*markdown-body[^"]*"[^>]*>(.*?)</article>', html, re.I | re.S)
    if readme_match:
        details["readme_excerpt"] = shorten(strip_html_to_text(readme_match.group(1)), 900)

    topic_matches = re.findall(r'/topics/[^"]+"[^>]*>([^<]+)</a>', html, re.I)
    if topic_matches:
        details["topics"] = [compact_whitespace(unescape(item)) for item in topic_matches[:8]]
    return details


def infer_paper_direction(text: str) -> str:
    lowered = text.lower()
    for keywords, label in PAPER_DIRECTION_RULES:
        if any(keyword in lowered for keyword in keywords):
            return label
    return "机器人通用方法"


def infer_method_tags(text: str) -> list[str]:
    lowered = f" {text.lower()} "
    tags = [label for keywords, label in METHOD_RULES if any(keyword in lowered for keyword in keywords)]
    seen: list[str] = []
    for tag in tags:
        if tag not in seen:
            seen.append(tag)
    return seen[:4]


def evidence_label(item: dict[str, Any]) -> str:
    if item.get("abstract"):
        return "摘要支撑"
    return "仅标题/元数据"


def theory_hint(abstract: str) -> str:
    keywords = ("equation", "objective", "loss", "optimi", "dynamic", "control", "policy", "constraint", "model", "diffusion", "transformer")
    sentence = pick_sentence(abstract, keywords)
    if sentence:
        return sentence
    if abstract:
        return "公开摘要没有直接暴露明确公式，但可以先根据方法标签和摘要句判断技术路线。"
    return "当前只拿到标题/元数据，无法负责任地还原公式细节。"


def enrich_paper_item(item: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    openalex = fetch_openalex_metadata(item.get("doi", ""), headers)
    abstract = item.get("abstract") or openalex.get("abstract") or ""
    direction = infer_paper_direction(" ".join([item.get("title", ""), abstract, openalex.get("primary_topic", "")]))
    method_tags = infer_method_tags(" ".join([item.get("title", ""), abstract, " ".join(openalex.get("concepts", []))]))
    overview_sentence = select_sentences(abstract)[0] if abstract else ""
    method_sentence = pick_sentence(abstract, ("propose", "present", "introduce", "framework", "method", "approach", "policy", "objective", "transformer", "diffusion"))
    item.update(
        {
            "abstract": abstract,
            "cited_by_count": openalex.get("cited_by_count"),
            "primary_topic": openalex.get("primary_topic", ""),
            "concepts": openalex.get("concepts", []),
            "oa_url": openalex.get("oa_url", ""),
            "oa_status": openalex.get("oa_status", ""),
            "direction": direction,
            "method_tags": method_tags,
            "overview_sentence": overview_sentence,
            "note": {
                "overview": overview_sentence and f"这篇工作首先强调：{overview_sentence}" or f"从标题看，它主要落在“{direction}”方向。",
                "method": method_sentence and f"方法线上更接近 {' / '.join(method_tags) or '该方向常见技术'}。{method_sentence}" or theory_hint(abstract),
                "application": {
                    "机械臂操控": "更偏向抓取、装配、接触丰富操作等真实机械臂任务。",
                    "触觉与接触感知": "更适合需要触觉闭环、滑移检测和精细接触判断的系统。",
                    "足式与人形运动": "更适合行走、跑跳、抗扰和平衡恢复等运动控制问题。",
                    "导航与规划": "更适合长时序任务编排、复杂场景导航和系统级决策。",
                    "仿真到真实迁移": "更适合把仿真中的策略稳定迁移到真实机器人平台。",
                    "大模型机器人系统": "更适合任务理解、技能编排和机器人代理框架。",
                    "手术机器人": "更偏向高约束、高风险、高价值的垂直机器人场景。",
                }.get(direction, "对机器人系统设计、实验选题和工程落地都有一定参考价值。"),
                "reading": openalex.get("oa_url") and "有开放获取入口，手机深读成本相对更低。" or (abstract and "建议先看我整理的小文，再决定是否跳原文。") or "当前更适合作为题目筛选项，先看小文，不建议直接跳原文。",
            },
        }
    )
    return item


def enrich_repo_item(item: dict[str, Any], headers: dict[str, str], keyword_weights: dict[str, int]) -> dict[str, Any]:
    repo_details = fetch_repo_page_details(item["repo"], headers)
    description = repo_details.get("description") or item.get("description") or ""
    readme_excerpt = repo_details.get("readme_excerpt", "")
    topics = repo_details.get("topics", [])
    combined = " ".join([item.get("repo", ""), description, " ".join(topics), readme_excerpt]).lower()
    score = 0
    hits: list[str] = []
    for keyword, weight in keyword_weights.items():
        if keyword_in_text(combined, keyword):
            score += weight
            hits.append(keyword)
    relevance_label = "直接相关" if any(keyword_in_text(combined, k) for k in ("robot", "robotics", "embodied", "grasp", "locomotion", "sim2real", "humanoid", "ros", "ros2", "gazebo", "moveit", "isaac", "mujoco", "pinocchio")) else ("中度相关" if score >= 3 else "弱相关")
    use_mode = "更像工具链/基础设施" if any(keyword_in_text(combined, k) for k in ("tool", "library", "sdk", "parser", "converter", "framework", "middleware", "architecture", "pipeline")) else ("更像基准/数据资源" if any(keyword_in_text(combined, k) for k in ("benchmark", "dataset", "leaderboard")) else ("更像 agent 范式参考" if any(keyword_in_text(combined, k) for k in ("agent", "assistant", "copilot")) else "更像灵感源或通用工程参考"))
    stars_today = int(item.get("stars_today") or "0")
    item.update(
        {
            "description": description,
            "readme_excerpt": readme_excerpt,
            "topics": topics,
            "relevance_score": score,
            "keyword_hits": hits,
            "relevance_label": relevance_label,
            "use_mode": use_mode,
            "note": {
                "overview": description or "项目公开描述较少，目前只能从仓库名和热度判断定位。",
                "why_trending": (stars_today >= 5000 and f"今天是明显爆发态热度，新增 {stars_today} star。") or (stars_today >= 1500 and f"今天热度很高，新增 {stars_today} star。") or f"今天有一定增长，新增 {stars_today} star。",
                "robotics_value": "对机器人研究是直接可复用的主线资源。" if relevance_label == "直接相关" else ("对机器人研究更像通用工具或基础设施补充。" if relevance_label == "中度相关" else "对机器人主线方法的直接帮助较弱，更适合作为通用工程参考。"),
                "reading": f"建议把它当作“{use_mode}”来看，先看小文，再决定要不要进 GitHub 深挖。",
            },
        }
    )
    return item


def assign_report_paths(report: dict[str, Any]) -> None:
    date_slug = report["reference_date"]
    report["daily_relpath"] = f"daily/{date_slug}/index.html"
    for index, item in enumerate(report.get("papers", []), start=1):
        item["slug"] = f"paper-{index:02d}-{slugify(item['title'])}"
        item["detail_relpath"] = f"daily/{date_slug}/papers/{item['slug']}.html"
    for index, item in enumerate(report.get("repos", []), start=1):
        item["slug"] = f"repo-{index:02d}-{slugify(item['repo'].replace('/', '-'))}"
        item["detail_relpath"] = f"daily/{date_slug}/repos/{item['slug']}.html"


def build_markdown_digest(report: dict[str, Any], public_base_url: str) -> str:
    lines = [
        f"# 机器人具身智能日报 - {report['reference_date']}",
        "",
        f"- 统计窗口: {report['window_start']} 至 {report['reference_date']}",
        f"- 生成时间: {report['generated_at']}",
        f"- 论文数: {len(report['papers'])}",
        f"- GitHub 热点仓库数: {len(report['repos'])}",
    ]
    daily_url = join_url(public_base_url, report["daily_relpath"])
    if daily_url:
        lines.extend(["", f"- 每日详情页: {daily_url}"])
    lines.append("")

    lines.extend(["## 论文速读", ""])
    if not report["papers"]:
        lines.extend(["- 无命中结果。", ""])
    else:
        for index, item in enumerate(report["papers"], start=1):
            lines.extend(
                [
                    f"### {index}. {item['title']}",
                    f"- 方向: {item['direction']}",
                    f"- 证据等级: {evidence_label(item)}",
                    f"- 内容: {item['note']['overview']}",
                    f"- 理论: {item['note']['method']}",
                    f"- 应用: {item['note']['application']}",
                    f"- 阅读建议: {item['note']['reading']}",
                    f"- 小文: {join_url(public_base_url, item['detail_relpath']) or item['detail_relpath']}",
                    f"- 原始来源: {item.get('oa_url') or item.get('url') or item.get('source_homepage') or '无'}",
                    "",
                ]
            )

    lines.extend(["## GitHub 项目速读", ""])
    if not report["repos"]:
        lines.extend(["- 无命中结果。", ""])
    else:
        for index, item in enumerate(report["repos"], start=1):
            lines.extend(
                [
                    f"### {index}. {item['repo']}",
                    f"- 相关性: {item['relevance_label']}（分数 {item['relevance_score']}）",
                    f"- 定位: {item['note']['overview']}",
                    f"- 热度判断: {item['note']['why_trending']}",
                    f"- 可用点: {item['note']['robotics_value']}",
                    f"- 使用姿势: {item['note']['reading']}",
                    f"- 小文: {join_url(public_base_url, item['detail_relpath']) or item['detail_relpath']}",
                    f"- 原始来源: {item.get('url') or '无'}",
                    "",
                ]
            )
    return "\n".join(lines)


def build_mobile_digest(report: dict[str, Any], public_base_url: str, paper_limit: int, repo_limit: int) -> str:
    lines = [f"# 今日机器人快报 {report['reference_date']}", ""]
    daily_url = join_url(public_base_url, report["daily_relpath"])
    if daily_url:
        lines.extend([f"先看总览小文: [今日详情页]({daily_url})", ""])

    lines.extend(["## 论文", ""])
    papers = report["papers"][:paper_limit]
    if not papers:
        lines.extend(["- 今日没有命中高相关论文。", ""])
    else:
        for index, item in enumerate(papers, start=1):
            source_url = item.get("oa_url") or item.get("url") or item.get("source_homepage") or ""
            lines.extend(
                [
                    f"{index}. {shorten(item['title'], 92)}",
                    f"- 内容: {shorten(item['note']['overview'], 88)}",
                    f"- 理论: {shorten(item['note']['method'], 88)}",
                    f"- 应用: {shorten(item['note']['application'], 70)}",
                    f"- 小文: [手机解读]({join_url(public_base_url, item['detail_relpath'])})" + (f" | [原始来源]({source_url})" if source_url else ""),
                ]
            )
        lines.append("")

    lines.extend(["## GitHub 项目", ""])
    repos = report["repos"][:repo_limit]
    if not repos:
        lines.extend(["- 今日没有命中高相关 GitHub 项目。", ""])
    else:
        for index, item in enumerate(repos, start=1):
            lines.extend(
                [
                    f"{index}. {item['repo']}",
                    f"- 定位: {shorten(item['note']['overview'], 88)}",
                    f"- 可用点: {shorten(item['note']['robotics_value'], 70)}",
                    f"- 建议: {shorten(item['note']['reading'], 70)}",
                    f"- 小文: [手机解读]({join_url(public_base_url, item['detail_relpath'])})" + (f" | [源地址]({item['url']})" if item.get('url') else ""),
                ]
            )
        lines.append("")

    lines.append("推送里优先给出我整理过的内容，原始论文站点和 GitHub 只作为二跳入口。")
    return "\n".join(lines)


def _link_row(items: list[tuple[str, str]]) -> str:
    items = [(label, url) for label, url in items if url]
    if not items:
        return ""
    return '<div class="links">' + "".join(f'<a href="{escape(url)}">{escape(label)}</a>' for label, url in items) + "</div>"


def _tag_row(tags: list[str]) -> str:
    tags = [tag for tag in tags if tag]
    if not tags:
        return ""
    return '<div class="tags">' + "".join(f'<span class="tag">{escape(tag)}</span>' for tag in tags) + "</div>"


def _page(title: str, eyebrow: str, lead: str, body: str, css_relpath: str) -> str:
    return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)}</title><link rel="stylesheet" href="{escape(css_relpath)}"></head><body><main class="page"><header class="hero"><div class="eyebrow">{escape(eyebrow)}</div><h1>{escape(title)}</h1><p class="lead">{escape(lead)}</p></header>{body}</main></body></html>'


def _paper_entry(item: dict[str, Any], detail_href: str) -> str:
    quote = item.get("overview_sentence") and f'<div class="quote">摘要摘录：{escape(shorten(item["overview_sentence"], 240))}</div>' or ""
    return (
        '<article class="entry">'
        f'<div class="pill">Paper · {escape(item["direction"])}</div><h2><a href="{escape(detail_href)}">{escape(item["title"])}</a></h2>'
        f'<div class="meta"><span>{escape(item.get("venue", ""))}</span><span>{escape(item.get("published", "未知"))}</span><span>{escape(evidence_label(item))}</span></div>'
        '<div class="grid">'
        f'<div class="block"><span class="k">内容</span>{escape(item["note"]["overview"])}</div>'
        f'<div class="block"><span class="k">理论</span>{escape(item["note"]["method"])}</div>'
        f'<div class="block"><span class="k">应用</span>{escape(item["note"]["application"])}</div>'
        '</div>'
        f'{_tag_row(item.get("method_tags", []) + item.get("concepts", [])[:3])}{quote}'
        f'{_link_row([("看我整理的小文", detail_href), ("开放获取/原始来源", item.get("oa_url") or item.get("url") or item.get("source_homepage") or "")])}'
        '</article>'
    )


def _repo_entry(item: dict[str, Any], detail_href: str) -> str:
    quote = item.get("readme_excerpt") and f'<div class="quote">README 摘录：{escape(shorten(item["readme_excerpt"], 260))}</div>' or ""
    return (
        '<article class="entry">'
        f'<div class="pill">Repo · {escape(item["relevance_label"])}</div><h2><a href="{escape(detail_href)}">{escape(item["repo"])}</a></h2>'
        f'<div class="meta"><span>{escape(item.get("language", "未知"))}</span><span>+{escape(str(item.get("stars_today", "0")))} today</span><span>score {escape(str(item.get("relevance_score", 0)))}</span></div>'
        '<div class="grid">'
        f'<div class="block"><span class="k">定位</span>{escape(item["note"]["overview"])}</div>'
        f'<div class="block"><span class="k">可用点</span>{escape(item["note"]["robotics_value"])}</div>'
        f'<div class="block"><span class="k">建议</span>{escape(item["note"]["reading"])}</div>'
        '</div>'
        f'{_tag_row(item.get("topics", [])[:4] + item.get("keyword_hits", [])[:3])}{quote}'
        f'{_link_row([("看我整理的小文", detail_href), ("源地址", item.get("url") or "")])}'
        '</article>'
    )


def write_site(report: dict[str, Any], site_dir: Path) -> None:
    daily_dir = site_dir / "daily" / report["reference_date"]
    papers_dir = daily_dir / "papers"
    repos_dir = daily_dir / "repos"
    papers_dir.mkdir(parents=True, exist_ok=True)
    repos_dir.mkdir(parents=True, exist_ok=True)
    (site_dir / "assets").mkdir(parents=True, exist_ok=True)
    (site_dir / "assets" / "style.css").write_text(SITE_CSS, encoding="utf-8")
    (site_dir / ".nojekyll").write_text("", encoding="utf-8")

    papers_html = "".join(_paper_entry(item, f'papers/{item["slug"]}.html') for item in report["papers"]) or '<p class="entry">今天没有命中高相关论文。</p>'
    repos_html = "".join(_repo_entry(item, f'repos/{item["slug"]}.html') for item in report["repos"]) or '<p class="entry">今天没有命中高相关 GitHub 项目。</p>'
    daily_page = _page(
        f"{report['reference_date']} 机器人日报",
        "Daily Digest",
        "先看我帮你消化过的内容，再决定要不要跳原始论文站点或 GitHub。",
        f'<section class="section"><h2>论文</h2>{papers_html}</section><section class="section"><h2>GitHub 项目</h2>{repos_html}</section>',
        "../../assets/style.css",
    )
    (daily_dir / "index.html").write_text(daily_page, encoding="utf-8")
    (daily_dir / "meta.json").write_text(json.dumps({"reference_date": report["reference_date"], "paper_count": len(report["papers"]), "repo_count": len(report["repos"]), "top_paper": report["papers"][0]["title"] if report["papers"] else "", "top_repo": report["repos"][0]["repo"] if report["repos"] else "", "relpath": report["daily_relpath"]}, ensure_ascii=False, indent=2), encoding="utf-8")

    for item in report["papers"]:
        paper_tags = _tag_row(item.get("method_tags", []) + item.get("concepts", [])[:4])
        paper_links = _link_row([
            ("开放获取/原始来源", item.get("oa_url") or item.get("url") or item.get("source_homepage") or ""),
            ("DOI", item.get("doi") and f"https://doi.org/{item['doi']}" or ""),
        ])
        paper_quote = item.get("overview_sentence") and f'<div class="quote">摘要摘录：{escape(shorten(item["overview_sentence"], 420))}</div>' or ""
        paper_body = (
            f'<section class="section"><a class="back" href="../index.html">← 回到当日日报</a>'
            f'<div class="facts"><div class="fact"><div>期刊</div><div>{escape(item.get("venue", ""))}</div></div>'
            f'<div class="fact"><div>日期</div><div>{escape(item.get("published", "未知"))}</div></div>'
            f'<div class="fact"><div>证据等级</div><div>{escape(evidence_label(item))}</div></div></div>'
            f'{paper_tags}{paper_links}</section>'
            f'<section class="section"><h2>我先帮你看</h2><p>{escape(item["note"]["overview"])}</p><p>{escape(item["note"]["application"])}</p><p>{escape(item["note"]["reading"])}</p></section>'
            f'<section class="section"><h2>理论线索</h2><p>{escape(item["note"]["method"])}</p>{paper_quote}</section>'
        )
        detail = _page(
            item["title"],
            f'Paper · {item["direction"]}',
            "这是面向手机深读前筛选的小文页：先看方向、方法、应用和证据等级，再决定是否跳原文。",
            paper_body,
            "../../../assets/style.css",
        )
        (papers_dir / f'{item["slug"]}.html').write_text(detail, encoding="utf-8")

    for item in report["repos"]:
        repo_tags = _tag_row(item.get("topics", [])[:6] + item.get("keyword_hits", [])[:4])
        repo_links = _link_row([("源地址", item.get("url") or "")])
        repo_quote = item.get("readme_excerpt") and f'<div class="quote">README 摘录：{escape(shorten(item["readme_excerpt"], 680))}</div>' or ""
        repo_body = (
            f'<section class="section"><a class="back" href="../index.html">← 回到当日日报</a>'
            f'<div class="facts"><div class="fact"><div>语言</div><div>{escape(item.get("language", "未知"))}</div></div>'
            f'<div class="fact"><div>今日新增 Star</div><div>{escape(str(item.get("stars_today", "0")))}</div></div>'
            f'<div class="fact"><div>相关性</div><div>{escape(item.get("relevance_label", ""))}</div></div></div>'
            f'{repo_tags}{repo_links}</section>'
            f'<section class="section"><h2>我先帮你看</h2><p>{escape(item["note"]["overview"])}</p><p>{escape(item["note"]["robotics_value"])}</p><p>{escape(item["note"]["reading"])}</p></section>'
            f'<section class="section"><h2>热度判断</h2><p>{escape(item["note"]["why_trending"])}</p>{repo_quote}</section>'
        )
        detail = _page(
            item["repo"],
            f'Repo · {item["relevance_label"]}',
            "这是一页为手机阅读准备的仓库小文：先看它在做什么、为什么热、对机器人研究是否真有用。",
            repo_body,
            "../../../assets/style.css",
        )
        (repos_dir / f'{item["slug"]}.html').write_text(detail, encoding="utf-8")

    metas = []
    for meta_path in sorted((site_dir / "daily").glob("*/meta.json"), reverse=True):
        try:
            metas.append(json.loads(meta_path.read_text(encoding="utf-8")))
        except Exception:
            continue
    entry_chunks = []
    for meta in metas:
        summary = f"论文 {meta['paper_count']} 条，项目 {meta['repo_count']} 条。最值得先看的是：{meta.get('top_paper') or meta.get('top_repo') or '暂无'}"
        entry_chunks.append(
            f'<article class="entry"><div class="pill">{escape(meta["reference_date"])}</div>'
            f'<h2><a href="{escape(meta["relpath"])}">{escape(meta["reference_date"])} 的手机小文合集</a></h2>'
            f'<p>{escape(summary)}</p><div class="links"><a href="{escape(meta["relpath"])}">打开当日日报</a></div></article>'
        )
    index_entries = "".join(entry_chunks) or '<p class="entry">还没有归档日报。</p>'
    index_page = _page("机器人每日小文库", "Mobile Knowledge Layer", "推送只发浓缩摘要，真正适合手机阅读的每条论文和项目小文都存放在这里。", f'<section class="section"><h2>按日期查看每日小文</h2>{index_entries}</section>', "assets/style.css")
    (site_dir / "index.html").write_text(index_page, encoding="utf-8")
