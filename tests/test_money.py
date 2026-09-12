"""Money has to be exact; these tests are the reason the type exists."""

from __future__ import annotations

import pytest

from ledger import Money, MoneyError


def test_parse_whole_number() -> None:
    assert Money.parse("12").cents == 1200


def test_parse_one_decimal() -> None:
    assert Money.parse("12.3").cents == 1230


def test_parse_two_decimals() -> None:
    assert Money.parse("12.34").cents == 1234


def test_parse_negative() -> None:
    assert Money.parse("-7.05").cents == -705


def test_parse_strips_thousands_separator_and_space() -> None:
    assert Money.parse(" 1,234.50 ").cents == 123450


@pytest.mark.parametrize("bad", ["", "12.345", "abc", "1.2.3", "--5", "12."])
def test_parse_rejects_junk(bad: str) -> None:
    with pytest.raises(MoneyError):
        Money.parse(bad)


def test_str_round_trips_through_parse() -> None:
    for text in ("0.00", "12.34", "-7.05", "999.99"):
        assert str(Money.parse(text)) == text


def test_float_adds_wrong_but_money_does_not() -> None:
    """The whole point of the type: three tenths really is three tenths."""
    total = Money.zero()
    for _ in range(3):
        total = total + Money.parse("0.10")
    assert total.cents == 30
    assert str(total) == "0.30"


def test_multiply_requires_int() -> None:
    with pytest.raises(MoneyError):
        Money.parse("1.00") * 1.5  # type: ignore[operator]


def test_multiply_by_int() -> None:
    assert (Money.parse("2.50") * 4).cents == 1000
