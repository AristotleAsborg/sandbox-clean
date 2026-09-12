"""Human-facing summaries. Nothing here mutates the ledger."""

from __future__ import annotations

import csv
import io

from .store import Ledger


def summary(ledger: Ledger) -> dict[str, int]:
    """Account name -> balance in cents.

    Cents, not `Money`: this feeds JSON and CSV, where a custom type is just
    something else to serialise wrong.
    """
    return {name: amount.cents for name, amount in ledger.balances().items()}


def biggest_account(ledger: Ledger) -> tuple[str, int] | None:
    """The account with the largest absolute balance, or None for an empty book."""
    balances = summary(ledger)
    if not balances:
        return None
    name = max(balances, key=lambda key: abs(balances[key]))
    return name, balances[name]


def to_csv(ledger: Ledger) -> str:
    """Postings as CSV, newest last. Header is always present."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["debit", "credit", "amount_cents", "memo"])
    for entry in ledger.postings:
        writer.writerow([entry.debit, entry.credit, entry.amount.cents, entry.memo])
    return buffer.getvalue()
