"""Retrieve cited chunks; print the full JSON response or save it to a file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from uuid import UUID

from ragwell import AsyncRagwell
from ragwell.types import SearchFilters, SearchResponse

from common import load_settings, run


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phrase", help="retrieval query, in quotes")
    parser.add_argument(
        "--k", type=int, choices=range(1, 21), default=5, metavar="1..20"
    )
    parser.add_argument(
        "--document-id",
        type=UUID,
        action="append",
        help="repeat to include multiple document IDs",
    )
    for option in ("tag", "tag-all", "source", "author", "language", "category"):
        parser.add_argument(
            f"--{option}", action="append", help="repeat for multiple values"
        )
    parser.add_argument(
        "--output", type=Path, help="save full JSON here instead of printing it"
    )
    args = parser.parse_args(argv)
    if not args.phrase.strip() or len(args.phrase) > 2048:
        parser.error("phrase must contain 1–2048 characters")
    for name in (
        "document_id",
        "tag",
        "tag_all",
        "source",
        "author",
        "language",
        "category",
    ):
        if len(getattr(args, name) or []) > 20:
            parser.error(f"--{name.replace('_', '-')} accepts at most 20 values")
    return args


def search_filters(args: argparse.Namespace) -> SearchFilters:
    return SearchFilters(
        document_ids=args.document_id or [],
        tags_any=args.tag or [],
        tags_all=args.tag_all or [],
        source_any=args.source or [],
        author_any=args.author or [],
        language_any=args.language or [],
        category_any=args.category or [],
    )


def output_response(response: SearchResponse, output: Path | None) -> None:
    text = json.dumps(response.to_dict(), ensure_ascii=False, indent=2) + "\n"
    if output is None:
        print(text, end="")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        # Avoid accidentally replacing an earlier response or another local file.
        with output.open("x", encoding="utf-8") as destination:
            destination.write(text)
        print(f"Saved {len(response.items)} result(s) to {output}")


async def main() -> int:
    args = parse_args()
    if args.output is not None and args.output.exists():
        raise ValueError("Output already exists; choose a new filename")
    settings = load_settings()
    async with AsyncRagwell(
        base_url=settings.base_url, api_key=settings.api_key
    ) as client:
        response = await client.project(settings.project_id).search(
            query=args.phrase, k=args.k, filters=search_filters(args)
        )
    output_response(response, args.output)
    return 0


if __name__ == "__main__":
    run(main())
