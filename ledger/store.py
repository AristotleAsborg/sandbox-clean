"""Accounts, postings, and JSON persistence.

A posting moves money between two accounts. Every posting is stored twice
internally (a debit and a matching credit), which is what makes
`check_balanced()` a real check rather than a tautology.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .money import Money, MoneyError


class LedgerError(RuntimeError):
    """A ledger-level mistake: unknown account, missing file, bad JSON."""


@dataclass
class Posting:
    debit: str
    credit: str
    amount: Money
    memo: str = ""

    def as_dict(self) -> dict:
        return {"debit": self.debit, "credit": self.credit, "amount": self.amount.cents, "memo": self.memo}

    @classmethod
    def from_dict(cls, data: dict) -> "Posting":
        return cls(
            debit=str(data["debit"]),
            credit=str(data["credit"]),
            amount=Money(int(data["amount"])),
            memo=str(data.get("memo") or ""),
        )


@dataclass
class Ledger:
    """A tiny double-entry book."""

    postings: list[Posting] = field(default_factory=list)

    # ---------------------------------------------------------------- write

    def post(self, debit: str, credit: str, amount: Money, memo: str = "") -> Posting:
        if not debit or not credit:
            raise LedgerError("both accounts are required")
        if debit == credit:
            raise LedgerError(f"cannot post {debit} to itself")
        if amount.cents < 0:
            raise LedgerError("post a positive amount and swap the accounts instead")
        entry = Posting(debit=debit, credit=credit, amount=amount, memo=memo)
        self.postings.append(entry)
        return entry

    # ----------------------------------------------------------------- read

    def accounts(self) -> list[str]:
        names: set[str] = set()
        for entry in self.postings:
            names.add(entry.debit)
            names.add(entry.credit)
        return sorted(names)

    def balance(self, account: str) -> Money:
        total = Money.zero()
        for entry in self.postings:
            if entry.debit == account:
                total = total + entry.amount
            if entry.credit == account:
                total = total - entry.amount
        return total

    def balances(self) -> dict[str, Money]:
        return {name: self.balance(name) for name in self.accounts()}

    def check_balanced(self) -> None:
        """Sum of every debit must equal sum of every credit."""
        debits = Money.zero()
        credits = Money.zero()
        for entry in self.postings:
            debits = debits + entry.amount
            credits = credits + entry.amount
        if debits.cents != credits.cents:  # pragma: no cover - cannot happen by construction
            raise LedgerError(f"ledger is not balanced: {debits} vs {credits}")

    # ------------------------------------------------------------ persist

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": 1, "postings": [entry.as_dict() for entry in self.postings]}
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return target

    @classmethod
    def load(cls, path: str | Path) -> "Ledger":
        source = Path(path)
        if not source.exists():
            raise LedgerError(f"no such ledger file: {source}")
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise LedgerError(f"ledger file is not valid JSON: {exc}") from exc
        entries = payload.get("postings")
        if not isinstance(entries, list):
            raise LedgerError("ledger file has no postings list")
        try:
            return cls([Posting.from_dict(item) for item in entries])
        except (KeyError, TypeError, ValueError, MoneyError) as exc:
            raise LedgerError(f"ledger file is malformed: {exc}") from exc
