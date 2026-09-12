# ledger

A tiny double-entry ledger, used as the *clean* practice repository for
`repo-autopilot` (see the roadmap, step 1.6).

It exists so the pipeline can do a fast smoke run against a project that is
supposed to be healthy: everything passes, nothing is flaky, the README matches
the code.

## Install

```console
python -m pip install -e .
```

Requires Python 3.10 or newer. The runtime has no third-party dependencies;
`pytest` is needed only to run the test suite.

## Usage

```python
from ledger import Ledger, Money

book = Ledger()
book.post("cash", "revenue", Money.parse("12.34"))
book.balance("cash")          # Money(cents=1234)
book.summary()                # {'cash': 1234, 'revenue': -1234}
```

## Layout

| path | what |
| --- | --- |
| `ledger/money.py` | integer-cent money type; no floats anywhere |
| `ledger/store.py` | accounts, postings, JSON persistence |
| `ledger/report.py` | summaries and CSV export |

## Tests

`python -m pytest -q` — 20 tests, no network, no fixtures on disk.
