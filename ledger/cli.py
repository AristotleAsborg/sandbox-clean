"""A very small command line front end."""

from __future__ import annotations

import argparse
import sys

from .money import Money, MoneyError
from .report import summary
from .store import Ledger, LedgerError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ledger", description="a tiny ledger")
    sub = parser.add_subparsers(dest="command", required=True)

    post = sub.add_parser("post", help="record a posting")
    post.add_argument("debit")
    post.add_argument("credit")
    post.add_argument("amount")
    post.add_argument("--memo", default="")
    post.add_argument("--file", default=None)

    show = sub.add_parser("summary", help="print balances in cents")
    show.add_argument("--file", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    ledger = Ledger()
    if getattr(args, "file", None):
        try:
            ledger = Ledger.load(args.file)
        except LedgerError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    if args.command == "post":
        try:
            amount = Money.parse(args.amount)
        except MoneyError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        try:
            ledger.post(args.debit, args.credit, amount, args.memo)
        except LedgerError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        if args.file:
            ledger.save(args.file)
        print(f"posted {args.debit} -> {args.credit} {amount}")
        return 0

    for name, cents in summary(ledger).items():
        print(f"{name}\t{cents}")
    return 0
