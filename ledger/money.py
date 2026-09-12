"""Money as integer cents. No floats, ever.

Why this file exists at all: `0.1 + 0.2 != 0.3` in binary floating point. A
ledger that drifts by a cent per thousand postings is worse than useless,
because the drift is invisible until somebody reconciles the books by hand.
So the type stores cents and refuses to do arithmetic with anything else.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Accepts "12", "12.3", "12.34", "-7.05". Two decimal places at most: a third
# decimal is a bug in the caller, not something to round away silently.
_AMOUNT = re.compile(r"^-?\d+(\.\d{1,2})?$")


class MoneyError(ValueError):
    """Raised for amounts that cannot be represented exactly in cents."""


@dataclass(frozen=True, order=True)
class Money:
    """An exact amount of money."""

    cents: int

    def __post_init__(self) -> None:
        if not isinstance(self.cents, int):
            raise MoneyError(f"cents must be int, got {type(self.cents).__name__}")

    # ------------------------------------------------------------- construct

    @classmethod
    def parse(cls, text: str) -> "Money":
        """Parse a decimal string into cents, exactly."""
        cleaned = text.strip().replace(",", "")
        if not cleaned:
            raise MoneyError("empty amount")
        if not _AMOUNT.match(cleaned):
            raise MoneyError(f"not a 2-decimal amount: {text!r}")
        negative = cleaned.startswith("-")
        digits = cleaned.lstrip("-")
        if "." in digits:
            whole, fraction = digits.split(".", 1)
        else:
            whole, fraction = digits, ""
        fraction = (fraction + "00")[:2]
        cents = int(whole) * 100 + int(fraction)
        return cls(-cents if negative else cents)

    @classmethod
    def zero(cls) -> "Money":
        return cls(0)

    # -------------------------------------------------------------- render

    def __str__(self) -> str:
        sign = "-" if self.cents < 0 else ""
        whole, fraction = divmod(abs(self.cents), 100)
        return f"{sign}{whole}.{fraction:02d}"

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Money({self.cents})"

    # ---------------------------------------------------------- arithmetic

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.cents + other.cents)

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.cents - other.cents)

    def __neg__(self) -> "Money":
        return Money(-self.cents)

    def __mul__(self, factor: int) -> "Money":
        """Multiplication is integer-only on purpose.

        Multiplying money by 1.5 has to decide where the half cent goes; that is
        a business decision (allocate? round? split?), not an operator's job.
        """
        if not isinstance(factor, int):
            raise MoneyError("multiply money by an int; rounding policy is a business decision")
        return Money(self.cents * factor)
