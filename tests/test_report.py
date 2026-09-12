"""Summaries and CSV export."""

from __future__ import annotations

from ledger import Ledger, Money, summary, to_csv
from ledger.report import biggest_account


def build() -> Ledger:
    book = Ledger()
    book.post("cash", "revenue", Money.parse("10.00"))
    book.post("expenses", "cash", Money.parse("3.00"))
    return book


def test_summary_is_in_cents() -> None:
    assert summary(build()) == {"cash": 700, "expenses": 300, "revenue": -1000}


def test_summary_of_empty_ledger_is_empty() -> None:
    assert summary(Ledger()) == {}


def test_biggest_account_picks_largest_absolute_balance() -> None:
    assert biggest_account(build()) == ("revenue", -1000)


def test_biggest_account_of_empty_ledger_is_none() -> None:
    assert biggest_account(Ledger()) is None


def test_csv_has_header_and_one_row_per_posting() -> None:
    rows = to_csv(build()).strip().splitlines()
    assert rows[0] == "debit,credit,amount_cents,memo"
    assert len(rows) == 3


def test_csv_quotes_memos_with_commas() -> None:
    book = Ledger()
    book.post("cash", "revenue", Money.parse("1.00"), memo="sale, small")
    assert '"sale, small"' in to_csv(book)
