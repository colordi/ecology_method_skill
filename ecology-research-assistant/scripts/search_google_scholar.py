#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Scholar 检索脚本（基于 scholarly）

说明：
- Google Scholar 无官方公开 API；scholarly 属于非官方访问方式，可能触发风控/验证码/429。
- 本脚本仅用于获取标题/摘要等元数据做初筛，不抓取全文。
- 若频繁失败，建议改用内置的 Semantic Scholar 路径（scripts/search_literature.py）。
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    from scholarly import ProxyGenerator, scholarly  # type: ignore

    SCHOLARLY_AVAILABLE = True
except ImportError:
    SCHOLARLY_AVAILABLE = False


@dataclass(frozen=True)
class Paper:
    title: str
    authors: List[str]
    year: Optional[int]
    venue: Optional[str]
    citations: Optional[int]
    abstract: Optional[str]
    url: Optional[str]
    eprint_url: Optional[str]


def _setup_proxy(use_proxy: bool) -> None:
    if not use_proxy:
        return
    try:
        pg = ProxyGenerator()
        pg.FreeProxies()
        scholarly.use_proxy(pg)
        print("Using free proxy (scholarly)", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Could not setup proxy: {e}", file=sys.stderr)


def _safe_int(v: Any) -> Optional[int]:
    try:
        if v is None:
            return None
        if isinstance(v, int):
            return v
        s = str(v).strip()
        return int(s) if s else None
    except Exception:
        return None


def _extract(result: Dict[str, Any]) -> Paper:
    bib = result.get("bib", {}) or {}
    title = (bib.get("title") or "").strip()

    authors_raw = bib.get("author", []) or []
    if isinstance(authors_raw, str):
        authors = [a.strip() for a in authors_raw.split(" and ") if a.strip()]
    else:
        authors = [str(a).strip() for a in authors_raw if str(a).strip()]

    year = _safe_int(bib.get("pub_year"))

    venue = bib.get("venue")
    if isinstance(venue, str):
        venue = venue.strip() or None
    else:
        venue = None

    abstract = bib.get("abstract")
    if isinstance(abstract, str):
        abstract = abstract.strip() or None
    else:
        abstract = None

    citations = _safe_int(result.get("num_citations"))

    url = result.get("pub_url")
    if isinstance(url, str):
        url = url.strip() or None
    else:
        url = None

    eprint_url = result.get("eprint_url")
    if isinstance(eprint_url, str):
        eprint_url = eprint_url.strip() or None
    else:
        eprint_url = None

    return Paper(
        title=title,
        authors=authors,
        year=year,
        venue=venue,
        citations=citations,
        abstract=abstract,
        url=url,
        eprint_url=eprint_url,
    )


def search(
    query: str,
    limit: int,
    year_start: Optional[int],
    year_end: Optional[int],
    sort_by: str,
    use_proxy: bool,
    min_delay_sec: float,
    max_delay_sec: float,
) -> List[Paper]:
    if not SCHOLARLY_AVAILABLE:
        raise ImportError("scholarly library required. Install with: pip install scholarly")

    if limit <= 0 or limit > 200:
        raise ValueError("--limit 需在 1..200 之间")

    _setup_proxy(use_proxy)

    print(f"Searching Google Scholar: {query}", file=sys.stderr)
    results: List[Paper] = []

    search_query = scholarly.search_pubs(query)
    for i, r in enumerate(search_query):
        if i >= limit:
            break

        paper = _extract(r)
        if not paper.title:
            continue

        if year_start is not None or year_end is not None:
            if paper.year is None:
                continue
            if year_start is not None and paper.year < year_start:
                continue
            if year_end is not None and paper.year > year_end:
                continue

        results.append(paper)

        # 轻度节流，避免过快访问
        sleep_sec = random.uniform(min_delay_sec, max_delay_sec)
        time.sleep(max(0.0, sleep_sec))

    if sort_by == "citations":
        results.sort(key=lambda p: p.citations or 0, reverse=True)

    return results


def _to_json(papers: List[Paper], meta: Dict[str, Any]) -> str:
    return json.dumps(
        {
            "meta": meta,
            "results": [
                {
                    "title": p.title,
                    "authors": p.authors,
                    "year": p.year,
                    "venue": p.venue,
                    "citationCount": p.citations,
                    "doi": None,
                    "url": p.url,
                    "abstract": p.abstract,
                    "eprintUrl": p.eprint_url,
                }
                for p in papers
            ],
        },
        ensure_ascii=False,
        indent=2,
    )


def _to_markdown(papers: List[Paper], meta: Dict[str, Any], abstract_max_chars: int) -> str:
    lines: List[str] = []
    lines.append("# Candidate Papers（标题+摘要初筛）")
    lines.append("")
    lines.append("## 检索信息")
    lines.append(f"- Provider: {meta.get('provider')}")
    lines.append(f"- Query: `{meta.get('query')}`")
    if meta.get("year_start") or meta.get("year_end"):
        lines.append(f"- 年份范围: {meta.get('year_start') or ''}–{meta.get('year_end') or ''}")
    lines.append("")
    lines.append("## 候选条目（供用户取全文核对）")
    lines.append("")

    if not papers:
        lines.append("- （无结果）")
        return "\n".join(lines) + "\n"

    for i, p in enumerate(papers, start=1):
        authors = ", ".join(p.authors[:3]) + (" et al." if len(p.authors) > 3 else "")
        lines.append(f"{i}. **{p.title}**")
        lines.append(f"   - Authors: {authors or '未知'}")
        lines.append(f"   - Year: {p.year or '未知'}")
        lines.append(f"   - Venue: {p.venue or '未知'}")
        lines.append(f"   - Citations: {p.citations if p.citations is not None else '未知'}")
        lines.append(f"   - URL: {p.url}" if p.url else "   - URL: 未知")
        if p.eprint_url:
            lines.append(f"   - Eprint URL: {p.eprint_url}")
        if p.abstract:
            abs_text = p.abstract.replace("\n", " ").strip()
            if abstract_max_chars > 0 and len(abs_text) > abstract_max_chars:
                abs_text = abs_text[: abstract_max_chars].rstrip() + "…"
            lines.append(f"   - Abstract: {abs_text}")
        else:
            lines.append("   - Abstract: 未提供")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _bibtex_key(authors: List[str], year: Optional[int], title: str) -> str:
    if authors:
        last_name = authors[0].split()[-1] or "Unknown"
    else:
        last_name = "Unknown"
    y = str(year) if year else "XXXX"
    words = re.findall(r"\b[a-zA-Z]{4,}\b", title or "")
    keyword = (words[0].lower() if words else "paper").strip()
    return f"{last_name}{y}{keyword}"


def _to_bibtex(papers: List[Paper], meta: Dict[str, Any]) -> str:
    entries: List[str] = []
    for p in papers:
        key = _bibtex_key(p.authors, p.year, p.title)
        venue = (p.venue or "").lower()
        if "proceedings" in venue or "conference" in venue:
            entry_type = "inproceedings"
            venue_field = "booktitle"
        else:
            entry_type = "article"
            venue_field = "journal"

        lines = [f"@{entry_type}{{{key},"]
        if p.authors:
            lines.append(f"  author = {{{' and '.join(p.authors)}}},")
        if p.title:
            lines.append(f"  title = {{{p.title}}},")
        if p.venue:
            lines.append(f"  {venue_field} = {{{p.venue}}},")
        if p.year:
            lines.append(f"  year = {{{p.year}}},")
        if p.url:
            lines.append(f"  url = {{{p.url}}},")
        if p.citations:
            lines.append(f"  note = {{Cited by: {p.citations}}},")
        if lines[-1].endswith(","):
            lines[-1] = lines[-1][:-1]
        lines.append("}")
        entries.append("\n".join(lines))
    return "\n\n".join(entries).rstrip() + "\n"


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Google Scholar 检索（需要 scholarly 库；仅用于元数据初筛）",
        epilog='示例：python ecology-methods-literature-list/scripts/search_google_scholar.py "machine learning" --limit 20 --format json',
    )
    parser.add_argument("query", help="检索关键词/检索式")
    parser.add_argument("--limit", type=int, default=20, help="返回条目数上限（默认 20）")
    parser.add_argument("--year-start", type=int, default=None, help="起始年份（含）")
    parser.add_argument("--year-end", type=int, default=None, help="终止年份（含）")
    parser.add_argument(
        "--sort-by",
        choices=["relevance", "citations"],
        default="relevance",
        help="排序方式（默认 relevance；citations 会更慢且更易触发限流）",
    )
    parser.add_argument("--use-proxy", action="store_true", help="使用免费代理（不推荐；可能泄露检索词）")
    parser.add_argument(
        "--format",
        choices=["json", "md", "bibtex"],
        default="json",
        help="输出格式（默认 json）",
    )
    parser.add_argument(
        "--abstract-max-chars",
        type=int,
        default=280,
        help="md 输出时摘要最大字符数（默认 280；0 表示不截断）",
    )
    parser.add_argument(
        "--min-delay",
        type=float,
        default=2.0,
        help="请求间隔最小秒数（默认 2.0）",
    )
    parser.add_argument(
        "--max-delay",
        type=float,
        default=5.0,
        help="请求间隔最大秒数（默认 5.0）",
    )
    args = parser.parse_args(argv)

    if not SCHOLARLY_AVAILABLE:
        print("Error: scholarly library not installed", file=sys.stderr)
        print("Install with: pip install scholarly", file=sys.stderr)
        return 1

    papers = search(
        query=args.query,
        limit=args.limit,
        year_start=args.year_start,
        year_end=args.year_end,
        sort_by=args.sort_by,
        use_proxy=args.use_proxy,
        min_delay_sec=args.min_delay,
        max_delay_sec=args.max_delay,
    )

    meta = {
        "provider": "google_scholar",
        "query": args.query,
        "limit": args.limit,
        "year_start": args.year_start,
        "year_end": args.year_end,
        "sort_by": args.sort_by,
        "count": len(papers),
        "note": "非官方访问方式；可能触发验证码/限流",
    }

    if args.format == "json":
        sys.stdout.write(_to_json(papers, meta) + "\n")
        return 0 if papers else 2
    if args.format == "md":
        sys.stdout.write(_to_markdown(papers, meta, abstract_max_chars=args.abstract_max_chars))
        return 0 if papers else 2
    sys.stdout.write(_to_bibtex(papers, meta))
    return 0 if papers else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
