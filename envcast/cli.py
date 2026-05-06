"""Command-line interface for envcast."""

import argparse
import sys
from typing import List, Optional

from envcast.loader import EnvLoader
from envcast.differ import diff_envs
from envcast.formatter import format_diff
from envcast.syncer import sync_env


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envcast",
        description="Diff and sync environment variables across deployment targets.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- diff ---
    diff_p = sub.add_parser("diff", help="Show differences between two .env files.")
    diff_p.add_argument("source", help="Source .env file")
    diff_p.add_argument("target", help="Target .env file")
    diff_p.add_argument(
        "--show-matching", action="store_true", help="Include matching keys in output"
    )
    diff_p.add_argument("--no-color", action="store_true", help="Disable color output")

    # --- sync ---
    sync_p = sub.add_parser("sync", help="Sync source .env into one or more targets.")
    sync_p.add_argument("source", help="Source .env file")
    sync_p.add_argument("targets", nargs="+", help="Target .env file(s)")
    sync_p.add_argument(
        "--no-overwrite", action="store_true", help="Skip keys that already exist"
    )
    sync_p.add_argument(
        "--only-missing", action="store_true", help="Only add keys absent in target"
    )
    sync_p.add_argument(
        "--dry-run", action="store_true", help="Preview changes without writing"
    )

    return parser


def cmd_diff(args: argparse.Namespace) -> int:
    loader = EnvLoader()
    source = loader.load_file(args.source)
    target = loader.load_file(args.target)
    result = diff_envs(source, target)
    print(format_diff(result, show_matching=args.show_matching, color=not args.no_color))
    return 0 if not result.has_differences else 1


def cmd_sync(args: argparse.Namespace) -> int:
    loader = EnvLoader()
    source = loader.load_file(args.source)
    exit_code = 0
    for target_path in args.targets:
        target = loader.load_file(target_path)
        result = sync_env(
            source,
            target,
            target_path,
            overwrite=not args.no_overwrite,
            dry_run=args.dry_run,
            only_missing=args.only_missing,
        )
        status = "[dry-run] " if args.dry_run else ""
        print(
            f"{status}{target_path}: +{len(result.added)} added, "
            f"~{len(result.updated)} updated, -{len(result.skipped)} skipped"
        )
    return exit_code


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "diff":
        sys.exit(cmd_diff(args))
    elif args.command == "sync":
        sys.exit(cmd_sync(args))


if __name__ == "__main__":
    main()
