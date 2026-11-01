"""Independent numerical controls for the direct-only comparison."""

import pytest

from atlas.baseline import direct_loss_only
from atlas.engine import furfine
from atlas.models import Bank, Dataset, Exposure, Scenario


@pytest.fixture
def hand_chain():
    # A lends 100 to B; C lends 80 to A. Assets = liabilities + equity.
    return Dataset(
        topology="manual_chain",
        banks=[
            Bank(
                id="A",
                name="A",
                external_assets=100,
                interbank_assets=100,
                interbank_liabilities=80,
                deposits=70,
                equity=50,
            ),
            Bank(
                id="B",
                name="B",
                external_assets=200,
                interbank_assets=0,
                interbank_liabilities=100,
                deposits=50,
                equity=50,
            ),
            Bank(
                id="C",
                name="C",
                external_assets=100,
                interbank_assets=80,
                interbank_liabilities=0,
                deposits=140,
                equity=40,
            ),
        ],
        exposures=[
            Exposure(lender="A", borrower="B", amount=100),
            Exposure(lender="C", borrower="A", amount=80),
        ],
    )


def test_hand_chain_direct_vs_cascade(hand_chain):
    scenario = Scenario(initial_defaults=["B"], recovery=0.4)
    before = hand_chain.model_dump_json()
    direct = direct_loss_only(hand_chain, scenario)
    cascade = furfine(hand_chain, scenario)
    assert direct["interbank_loss"] == pytest.approx(60)
    assert direct["defaults"] == ["A", "B"]
    assert direct["secondary_defaults"] == ["A"]
    assert direct["equity"] == {"A": -10, "B": 50, "C": 40}
    assert cascade["interbank_loss"] == pytest.approx(108)
    assert cascade["secondary_defaults"] == ["A", "C"]
    assert cascade["interbank_loss"] - direct["interbank_loss"] == pytest.approx(48)
    assert hand_chain.model_dump_json() == before


def test_initially_failed_lenders_do_not_receive_loss(hand_chain):
    direct = direct_loss_only(hand_chain, Scenario(initial_defaults=["A", "B", "B"]))
    assert direct["initial_defaults"] == ["A", "B"]
    assert direct["secondary_defaults"] == ["C"]
    assert direct["bank_interbank_loss"] == {"A": 0, "B": 0, "C": 48}


def test_external_shock_identifies_initial_defaults(hand_chain):
    direct = direct_loss_only(hand_chain, Scenario(external_impairment=0.25))
    # B equity = 50 - 0.25*200 = 0, so B defaults without a forced event.
    assert direct["initial_defaults"] == ["B"]
    assert direct["secondary_defaults"] == ["A"]
    assert direct["equity"]["C"] == 15
    assert direct["external_loss"] == 100


def test_boundaries_and_invalid_bank(hand_chain):
    assert direct_loss_only(hand_chain, Scenario())["default_count"] == 0
    full_recovery = direct_loss_only(hand_chain, Scenario(initial_defaults=["B"], recovery=1))
    assert full_recovery["defaults"] == ["B"]
    assert full_recovery["interbank_loss"] == 0
    exact_zero = direct_loss_only(hand_chain, Scenario(initial_defaults=["B"], recovery=0.5))
    assert exact_zero["secondary_defaults"] == ["A"]
    assert exact_zero["equity"]["A"] == 0
    with pytest.raises(ValueError, match="Unknown"):
        direct_loss_only(hand_chain, Scenario(initial_defaults=["missing"]))
