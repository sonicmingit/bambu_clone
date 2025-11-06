"""CLI entry point for MakerWorld synchronization."""
from __future__ import annotations

import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from backend.services.makerworld_client import MakerWorldClient
from backend.sync.tasks import sync_models


def _parse_datetime(value: str) -> datetime:
    try:
        if value.endswith("Z"):
            value = value.replace("Z", "+00:00")
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid datetime value: {value}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sync MakerWorld models")
    parser.add_argument("--pages", type=int, default=1, help="Number of pages to fetch")
    parser.add_argument("--per-page", type=int, default=20, help="Page size for the MakerWorld API")
    parser.add_argument(
        "--updated-after",
        type=_parse_datetime,
        help="Only fetch models updated after the given ISO timestamp",
    )
    parser.add_argument("--no-download", action="store_true", help="Skip downloading attachments")
    parser.add_argument("--storage", help="Override storage root directory")
    parser.add_argument("--username", help="MakerWorld username")
    parser.add_argument("--password", help="MakerWorld password")
    parser.add_argument("--token", help="MakerWorld API token")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Logging level",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=getattr(logging, args.log_level))

    client = MakerWorldClient(username=args.username, password=args.password, token=args.token)

    try:
        sync_models(
            client=client,
            pages=args.pages,
            per_page=args.per_page,
            updated_after=args.updated_after,
            download_files=not args.no_download,
            storage_root=Path(args.storage) if args.storage else None,
        )
    finally:
        client.close()


if __name__ == "__main__":  # pragma: no cover
    main()
