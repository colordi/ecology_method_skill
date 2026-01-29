#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文献检索脚本（默认：Semantic Scholar API）

设计目标：
- 只检索元数据（标题/摘要/作者/期刊/年份/被引次数/链接/DOI 等）
- 便于 Stage 2 用“标题+摘要”做初筛，避免抓取全文
- 不依赖第三方库，减少环境摩擦
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


S2_API_BASE = "https://api.semanticscholar.org/graph/v1"
DEFAULT_FIELDS = [
    "title",
    "authors",
    "year",
    "venue",
    "abstract",
    "url",
    "externalIds",
    "citationCount",
]


@dataclass(frozen=True)
class Paper:
    title: str
    year: Optional[int]
    venue: Optional[str]
    authors: List[str]
    citation_count: Optional[int]
    abstract: Optional[str]
    url: Optional[str]
    doi: Optional[str]


def _http_get_json(url: str, timeout_sec: int = 30, retries: int = 3) -> Dict[str, Any]:
    headers = {
        "User-Agent": "ecology-methods-literature-list/1.0 (metadata-only; contact: none)",
        "Accept": "application/json",
    }
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key

    last_err: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                data = resp.read().decode("utf-8", errors="replace")
                return json.loads(data)
        except urllib.error.HTTPError as e:
            last_err = e
            # 429/5xx 做有限次退避重试，避免频繁失败影响使用体验
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                wait_sec = 1.5 * (2**attempt)
                time.sleep(wait_sec)
                continue
            raise
        except urllib.error.URLError as e:
            last_err = e
            if attempt < retries:
                wait_sec = 1.0 * (2**attempt)
                time.sleep(wait_sec)
                continue
            raise

    if last_err:
        raise last_err
    raise RuntimeError("未知网络错误")


def _parse_papers(payload: Dict[str, Any]) -> List[Paper]:
    out: List[Paper] = []
    for item in payload.get("data", []) or []:
        title = (item.get("title") or "").strip()
        if not title:
            continue

        authors = []
        for a in item.get("authors", []) or []:
            name = (a.get("name") or "").strip()
            if name:
                authors.append(name)

        external_ids = item.get("externalIds") or {}
        doi = external_ids.get("DOI") or external_ids.get("doi")
        if isinstance(doi, str):
            doi = doi.strip() or None
        else:
            doi = None

        year = item.get("year")
        if not isinstance(year, int):
            year = None

        venue = item.get("venue")
        if isinstance(venue, str):
            venue = venue.strip() or None
        else:
            venue = None

        citation_count = item.get("citationCount")
        if not isinstance(citation_count, int):
            citation_count = None

        abstract = item.get("abstract")
        if isinstance(abstract, str):
            abstract = abstract.strip() or None
        else:
            abstract = None

        url = item.get("url")
        if isinstance(url, str):
            url = url.strip() or None
        else:
            url = None

        out.append(
            Paper(
                title=title,
                year=year,
                venue=venue,
                authors=authors,
                citation_count=citation_count,
                abstract=abstract,
                url=url,
                doi=doi,
            )
        )
    return out


def search_semantic_scholar(
    query: str,
    limit: int,
    offset: int,
    fields: List[str],
    year_start: Optional[int],
    year_end: Optional[int],
    timeout_sec: int,
) -> Tuple[List[Paper], Dict[str, Any]]:
    if limit <= 0 or limit > 100:
        raise ValueError("limit 需在 1..100 之间")

    def in_year_range(p: Paper) -> bool:
        if year_start is None and year_end is None:
            return True
        if p.year is None:
            return False
        if year_start is not None and p.year < year_start:
            return False
        if year_end is not None and p.year > year_end:
            return False
        return True

    # 说明：
    # - Semantic Scholar 的搜索接口支持 offset 翻页。
    # - 若用户给了年份过滤，我们会“多翻几页”来尽量补齐到目标 limit，
    #   避免“先取 limit 条再过滤”导致返回数量偏少。
    collected: List[Paper] = []
    fetched_items = 0
    fetched_pages = 0
    api_total: Optional[int] = None

    page_limit = min(100, max(10, limit))
    max_pages = 20  # 保护：避免在年份过滤很苛刻时无限翻页
    page_offset = max(0, offset)

    while len(collected) < limit and fetched_pages < max_pages:
        params = {
            "query": query,
            "limit": str(page_limit),
            "offset": str(page_offset),
            "fields": ",".join(fields),
        }
        url = f"{S2_API_BASE}/paper/search?{urllib.parse.urlencode(params)}"
        payload = _http_get_json(url, timeout_sec=timeout_sec, retries=3)
        api_total = payload.get("total") if api_total is None else api_total

        papers_page = _parse_papers(payload)
        if not papers_page:
            break

        fetched_pages += 1
        fetched_items += len(papers_page)

        for p in papers_page:
            if not in_year_range(p):
                continue
            collected.append(p)
            if len(collected) >= limit:
                break

        page_offset += page_limit

        # 若 API 已明确 total，并且我们已经翻到末尾，提前结束
        if isinstance(api_total, int) and page_offset >= api_total:
            break

        # 没有年份过滤时，默认只取一页（更快、更省配额）
        if year_start is None and year_end is None:
            break

    meta = {
        "provider": "semantic_scholar",
        "query": query,
        "requested_limit": limit,
        "offset": offset,
        "year_start": year_start,
        "year_end": year_end,
        "total": api_total,
        "fetched_pages": fetched_pages,
        "fetched_items": fetched_items,
        "returned_items": len(collected),
        "note": "年份过滤在本地执行；为补齐返回数量，可能自动翻页多次。",
    }
    return collected[:limit], meta


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
                    "citationCount": p.citation_count,
                    "doi": p.doi,
                    "url": p.url,
                    "abstract": p.abstract,
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
    total = meta.get("total")
    if total is not None:
        lines.append(f"- 结果总数（API返回）: {total}")
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
        lines.append(f"   - Citations: {p.citation_count if p.citation_count is not None else '未知'}")
        lines.append(f"   - DOI: `{p.doi}`" if p.doi else "   - DOI: 未知")
        lines.append(f"   - URL: {p.url}" if p.url else "   - URL: 未知")
        if p.abstract:
            abs_text = p.abstract.replace("\n", " ").strip()
            if abstract_max_chars > 0 and len(abs_text) > abstract_max_chars:
                abs_text = abs_text[: abstract_max_chars].rstrip() + "…"
            lines.append(f"   - Abstract: {abs_text}")
        else:
            lines.append("   - Abstract: 未提供")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="search_literature.py",
        description="文献检索（元数据/标题摘要初筛；默认使用 Semantic Scholar API）",
    )
    parser.add_argument("query", help="检索关键词/检索式（建议包含方法名+生态学场景关键词）")
    parser.add_argument("--limit", type=int, default=10, help="返回条目数（默认 10）")
    parser.add_argument("--offset", type=int, default=0, help="结果偏移量（用于翻页）")
    parser.add_argument("--year-start", type=int, default=None, help="起始年份（含）")
    parser.add_argument("--year-end", type=int, default=None, help="终止年份（含）")
    parser.add_argument(
        "--format",
        choices=["json", "md"],
        default="json",
        help="输出格式：json 或 md（默认 json）",
    )
    parser.add_argument(
        "--fields",
        default=",".join(DEFAULT_FIELDS),
        help="字段列表（逗号分隔，默认包含 title/authors/year/venue/abstract/url/externalIds/citationCount）",
    )
    parser.add_argument(
        "--abstract-max-chars",
        type=int,
        default=280,
        help="md 输出时摘要最大字符数（默认 280；0 表示不截断）",
    )
    parser.add_argument("--timeout", type=int, default=30, help="请求超时秒数（默认 30）")
    args = parser.parse_args(argv)

    if args.limit <= 0 or args.limit > 100:
        print("错误：--limit 需在 1..100 之间", file=sys.stderr)
        return 2

    fields = [f.strip() for f in (args.fields or "").split(",") if f.strip()]
    if not fields:
        print("错误：--fields 不能为空", file=sys.stderr)
        return 2

    try:
        papers, meta = search_semantic_scholar(
            query=args.query,
            limit=args.limit,
            offset=args.offset,
            fields=fields,
            year_start=args.year_start,
            year_end=args.year_end,
            timeout_sec=args.timeout,
        )
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
        print(f"请求失败（HTTP {e.code}）：{msg}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"请求失败（网络错误）：{e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"请求失败：{e}", file=sys.stderr)
        return 1

    if args.format == "json":
        sys.stdout.write(_to_json(papers, meta) + "\n")
        return 0

    sys.stdout.write(_to_markdown(papers, meta, abstract_max_chars=args.abstract_max_chars))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
