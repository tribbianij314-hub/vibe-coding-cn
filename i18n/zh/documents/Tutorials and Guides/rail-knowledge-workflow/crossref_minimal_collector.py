"""Crossref 最小采集器示例。

运行方式：
  python crossref_minimal_collector.py --query "railway signaling" --rows 20
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crossref minimal collector")
    parser.add_argument("--query", required=True, help="检索关键词")
    parser.add_argument("--rows", type=int, default=20, help="返回条数")
    parser.add_argument("--out", default="./data/raw", help="输出目录")
    return parser.parse_args()


def normalize_item(item: dict) -> dict:
    authors = []
    for author in item.get("author", []):
        given = author.get("given", "")
        family = author.get("family", "")
        full_name = f"{given} {family}".strip()
        if full_name:
            authors.append(full_name)

    published_at = None
    issued = item.get("issued", {}).get("date-parts", [])
    if issued and issued[0]:
        parts = issued[0]
        year = parts[0]
        month = parts[1] if len(parts) > 1 else 1
        day = parts[2] if len(parts) > 2 else 1
        published_at = f"{year:04d}-{month:02d}-{day:02d}"

    return {
        "source_id": "src_crossref",
        "source_record_id": item.get("DOI"),
        "doi": item.get("DOI"),
        "title": (item.get("title") or [""])[0],
        "authors": authors,
        "abstract": item.get("abstract"),
        "doc_type": item.get("type", "unknown"),
        "published_at": published_at,
        "source_url": item.get("URL") or "",
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


def collect_crossref(query: str, rows: int) -> list[dict]:
    url = "https://api.crossref.org/works"
    params = {"query": query, "rows": rows}

    with httpx.Client(timeout=20) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        payload = response.json()

    items = payload.get("message", {}).get("items", [])
    return [normalize_item(item) for item in items]


def main() -> None:
    args = parse_args()
    records = collect_crossref(args.query, args.rows)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = out_dir / f"crossref_{timestamp}.json"

    output_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"采集完成，记录数: {len(records)}")
    print(f"输出文件: {output_path}")


if __name__ == "__main__":
    main()
