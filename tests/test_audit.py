import pytest

from atlas.engine import furfine
from atlas.generate import generate
from atlas.models import Bank, Dataset, Exposure, Scenario


def test_overflow_is_rejected():
    with pytest.raises(ValueError, match="Nonfinite"):
        Dataset(
            banks=[
                Bank(
                    id="A",
                    name="A",
                    external_assets=1e308,
                    interbank_assets=1e308,
                    interbank_liabilities=0,
                    deposits=1,
                    equity=1,
                ),
                Bank(
                    id="B",
                    name="B",
                    external_assets=1e308,
                    interbank_assets=0,
                    interbank_liabilities=1e308,
                    deposits=0,
                    equity=1,
                ),
            ],
            exposures=[Exposure(lender="A", borrower="B", amount=1e308)],
        )


def test_event_ledger_reconciles():
    data = generate()
    r = furfine(data, Scenario(external_impairment=0.1))
    assert sum(e["loss"] for e in r["events"]) == pytest.approx(r["interbank_loss"])
    pairs = [(e["lender"], e["borrower"]) for e in r["events"]]
    assert len(pairs) == len(set(pairs))
    for b in data.banks:
        assert r["equity"][b.id] == pytest.approx(
            b.equity - r["bank_external_loss"][b.id] - r["bank_interbank_loss"][b.id]
        )
