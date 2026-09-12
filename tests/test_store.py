"""Postings, balances, and the JSON round trip."""

from __future__ import annotations

import json

import pytest

from ledger import Ledger, LedgerError, Money
from _scratch import drop_scratch, make_scratch


def test_post_returns_the_entry() -> None:
    book = Ledger()
    entry = book.post("cash", "revenue", Money.parse("10.00"))
    assert entry.debit == "cash" and entry.credit == "revenue"


def test_balance_reflects_debit_and_credit() -> None:
    book = Ledger()
    book.post("cash", "revenue", Money.parse("10.00"))
    assert book.balance("cash").cents == 1000
    assert book.balance("revenue").cents == -1000


def test_accounts_are_sorted_and_deduplicated() -> None:
    book = Ledger()
    book.post("cash", "revenue", Money.parse("1.00"))
    book.post("cash", "revenue", Money.parse("1.00"))
    assert book.accounts() == ["cash", "revenue"]


def test_unknown_account_balance_is_zero() -> None:
    assert Ledger().balance("nothing-here").cents == 0


def test_post_to_itself_is_rejected() -> None:
    with pytest.raises(LedgerError):
        Ledger().post("cash", "cash", Money.parse("1.00"))


def test_negative_post_is_rejected() -> None:
    with pytest.raises(LedgerError):
        Ledger().post("cash", "revenue", Money.parse("-1.00"))


def test_empty_account_name_is_rejected() -> None:
    with pytest.raises(LedgerError):
        Ledger().post("", "revenue", Money.parse("1.00"))


def test_check_balanced_passes_on_a_normal_book() -> None:
    book = Ledger()
    book.post("cash", "revenue", Money.parse("5.00"))
    book.check_balanced()


def test_save_then_load_round_trips() -> None:
    book = Ledger()
    book.post("cash", "revenue", Money.parse("12.34"), memo="first sale")
    book.post("expenses", "cash", Money.parse("4.00"), memo="coffee")
    target = book.save("book.json")
    restored = Ledger.load(target)
    assert [entry.as_dict() for entry in restored.postings] == [
        entry.as_dict() for entry in book.postings
    ]


def test_load_missing_file_raises() -> None:
    with pytest.raises(LedgerError):
        Ledger.load("definitely-not-here.json")


def test_load_invalid_json_raises() -> None:
    scratch = make_scratch()
    try:
        broken = scratch / "broken.json"
        broken.write_text("{not json", encoding="utf-8")
        with pytest.raises(LedgerError):
            Ledger.load(broken)
    finally:
        drop_scratch(scratch)


def test_load_malformed_posting_raises() -> None:
    scratch = make_scratch()
    try:
        malformed = scratch / "bad.json"
        malformed.write_text(json.dumps({"postings": [{"debit": "a"}]}), encoding="utf-8")
        with pytest.raises(LedgerError):
            Ledger.load(malformed)
    finally:
        drop_scratch(scratch)
