#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
从检索脚本的 JSON 输出生成 reading-list.md 的“单个验证点段落”。

设计目标：
- 只做结构化填充：把 title/authors/year/venue/doi/url 等字段映射到模板
- 不做内容推断：不自动判断“相关性/适用边界”，只保留待填位置
- 兼容两种来源：
  - scripts/search_literature.py（Semantic Scholar）
  - scripts/search_google_scholar.py（Google Scholar）
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence


@dataclass(frozen=True)
class Paper:
    title: str
    authors: List[str]
    year: Optional[int]
    venue: Optional[str]
    doi: Optional[str]
    url: Optional[str]


def _read_json(path: str) -> Dict[str, Any]:
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _as_str(v: Any) -> Optional[str]:
    if isinstance(v, str):
        s = v.strip()
        return s or None
    return None


def _as_int(v: Any) -> Optional[int]:
    if isinstance(v, int):
        return v
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return None
        try:
            return int(s)
        except Exception:
            return None
    return None


def _parse_results(payload: Dict[str, Any]) -> List[Paper]:
    results = payload.get("results", [])
    if not isinstance(results, list):
        raise ValueError("JSON 格式错误：results 不是数组")

    papers: List[Paper] = []
    for item in results:
        if not isinstance(item, dict):
            continue

        title = _as_str(item.get("title")) or ""
        if not title:
            continue

        authors_raw = item.get("authors", [])
        authors: List[str] = []
        if isinstance(authors_raw, list):
            for a in authors_raw:
                s = _as_str(a)
                if s:
                    authors.append(s)
        elif isinstance(authors_raw, str):
            # 兼容少数情况：作者字符串
            authors = [a.strip() for a in authors_raw.split(",") if a.strip()]

        year = _as_int(item.get("year"))
        venue = _as_str(item.get("venue"))
        doi = _as_str(item.get("doi"))
        url = _as_str(item.get("url")) or _as_str(item.get("eprintUrl"))

        papers.append(
            Paper(
                title=title,
                authors=authors,
                year=year,
                venue=venue,
                doi=doi,
                url=url,
            )
        )
    return papers


def _authors_short(authors: Sequence[str]) -> str:
    if not authors:
        return "未知"
    if len(authors) <= 3:
        return ", ".join(authors)
    return ", ".join(authors[:3]) + " et al."


def _render(vp_title: str, vp_decision: str, papers: List[Paper], limit: int) -> str:
    out: List[str] = []
    out.append(f"## Verification Point: {vp_title}")
    out.append(f"> {vp_decision}")
    out.append("")

    if not papers:
        out.append("- （无候选文献：请调整检索式或放宽年份范围）")
        out.append("")
        return "\n".join(out)

    for i, p in enumerate(papers[:limit], start=1):
        out.append(f"### Paper {i}")
        out.append(f"- 标题：{p.title}")
        out.append(f"- 作者：{_authors_short(p.authors)}")
        out.append(f"- 年份：{p.year if p.year is not None else '未知'}")
        out.append(f"- 期刊/会议：{p.venue or '未知'}")
        out.append(f"- DOI：{p.doi or ''}")
        out.append(f"- 链接：{p.url or ''}")
        out.append("- 相关性（Skill1 填）：（待填：它支撑了哪个方法决策点）")
        out.append("- 适用边界/警告（Skill1 初填，可后续修正）：（待填：前提/限制/不适用情形）")
        out.append("")
        out.append("- 精读要点（必填，用户填）：")
        out.append("  -")
        out.append("- 原文定位（必填，用户填）：")
        out.append("  -")
        out.append("- 可直接写入 Methods 的表述（可选，用户填）：")
        out.append("  -")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="make_reading_list_section.py",
        description="把检索 JSON 输出转换为 reading-list.md 的单个验证点段落（不做内容推断）",
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="检索脚本输出的 JSON 文件路径；用 - 表示从 stdin 读取",
    )
    parser.add_argument(
        "--verification-point",
        "-v",
        required=True,
        help="验证点标题（将写入 'Verification Point' 标题行）",
    )
    parser.add_argument(
        "--decision",
        "-d",
        default="（待填：要验证/支撑的具体方法决策句）",
        help="验证点对应的“可核对决策句”（写入引用块）",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="最多输出多少篇候选（默认 10）",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="-",
        help="输出路径；默认输出到 stdout（-）",
    )
    args = parser.parse_args(argv)

    if args.limit <= 0 or args.limit > 100:
        print("错误：--limit 需在 1..100 之间", file=sys.stderr)
        return 2

    try:
        payload = _read_json(args.input)
        papers = _parse_results(payload)
        md = _render(args.verification_point, args.decision, papers, limit=args.limit)
    except Exception as e:
        print(f"生成失败：{e}", file=sys.stderr)
        return 1

    if args.output == "-":
        sys.stdout.write(md)
        return 0

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

