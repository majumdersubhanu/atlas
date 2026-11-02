"""One loss ledger and exposure dataset shared by graph and matrix views.

Layout coordinates are presentation metadata, never inputs to the loss model.
"""

import networkx as nx

from atlas.analysis import exposure_matrix, graph_metrics
from atlas.baseline import direct_loss_only
from atlas.engine import furfine
from atlas.models import Bank, Dataset, Exposure, Scenario
from atlas.storage import dataset_hash


def teaching_fixture(name: str = "chain") -> Dataset:
    """Small, hand-checkable networks; amounts use synthetic teaching units."""
    if name == "chain":
        loans = [("A", "B", 100), ("C", "A", 80)]
        equity = {"A": 50, "B": 50, "C": 40}
    elif name == "branch":
        loans = [("A", "B", 100), ("C", "A", 80), ("D", "B", 50), ("E", "D", 40), ("F", "C", 30)]
        equity = {"A": 50, "B": 50, "C": 40, "D": 25, "E": 30, "F": 30}
    else:
        raise ValueError("Unknown fixture; choose chain or branch")
    banks = []
    for bid, capital in equity.items():
        lending = sum(v for lender, _, v in loans if lender == bid)
        borrowing = sum(v for _, borrower, v in loans if borrower == bid)
        external = 200 if bid == "B" else 100
        banks.append(
            Bank(
                id=bid,
                name=f"Bank {bid}",
                external_assets=external,
                interbank_assets=lending,
                interbank_liabilities=borrowing,
                equity=capital,
                deposits=external + lending - borrowing - capital,
            )
        )
    return Dataset(
        topology=f"teaching_{name}",
        units="synthetic teaching units",
        banks=banks,
        exposures=[Exposure(lender=a, borrower=b, amount=v) for a, b, v in loans],
    )


def visualization_payload(data: Dataset, scenario: Scenario) -> dict:
    """Return identical evidence for both encodings, with stable layout across shocks."""
    if len(data.banks) > 80:
        raise ValueError("Interactive comparison supports at most 80 banks")
    cascade = furfine(data, scenario)
    baseline = direct_loss_only(data, scenario)
    graph = nx.DiGraph()
    graph.add_nodes_from(b.id for b in data.banks)
    graph.add_edges_from((e.lender, e.borrower) for e in data.exposures)
    # Unweighted layout: large loans do not imply short geographic distances.
    positions = nx.spring_layout(graph, seed=42, weight=None, iterations=100)
    # The training chain has an explicit horizontal layout for legible arithmetic.
    # Formal study stimuli must use their separately frozen layout specification.
    if data.topology == "teaching_chain" and set(graph) == {"A", "B", "C"}:
        positions = {"C": (-1.0, 0.0), "A": (0.0, 0.0), "B": (1.0, 0.0)}
    matrix = exposure_matrix(data)
    default_round = {bid: r["round"] for r in cascade["rounds"] for bid in r["new_defaults"]}
    return {
        "dataset_hash": dataset_hash(data),
        "dataset": data.model_dump(mode="json"),
        "scenario": scenario.model_dump(mode="json"),
        "nodes": [
            {
                **b.model_dump(),
                "x": float(positions[b.id][0]),
                "y": float(positions[b.id][1]),
                "default_round": default_round.get(b.id),
            }
            for b in data.banks
        ],
        "edges": [e.model_dump() for e in data.exposures],
        "matrix": {"ids": list(matrix.index), "values": matrix.to_numpy().tolist()},
        "cascade": cascade,
        "baseline": baseline,
        "metrics": graph_metrics(data),
        "comparison": {
            "additional_defaults": cascade["default_count"] - baseline["default_count"],
            "additional_interbank_loss": cascade["interbank_loss"] - baseline["interbank_loss"],
            "visualization_effect": "not evaluated; requires human participants",
        },
        "conventions": {
            "loan_direction": "lender → borrower",
            "loss_direction": "borrower → surviving lender",
            "matrix": "rows = lenders; columns = borrowers; cells = original loan amounts",
            "rounds": "computational rounds, not calendar time",
            "interpretation": "Synthetic conditional experiment; not a historical failure prediction",
        },
    }
