"""Command line interface for Pantau Anggaran pilot.

Examples:
    python cli.py summary
    python cli.py list --flagged-only
    python cli.py search --q laboratorium
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.flags import attach_flags, summarize
from app.loader import default_sample_path, load_csv


def main() -> None:
    parser = argparse.ArgumentParser(prog="pantau-anggaran", description="Pantau Anggaran pilot CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("summary", help="Ringkasan dataset pilot")
    p_list = sub.add_parser("list", help="Daftar paket dengan benderanya")
    p_list.add_argument("--flagged-only", action="store_true")
    p_search = sub.add_parser("search", help="Cari paket")
    p_search.add_argument("--q", required=True)

    args = parser.parse_args()
    packages = attach_flags(load_csv(default_sample_path()))
    if args.command == "summary":
        result = summarize(packages)
    elif args.command == "list":
        items = packages
        if args.flagged_only:
            items = [p for p in items if p["flags"]]
        result = {"packages": items, "count": len(items)}
    else:
        lowered = args.q.lower()
        items = [p for p in packages if lowered in p["nama_paket"].lower()]
        result = {"packages": items, "count": len(items)}
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
