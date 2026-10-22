"""Explicit restore into a NEW file. Never stop processes or replace an existing DB."""
import argparse
from pathlib import Path

from app.services.database_backup import restore_database_backup


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backup", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    args = parser.parse_args()
    print(restore_database_backup(args.backup, args.destination))


if __name__ == "__main__":
    main()
