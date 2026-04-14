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
:root{
  --bg:#f5efe4;
  --panel:#fffaf3;
  --panel-strong:#fffdf9;
  --ink:#1f1a16;
  --muted:#6a6158;
  --line:#dbcdbb;
  --accent:#9f4d29;
  --accent-soft:#f1dfcf;
  --shadow:0 18px 60px rgba(55,39,22,.09);
  --max:1100px
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0;
  color:var(--ink);
  background:
    radial-gradient(circle at top left, rgba(255,255,255,.92), transparent 35%),
    linear-gradient(180deg, #f9f5ee 0%, #f2eadf 45%, #efe6d9 100%);
  font:16px/1.75 "PingFang SC","Noto Sans SC","Segoe UI",sans-serif
}
.page{width:min(calc(100% - 28px),var(--max));margin:0 auto;padding:24px 0 72px}
.hero{
  padding:28px 24px 26px;
  background:linear-gradient(135deg, rgba(255,255,255,.86), rgba(255,248,240,.88));
  border:1px solid rgba(219,205,187,.95);
  border-radius:28px;
  box-shadow:var(--shadow);
  margin-bottom:22px
}
.eyebrow{
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding:6px 12px;
  background:var(--accent-soft);
  color:var(--accent);
  border-radius:999px;
  font-size:12px;
  letter-spacing:.08em;
  text-transform:uppercase;
  margin-bottom:14px
}
.eyebrow::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--accent)}
h1,h2,h3{font-family:"Source Han Serif SC","Songti SC","Noto Serif SC","Georgia",serif;line-height:1.14;margin:0}
h1{font-size:clamp(30px,7vw,58px);letter-spacing:-.03em}
h2{font-size:clamp(24px,4vw,34px);letter-spacing:-.02em}
h3{font-size:20px}
.lead{max-width:52rem;color:var(--muted);margin:14px 0 0}
.summary-strip{display:grid;gap:12px;margin-top:18px}
.summary-item{display:grid;grid-template-columns:110px 1fr;gap:10px;padding:12px 0;border-top:1px dashed var(--line)}
.summary-item:first-child{border-top:0}
.summary-k{font-size:12px;color:var(--accent);text-transform:uppercase;letter-spacing:.08em}
.section{margin-top:18px}
.section-head{display:flex;flex-wrap:wrap;align-items:end;justify-content:space-between;gap:12px;margin-bottom:14px}
.section-note{color:var(--muted);font-size:14px}
.stack{display:grid;gap:16px}
.entry{background:rgba(255,252,247,.96);border:1px solid rgba(219,205,187,.92);border-radius:24px;box-shadow:var(--shadow);padding:20px 18px}
.pill,.tag{display:inline-flex;align-items:center;padding:5px 10px;border-radius:999px;border:1px solid var(--line);font-size:12px}
.pill{background:var(--accent-soft);border-color:#e0c1a8;color:var(--accent);margin-bottom:10px}
.tag{background:#f7f0e6;color:#52473e}
.meta,.tags,.links{display:flex;flex-wrap:wrap;gap:10px 12px;color:var(--muted);font-size:14px}
.meta{margin:10px 0 12px}
.grid{display:grid;gap:12px;margin-top:12px}
.block{padding:14px 14px 12px;border-radius:18px;background:var(--panel);border:1px solid rgba(219,205,187,.85)}
.k{display:block;color:var(--accent);font-size:12px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px}
.quote{margin-top:14px;padding:14px 16px;border-left:3px solid var(--accent);border-radius:0 18px 18px 0;background:rgba(255,255,255,.7);color:var(--muted)}
.links{margin-top:14px}
.links a,.back{color:#8b3d1f;font-weight:700;text-decoration:none}
.links a:hover,.back:hover{text-decoration:underline}
.detail-card{background:rgba(255,252,247,.96);border:1px solid rgba(219,205,187,.92);border-radius:24px;box-shadow:var(--shadow);padding:20px 18px;margin-top:18px}
.detail-card h2{margin-bottom:12px}
.detail-card p{margin:0 0 10px}
.detail-card p:last-child{margin-bottom:0}
.back{display:inline-block;margin-top:6px}
.footnote{margin-top:14px;font-size:13px;color:var(--muted)}
.empty{background:rgba(255,252,247,.96);border:1px dashed var(--line);border-radius:22px;padding:18px;color:var(--muted)}
@media(min-width:820px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
"""

PAPER_DIRECTION_RULES = [
    (("manipulation", "grasp", "gripper", "contact"), "机械臂操控"),
    (("tactile", "touch", "visuotactile"), "触觉与接触感知"),
    (("locomotion", "humanoid", "legged", "biped", "quadruped", "gait"), "足式与人形运动"),
    (("navigation", "planning", "slam"), "导航与规划"),
    (("sim2real", "simulation", "sim-to-real"), "仿真到真实迁移"),
    (("language model", "llm", "agent", "ros"), "大模型机器人系统"),
    (("surgical", "surgery"), "手术机器人"),
]

METHOD_RULES = [
    (("reinforcement learning", "policy optimization", "actor-critic"), "强化学习"),
    (("transformer",), "Transformer"),
    (("diffusion",), "扩散模型"),
    (("constraint", "constrained"), "约束建模"),
    (("sim2real", "domain randomization", "sim-to-real"), "Sim2Real"),
    (("tactile", "touch"), "触觉反馈"),
    (("world model",), "世界模型"),
    (("retrieval", "rag"), "检索增强"),
    (("language model", "llm"), "语言模型"),
    (("geometry", "depth"), "几何/深度估计"),
    (("mpc", "model predictive"), "MPC"),
]

PAPER_FOCUS_RULES = [
    (("transparent", "depth completion"), "透明物体感知与抓取"),
    (("clay", "deformable"), "可变形物体操作"),
    (("radar", "mmwave"), "雷达感知与点云增强"),
    (("tactile", "touch"), "触觉感知闭环"),
    (("humanoid", "legged"), "人形/足式运动控制"),
    (("navigation", "planning", "slam"), "导航规划与场景决策"),
    (("world model", "language model", "agent"), "高层任务理解与技能编排"),
]

REPO_DOMAIN_RULES = [
    (("ros2", "ros", "middleware", "pipeline"), "机器人中间件/系统集成"),
    (("simulation", "gazebo", "isaac", "mujoco"), "仿真平台或训练环境"),
    (("moveit", "planning", "trajectory"), "运动规划与执行"),
    (("grasp", "manipulation"), "抓取与机械臂操作"),
    (("humanoid", "locomotion"), "足式/人形控制"),
    (("dataset", "benchmark"), "数据集或基准"),
    (("vision", "perception", "slam"), "感知与建图"),
]

SENTENCE_REPLACEMENTS = [
    (r"\bthis paper\b", "本文"),
    (r"\bthis work\b", "这项工作"),
    (r"\bwe propose\b", "作者提出"),
    (r"\bwe present\b", "作者提出"),
    (r"\bwe introduce\b", "作者提出"),
    (r"\bwe develop\b", "作者设计了"),
    (r"\bwe design\b", "作者设计了"),
    (r"\bwe demonstrate\b", "作者验证了"),
    (r"\bwe show\b", "结果表明"),
    (r"\bresults show that\b", "结果表明"),
    (r"\boutperform(s|ed)?\b", "优于"),
    (r"\bachieve(s|d)?\b", "达到"),
    (r"\benable(s|d)?\b", "使得"),
    (r"\brobotic grasping\b", "机器人抓取"),
    (r"\brobot grasping\b", "机器人抓取"),
    (r"\bdepth completion\b", "深度补全"),
    (r"\bmonocular depth estimation\b", "单目深度估计"),
    (r"\bpoint cloud enhancement\b", "点云增强"),
    (r"\bpoint cloud\b", "点云"),
    (r"\brange image(s)?\b", "距离图"),
    (r"\bdiffusion-based\b", "基于扩散模型的"),
    (r"\btransformer-based\b", "基于 Transformer 的"),
    (r"\breinforcement learning\b", "强化学习"),
    (r"\bpolicy\b", "策略"),
    (r"\bcontroller\b", "控制器"),
    (r"\bobjective\b", "目标函数"),
    (r"\bloss\b", "损失"),
    (r"\bconstraint(s)?\b", "约束"),
    (r"\bdynamics\b", "动力学"),
    (r"\bkinematics\b", "运动学"),
    (r"\bsimulation\b", "仿真"),
    (r"\breal-world\b", "真实世界"),
    (r"\breal robot\b", "真实机器人"),
    (r"\bbenchmark\b", "基准"),
    (r"\bdataset\b", "数据集"),
]


def compact_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def keyword_in_text(text: str, keyword: str) -> bool:
    if not text or not keyword:
        return False
    return bool(re.search(rf"(?<![a-z0-9]){re.escape(keyword.lower())}(?![a-z0-9])", text.lower()))


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
    raw_parts = re.split(r"(?<=[.!?])\s+", compact_whitespace(text))
    return [compact_whitespace(part) for part in raw_parts if compact_whitespace(part)]


def pick_sentence(text: str, keywords: tuple[str, ...]) -> str:
    for sentence in select_sentences(text):
        lowered = sentence.lower()
        if any(keyword in lowered for keyword in keywords):
            return sentence
    return ""


def english_ratio(text: str) -> float:
    if not text:
        return 0.0
    ascii_letters = sum(1 for char in text if char.isascii() and char.isalpha())
    chinese_chars = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")
    total = ascii_letters + chinese_chars
    if total == 0:
        return 0.0
    return ascii_letters / total


def localize_sentence(text: str) -> str:
    text = compact_whitespace(text)
    if not text:
        return ""
    localized = text
    for pattern, replacement in SENTENCE_REPLACEMENTS:
        localized = re.sub(pattern, replacement, localized, flags=re.I)
    localized = localized.replace(";", "；").replace(":", "：")
    localized = re.sub(r"\s+", " ", localized)
    if english_ratio(localized) > 0.68:
        return ""
    return localized


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
        best_oa = item.get("best_oa_location") or {}
        primary = item.get("primary_location") or {}
        open_access = item.get("open_access") or {}
        return {
            "abstract": reconstruct_openalex_abstract(item.get("abstract_inverted_index")),
            "cited_by_count": item.get("cited_by_count"),
            "primary_topic": (item.get("primary_topic") or {}).get("display_name", ""),
            "concepts": [entry.get("display_name", "") for entry in item.get("concepts", [])[:6] if entry.get("display_name")],
            "oa_url": open_access.get("oa_url") or best_oa.get("landing_page_url") or primary.get("landing_page_url") or "",
            "pdf_url": best_oa.get("pdf_url") or primary.get("pdf_url") or "",
            "oa_status": open_access.get("oa_status") or "",
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
        details["readme_excerpt"] = shorten(strip_html_to_text(readme_match.group(1)), 1200)

    topic_matches = re.findall(r'/topics/[^"]+"[^>]*>([^<]+)</a>', html, re.I)
    if topic_matches:
        details["topics"] = [compact_whitespace(unescape(item)) for item in topic_matches[:10]]
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


def infer_focus(text: str, direction: str) -> str:
    lowered = text.lower()
    for keywords, label in PAPER_FOCUS_RULES:
        if any(keyword in lowered for keyword in keywords):
            return label
    return direction


def evidence_label(item: dict[str, Any]) -> str:
    if item.get("abstract"):
        return "摘要支持"
    return "仅标题/元数据"


def build_theory_axes(text: str, method_tags: list[str]) -> list[str]:
    lowered = text.lower()
    axes: list[str] = []
    if any(token in lowered for token in ("objective", "loss", "optimiz")):
        axes.append("目标函数或损失设计")
    if any(token in lowered for token in ("constraint", "constrained")):
        axes.append("约束建模")
    if any(token in lowered for token in ("dynamic", "kinematic", "geometry", "depth", "contact")):
        axes.append("动力学/几何结构")
    if any(token in lowered for token in ("policy", "controller", "control")):
        axes.append("策略或控制律")
    if any(token in lowered for token in ("world model", "latent", "state")):
        axes.append("状态表征或世界模型")
    if any(token in lowered for token in ("diffusion", "transformer")):
        axes.append("生成式序列建模")
    if not axes and method_tags:
        axes.extend(method_tags[:2])
    return axes[:3]


def infer_experiment_summary(abstract: str) -> str:
    lowered = abstract.lower()
    pieces: list[str] = []
    if any(token in lowered for token in ("real robot", "real-world", "hardware")):
        pieces.append("包含真实机器人或真实环境验证")
    if any(token in lowered for token in ("simulation", "simulated")):
        pieces.append("含仿真实验")
    if any(token in lowered for token in ("benchmark", "dataset")):
        pieces.append("在公开基准或数据集上评估")
    if any(token in lowered for token in ("ablation", "analysis")):
        pieces.append("做了消融或分析实验")
    if pieces:
        return "；".join(pieces) + "。"
    return "摘要没有展开完整实验表，但可以确认作者至少做了方法有效性验证。"


def infer_result_summary(abstract: str) -> str:
    sentence = pick_sentence(
        abstract,
        ("outperform", "improve", "achieve", "demonstrate", "show", "effective", "state-of-the-art"),
    )
    localized = localize_sentence(sentence)
    if localized:
        return f"结果层面，{localized}"
    if sentence:
        return "结果层面，摘要声称方法在指标或任务完成度上有明显提升。"
    return "结果层面，公开摘要没有给出足够细节，适合先把它当作值得复查的候选。"


def build_access_note(item: dict[str, Any]) -> str:
    if item.get("pdf_url"):
        return "已找到合法开放 PDF，可直接从详情页跳转。"
    if item.get("oa_url"):
        return "已找到合法开放获取入口，手机可直接阅读。"
    return "当前未发现合法开放全文，只保留 DOI/期刊页等正规入口。"


def build_reading_note(item: dict[str, Any]) -> str:
    if item.get("pdf_url") or item.get("oa_url"):
        return "建议先看小文中的主旨、方法和实验，再决定是否进入原文或 PDF。"
    return "建议先把这篇论文当成选题线索，小文足够帮助你判断要不要进一步找全文。"


def theory_hint(abstract: str, method_tags: list[str]) -> str:
    theory_sentence = pick_sentence(
        abstract,
        ("objective", "loss", "constraint", "dynamic", "model", "policy", "controller", "diffusion", "transformer"),
    )
    localized = localize_sentence(theory_sentence)
    axes = build_theory_axes(abstract, method_tags)
    axis_text = "、".join(axes) if axes else "方法框架"
    if localized:
        return f"理论线索主要落在{axis_text}上；摘要中明确提到：{localized}"
    if abstract:
        return f"公开摘要没有展开完整公式，但可以确认作者的理论抓手主要围绕{axis_text}。"
    return "目前只有标题和元数据，无法负责任地还原具体推导，只能保留研究方向判断。"


def build_paper_overview(direction: str, focus: str, abstract: str) -> str:
    sentence = localize_sentence(select_sentences(abstract)[0] if abstract else "")
    if sentence:
        return f"主旨上，这篇论文聚焦{focus}，摘要开头直接指出：{sentence}"
    return f"主旨上，这篇论文主要落在“{direction}”方向，更具体地说是在处理{focus}。"


def build_method_summary(method_tags: list[str], abstract: str) -> str:
    method_sentence = pick_sentence(
        abstract,
        ("propose", "present", "introduce", "framework", "method", "approach", "policy", "objective", "controller"),
    )
    localized = localize_sentence(method_sentence)
    tag_text = "、".join(method_tags) if method_tags else "问题建模 + 感知/控制联合设计"
    if localized:
        return f"方法上，作者主要采用{tag_text}路线；摘要里最关键的一句是：{localized}"
    return f"方法上，这篇工作更接近{tag_text}路线，但公开摘要没有把实现细节展开到可直接复现的程度。"


def direction_application(direction: str) -> str:
    return {
        "机械臂操控": "更偏向抓取、装配、接触丰富操作和机械臂精细执行。",
        "触觉与接触感知": "更适合需要触觉闭环、滑移检测和精细接触判断的系统。",
        "足式与人形运动": "更适合步态生成、平衡恢复、动态控制和抗扰运动。",
        "导航与规划": "更适合长时序任务编排、复杂场景导航和系统级决策。",
        "仿真到真实迁移": "更适合把仿真中的策略稳定迁移到真实机器人平台。",
        "大模型机器人系统": "更适合任务理解、技能编排和机器人代理框架。",
        "手术机器人": "更偏向高约束、高风险、高价值的垂直机器人场景。",
    }.get(direction, "对机器人系统设计、实验选题和工程落地都有一定参考价值。")


def enrich_paper_item(item: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    openalex = fetch_openalex_metadata(item.get("doi", ""), headers)
    abstract = item.get("abstract") or openalex.get("abstract") or ""
    analysis_text = " ".join(
        [
            item.get("title", ""),
            abstract,
            openalex.get("primary_topic", ""),
            " ".join(openalex.get("concepts", [])),
        ]
    )
    direction = infer_paper_direction(analysis_text)
    focus = infer_focus(analysis_text, direction)
    method_tags = infer_method_tags(analysis_text)
    summary_cn = f"这篇论文关注{focus}，方法路线偏向{'、'.join(method_tags) if method_tags else direction}。"

    item.update(
        {
            "abstract": abstract,
            "cited_by_count": openalex.get("cited_by_count"),
            "primary_topic": openalex.get("primary_topic", ""),
            "concepts": openalex.get("concepts", []),
            "oa_url": openalex.get("oa_url") or item.get("oa_url", ""),
            "pdf_url": openalex.get("pdf_url") or item.get("pdf_url", ""),
            "oa_status": openalex.get("oa_status", item.get("oa_status", "")),
            "direction": direction,
            "focus": focus,
            "method_tags": method_tags,
            "overview_sentence": select_sentences(abstract)[0] if abstract else "",
            "note": {
                "summary_cn": summary_cn,
                "overview": build_paper_overview(direction, focus, abstract),
                "method": build_method_summary(method_tags, abstract),
                "theory": theory_hint(abstract, method_tags),
                "experiment": infer_experiment_summary(abstract),
                "result": infer_result_summary(abstract),
                "application": direction_application(direction),
                "reading": build_reading_note({**item, **openalex}),
                "access": build_access_note({**item, **openalex}),
            },
        }
    )
    return item


def infer_repo_domain(text: str) -> str:
    lowered = text.lower()
    for keywords, label in REPO_DOMAIN_RULES:
        if any(keyword in lowered for keyword in keywords):
            return label
    return "研究工具链或工程参考"


def build_repo_overview(description: str, domain: str, use_mode: str, topics: list[str]) -> str:
    if description:
        return f"这是一个偏“{domain}”的仓库，从公开描述看更像{use_mode}。核心关键词包括：{', '.join(topics[:3]) or '暂无明确 topic'}。"
    return f"这是一个偏“{domain}”的仓库，目前公开描述较少，更适合先从小文判断是否值得深入。"


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

    relevance_label = (
        "直接相关"
        if any(
            keyword_in_text(combined, keyword)
            for keyword in ("robot", "robotics", "embodied", "grasp", "locomotion", "sim2real", "humanoid", "ros", "ros2", "gazebo", "moveit", "isaac", "mujoco", "pinocchio")
        )
        else ("中度相关" if score >= 3 else "弱相关")
    )
    use_mode = (
        "工具链/基础设施"
        if any(keyword_in_text(combined, keyword) for keyword in ("tool", "library", "sdk", "parser", "converter", "framework", "middleware", "architecture", "pipeline"))
        else ("基准/数据资源" if any(keyword_in_text(combined, keyword) for keyword in ("benchmark", "dataset", "leaderboard")) else ("agent 范式参考" if any(keyword_in_text(combined, keyword) for keyword in ("agent", "assistant", "copilot")) else "工程灵感源"))
    )
    stars_today = int(item.get("stars_today") or "0")
    source_kind = item.get("source_kind", "trending")
    source_note = (
        f"今天在 Trending 里新增 {stars_today} star。"
        if source_kind == "trending"
        else "这不是当天最热的全站 Trending，但它更贴近机器人研究主线，被作为研究向补位推荐。"
    )
    domain = infer_repo_domain(combined)

    item.update(
        {
            "description": description,
            "readme_excerpt": readme_excerpt,
            "topics": topics,
            "relevance_score": score,
            "keyword_hits": hits,
            "relevance_label": relevance_label,
            "use_mode": use_mode,
            "domain": domain,
            "note": {
                "summary_cn": f"这是一个偏{domain}的开源仓库，更像{use_mode}。",
                "overview": build_repo_overview(description, domain, use_mode, topics),
                "why_trending": source_note,
                "robotics_value": "对机器人研究是可直接复用的主线资源。" if relevance_label == "直接相关" else ("对机器人研究更像通用工具或基础设施补充。" if relevance_label == "中度相关" else "对机器人主线方法的直接帮助较弱，更适合作为工程参考。"),
                "integration": f"使用姿势上，建议先把它当作“{use_mode}”来看，重点关注它能不能进入你的训练、仿真、规划或系统集成链路。",
                "reading": "先看小文里的定位、可复用模块和接入位置，再决定要不要进 GitHub 深挖。",
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
        f"# 具身智能日报 - {report['reference_date']}",
        "",
        f"- 统计窗口: {report['window_start']} 至 {report['reference_date']}",
        f"- 生成时间: {report['generated_at']}",
        f"- 论文数: {len(report['papers'])}",
        f"- GitHub 项目数: {len(report['repos'])}",
    ]
    daily_url = join_url(public_base_url, report["daily_relpath"])
    if daily_url:
        lines.extend(["", f"- 每日详情页: {daily_url}"])
    lines.append("")

    lines.extend(["## 论文速读", ""])
    if not report["papers"]:
        lines.extend(["- 今日没有命中论文。", ""])
    else:
        for index, item in enumerate(report["papers"], start=1):
            access_url = item.get("pdf_url") or item.get("oa_url") or item.get("url") or item.get("source_homepage") or ""
            lines.extend(
                [
                    f"### {index}. {item['title']}",
                    f"- 期刊: {item.get('venue', '未知')}",
                    f"- 研究主旨: {item['note']['overview']}",
                    f"- 方法抓手: {item['note']['method']}",
                    f"- 理论线索: {item['note']['theory']}",
                    f"- 实验与结果: {item['note']['experiment']} {item['note']['result']}",
                    f"- 为什么值得看: {item['note']['application']}",
                    f"- 合法获取: {item['note']['access']}",
                    f"- 小文: {join_url(public_base_url, item['detail_relpath']) or item['detail_relpath']}",
                    f"- 原始入口: {access_url or '暂无'}",
                    "",
                ]
            )

    lines.extend(["## GitHub 项目速读", ""])
    if not report["repos"]:
        lines.extend(["- 今日没有命中项目。", ""])
    else:
        for index, item in enumerate(report["repos"], start=1):
            lines.extend(
                [
                    f"### {index}. {item['repo']}",
                    f"- 方向定位: {item['note']['overview']}",
                    f"- 为什么推它: {item['note']['why_trending']}",
                    f"- 机器人价值: {item['note']['robotics_value']}",
                    f"- 接入姿势: {item['note']['integration']}",
                    f"- 小文: {join_url(public_base_url, item['detail_relpath']) or item['detail_relpath']}",
                    f"- 源地址: {item.get('url') or '暂无'}",
                    "",
                ]
            )
    return "\n".join(lines)


def build_mobile_digest(report: dict[str, Any], public_base_url: str, paper_limit: int, repo_limit: int) -> str:
    lines = [f"# 今日具身智能快报 {report['reference_date']}", ""]
    daily_url = join_url(public_base_url, report["daily_relpath"])
    if daily_url:
        lines.extend([f"先看今日总览: [手机详情页]({daily_url})", ""])

    lines.extend(["## 论文", ""])
    papers = report["papers"][:paper_limit]
    if not papers:
        lines.extend(["- 今日没有命中论文。", ""])
    else:
        for index, item in enumerate(papers, start=1):
            access_url = item.get("pdf_url") or item.get("oa_url") or item.get("url") or item.get("source_homepage") or ""
            lines.extend(
                [
                    f"{index}. {shorten(item['title'], 90)}",
                    f"- 主旨: {shorten(item['note']['summary_cn'], 70)}",
                    f"- 方法: {shorten(item['note']['method'], 86)}",
                    f"- 理论: {shorten(item['note']['theory'], 86)}",
                    f"- 实验: {shorten(item['note']['experiment'], 68)}",
                    f"- 小文: [手机解读]({join_url(public_base_url, item['detail_relpath'])})" + (f" | [合法入口]({access_url})" if access_url else ""),
                ]
            )
        lines.append("")

    lines.extend(["## GitHub 项目", ""])
    repos = report["repos"][:repo_limit]
    if not repos:
        lines.extend(["- 今日没有命中项目。", ""])
    else:
        for index, item in enumerate(repos, start=1):
            lines.extend(
                [
                    f"{index}. {item['repo']}",
                    f"- 定位: {shorten(item['note']['summary_cn'], 70)}",
                    f"- 推荐理由: {shorten(item['note']['why_trending'], 72)}",
                    f"- 可用点: {shorten(item['note']['robotics_value'], 72)}",
                    f"- 小文: [手机解读]({join_url(public_base_url, item['detail_relpath'])})" + (f" | [源地址]({item['url']})" if item.get("url") else ""),
                ]
            )
        lines.append("")

    lines.append("推送里优先给出中文小文和判断结论，原始论文站点与 GitHub 只作为二跳入口。")
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
    return (
        "<!doctype html>"
        '<html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{escape(title)}</title>"
        f'<link rel="stylesheet" href="{escape(css_relpath)}"></head>'
        f"<body><main class=\"page\"><header class=\"hero\"><div class=\"eyebrow\">{escape(eyebrow)}</div><h1>{escape(title)}</h1><p class=\"lead\">{escape(lead)}</p></header>{body}</main></body></html>"
    )


def _summary_strip(rows: list[tuple[str, str]]) -> str:
    chunks = [
        f'<div class="summary-item"><div class="summary-k">{escape(label)}</div><div>{escape(value)}</div></div>'
        for label, value in rows
        if value
    ]
    if not chunks:
        return ""
    return '<div class="summary-strip">' + "".join(chunks) + "</div>"


def _paper_entry(item: dict[str, Any], detail_href: str) -> str:
    quote = item.get("overview_sentence") and f'<div class="quote">英文摘要原句：{escape(shorten(item["overview_sentence"], 220))}</div>' or ""
    return (
        '<article class="entry">'
        f'<div class="pill">Paper · {escape(item["direction"])}</div>'
        f'<h2><a href="{escape(detail_href)}">{escape(item["title"])}</a></h2>'
        f'<div class="meta"><span>{escape(item.get("venue", ""))}</span><span>{escape(item.get("published", "未知"))}</span><span>{escape(evidence_label(item))}</span></div>'
        '<div class="grid">'
        f'<div class="block"><span class="k">研究主旨</span>{escape(item["note"]["overview"])}</div>'
        f'<div class="block"><span class="k">方法抓手</span>{escape(item["note"]["method"])}</div>'
        f'<div class="block"><span class="k">理论线索</span>{escape(item["note"]["theory"])}</div>'
        f'<div class="block"><span class="k">实验与结果</span>{escape(item["note"]["experiment"] + " " + item["note"]["result"])}</div>'
        '</div>'
        f'{_tag_row(item.get("method_tags", []) + item.get("concepts", [])[:4])}'
        f'{quote}'
        f'{_link_row([("看中文小文", detail_href), ("合法原文入口", item.get("pdf_url") or item.get("oa_url") or item.get("url") or item.get("source_homepage") or "")])}'
        '</article>'
    )


def _repo_entry(item: dict[str, Any], detail_href: str) -> str:
    quote = item.get("description") and f'<div class="quote">仓库原始描述：{escape(shorten(item["description"], 240))}</div>' or ""
    return (
        '<article class="entry">'
        f'<div class="pill">Repo · {escape(item["relevance_label"])}</div>'
        f'<h2><a href="{escape(detail_href)}">{escape(item["repo"])}</a></h2>'
        f'<div class="meta"><span>{escape(item.get("language", "未知"))}</span><span>{escape(item.get("domain", "研究工具"))}</span><span>score {escape(str(item.get("relevance_score", 0)))}</span></div>'
        '<div class="grid">'
        f'<div class="block"><span class="k">方向定位</span>{escape(item["note"]["overview"])}</div>'
        f'<div class="block"><span class="k">为什么推它</span>{escape(item["note"]["why_trending"])}</div>'
        f'<div class="block"><span class="k">机器人价值</span>{escape(item["note"]["robotics_value"])}</div>'
        f'<div class="block"><span class="k">接入姿势</span>{escape(item["note"]["integration"])}</div>'
        '</div>'
        f'{_tag_row(item.get("topics", [])[:5] + item.get("keyword_hits", [])[:4])}'
        f'{quote}'
        f'{_link_row([("看中文小文", detail_href), ("打开 GitHub", item.get("url") or "")])}'
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

    papers_html = "".join(_paper_entry(item, f'papers/{item["slug"]}.html') for item in report["papers"]) or '<div class="empty">今天没有命中论文。</div>'
    repos_html = "".join(_repo_entry(item, f'repos/{item["slug"]}.html') for item in report["repos"]) or '<div class="empty">今天没有命中 GitHub 项目。</div>'

    daily_body = (
        '<section class="section">'
        '<div class="section-head"><h2>论文小文</h2><div class="section-note">先看主旨、方法、理论线索和实验判断，再决定是否跳原文。</div></div>'
        f'<div class="stack">{papers_html}</div></section>'
        '<section class="section">'
        '<div class="section-head"><h2>GitHub 小文</h2><div class="section-note">Trending 不够相关时，会补进研究向仓库推荐。</div></div>'
        f'<div class="stack">{repos_html}</div></section>'
    )
    daily_page = _page(
        f"{report['reference_date']} 具身智能日报",
        "Daily Digest",
        "这不是原始链接堆砌，而是为手机阅读重写过的中文判断页。",
        daily_body,
        "../../assets/style.css",
    )
    (daily_dir / "index.html").write_text(daily_page, encoding="utf-8")
    (daily_dir / "meta.json").write_text(
        json.dumps(
            {
                "reference_date": report["reference_date"],
                "paper_count": len(report["papers"]),
                "repo_count": len(report["repos"]),
                "top_paper": report["papers"][0]["title"] if report["papers"] else "",
                "top_repo": report["repos"][0]["repo"] if report["repos"] else "",
                "relpath": report["daily_relpath"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    for item in report["papers"]:
        summary = _summary_strip(
            [
                ("方向", item.get("direction", "")),
                ("焦点", item.get("focus", "")),
                ("期刊", item.get("venue", "")),
                ("日期", item.get("published", "未知")),
                ("证据", evidence_label(item)),
                ("获取", item["note"]["access"]),
            ]
        )
        links = _link_row(
            [
                ("合法 PDF/开放入口", item.get("pdf_url") or item.get("oa_url") or item.get("url") or item.get("source_homepage") or ""),
                ("DOI", f"https://doi.org/{item['doi']}" if item.get("doi") else ""),
            ]
        )
        quote = item.get("overview_sentence") and f'<div class="quote">英文摘要原句：{escape(shorten(item["overview_sentence"], 380))}</div>' or ""
        body = (
            '<div class="detail-card">'
            '<a class="back" href="../index.html">← 回到当日日报</a>'
            f"{summary}{links}"
            "</div>"
            '<div class="detail-card"><h2>研究主旨</h2>'
            f'<p>{escape(item["note"]["overview"])}</p>'
            f'<p>{escape(item["note"]["application"])}</p>'
            '</div>'
            '<div class="detail-card"><h2>研究方法</h2>'
            f'<p>{escape(item["note"]["method"])}</p>'
            f'{_tag_row(item.get("method_tags", []) + item.get("concepts", [])[:4])}'
            '</div>'
            '<div class="detail-card"><h2>理论推导线索</h2>'
            f'<p>{escape(item["note"]["theory"])}</p>'
            '<div class="footnote">当前只依据公开摘要和元数据生成线索判断；如果论文未开放全文，不会伪造公式细节。</div>'
            f'{quote}</div>'
            '<div class="detail-card"><h2>实验与结果</h2>'
            f'<p>{escape(item["note"]["experiment"])}</p>'
            f'<p>{escape(item["note"]["result"])}</p>'
            '</div>'
            '<div class="detail-card"><h2>阅读建议</h2>'
            f'<p>{escape(item["note"]["reading"])}</p>'
            f'<p>{escape(item["note"]["access"])}</p>'
            '</div>'
        )
        detail_page = _page(
            item["title"],
            f"Paper · {item['direction']}",
            "这里优先给出中文化的研究判断，让你先决定这篇论文值不值得深读。",
            body,
            "../../../assets/style.css",
        )
        (papers_dir / f'{item["slug"]}.html').write_text(detail_page, encoding="utf-8")

    for item in report["repos"]:
        summary = _summary_strip(
            [
                ("分类", item.get("domain", "")),
                ("语言", item.get("language", "未知")),
                ("相关性", item.get("relevance_label", "")),
                ("得分", str(item.get("relevance_score", 0))),
                ("来源", "Trending" if item.get("source_kind", "trending") == "trending" else "研究向补位"),
            ]
        )
        links = _link_row([("打开 GitHub", item.get("url") or "")])
        quote = item.get("readme_excerpt") and f'<div class="quote">README 摘录：{escape(shorten(item["readme_excerpt"], 520))}</div>' or ""
        body = (
            '<div class="detail-card">'
            '<a class="back" href="../index.html">← 回到当日日报</a>'
            f"{summary}{links}"
            "</div>"
            '<div class="detail-card"><h2>方向定位</h2>'
            f'<p>{escape(item["note"]["overview"])}</p>'
            f'{_tag_row(item.get("topics", [])[:6] + item.get("keyword_hits", [])[:4])}'
            '</div>'
            '<div class="detail-card"><h2>为什么推它</h2>'
            f'<p>{escape(item["note"]["why_trending"])}</p>'
            f'<p>{escape(item["note"]["robotics_value"])}</p>'
            '</div>'
            '<div class="detail-card"><h2>怎么使用它</h2>'
            f'<p>{escape(item["note"]["integration"])}</p>'
            f'<p>{escape(item["note"]["reading"])}</p>'
            '</div>'
            f'<div class="detail-card"><h2>原始信息</h2>{quote or "<p>公开 README 信息较少。</p>"}</div>'
        )
        detail_page = _page(
            item["repo"],
            f"Repo · {item['relevance_label']}",
            "这里优先告诉你它对机器人研究有没有用、该怎么接进你的实验链路。",
            body,
            "../../../assets/style.css",
        )
        (repos_dir / f'{item["slug"]}.html').write_text(detail_page, encoding="utf-8")

    metas = []
    for meta_path in sorted((site_dir / "daily").glob("*/meta.json"), reverse=True):
        try:
            metas.append(json.loads(meta_path.read_text(encoding="utf-8")))
        except Exception:
            continue

    archive_entries = []
    for meta in metas:
        summary = f"论文 {meta['paper_count']} 条，GitHub 项目 {meta['repo_count']} 条。"
        archive_entries.append(
            '<article class="entry">'
            f'<div class="pill">{escape(meta["reference_date"])}</div>'
            f'<h2><a href="{escape(meta["relpath"])}">{escape(meta["reference_date"])} 的手机小文合集</a></h2>'
            f'<p>{escape(summary)}</p>'
            f'<div class="links"><a href="{escape(meta["relpath"])}">打开这一天</a></div>'
            '</article>'
        )
    archive_html = "".join(archive_entries) or '<div class="empty">还没有归档日报。</div>'
    index_body = (
        '<section class="section">'
        '<div class="section-head"><h2>每日小文库</h2><div class="section-note">推送只发浓缩摘要，完整中文小文都保存在这里。</div></div>'
        f'<div class="stack">{archive_html}</div></section>'
    )
    index_page = _page(
        "具身智能每日小文库",
        "Mobile Knowledge Layer",
        "给手机阅读准备的日报归档页，避免你在微信里被一堆原始链接打断。",
        index_body,
        "assets/style.css",
    )
    (site_dir / "index.html").write_text(index_page, encoding="utf-8")
