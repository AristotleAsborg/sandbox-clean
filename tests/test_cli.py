"""The command line front end."""

from __future__ import annotations

import json

from ledger.cli import main
from _scratch import drop_scratch, make_scratch


def test_post_prints_the_amount(capsys) -> None:
    assert main(["post", "cash", "revenue", "12.34"]) == 0
    assert "12.34" in capsys.readouterr().out


def test_bad_amount_returns_two(capsys) -> None:
    assert main(["post", "cash", "revenue", "12.345"]) == 2
    assert "error:" in capsys.readouterr().err


def test_summary_reads_a_file() -> None:
    scratch = make_scratch()
    try:
        book = scratch / "book.json"
        book.write_text(
            json.dumps(
                {
                    "version": 1,
                    "postings": [
                        {"debit": "cash", "credit": "revenue", "amount": 1234, "memo": ""}
                    ],
                }
            ),
            encoding="utf-8",
        )
        assert main(["summary", "--file", str(book)]) == 0
    finally:
        drop_scratch(scratch)
