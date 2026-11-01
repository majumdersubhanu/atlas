"""Descriptive network measurements and explicitly conditional stress experiments.

These functions do not estimate historical exposures or identify causal topology
 effects. Loan arrows point lender -> borrower; credit losses travel in reverse.
"""

from collections.abc import Iterable

import networkx as nx
import numpy as np
import pandas as pd

from atlas.engine import furfine
from atlas.generate import generate
from atlas.models import Dataset, Scenario


def exposure_matrix(data: Dataset) -> pd.DataFrame:
    """Return A[i,j] = loan from i to j, with zero diagonal and stable ID order."""
    ids = [bank.id for bank in data.banks]
    matrix = pd.DataFrame(0.0, index=ids, columns=ids)
    for loan in data.exposures:
        matrix.loc[loan.lender, loan.borrower] = loan.amount
    matrix.index.name = "lender"
    matrix.columns.name = "borrower"
    return matrix


def graph_metrics(data: Dataset) -> dict:
    """Measure directed degrees, strengths and unweighted normalized betweenness.

    Exposure amounts are not path lengths. Betweenness uses hop distances and
    is a structural descriptor, not a systemic-risk estimate. Isolates remain
    in the graph and denominator of directed density E/[N(N-1)].
    """
    graph = nx.DiGraph()
    graph.add_nodes_from(bank.id for bank in data.banks)
    graph.add_weighted_edges_from((e.lender, e.borrower, e.amount) for e in data.exposures)
    centrality = nx.betweenness_centrality(graph, normalized=True, weight=None)
    return {
        "banks": len(graph),
        "edges": graph.number_of_edges(),
        "directed_density": nx.density(graph),
        "weak_components": nx.number_weakly_connected_components(graph),
        "strong_components": nx.number_strongly_connected_components(graph),
        "bank_metrics": [
            {
                "id": bid,
                "creditor_count": graph.in_degree(bid),
                "borrower_count": graph.out_degree(bid),
                "borrowing": float(graph.in_degree(bid, weight="weight")),
                "lending": float(graph.out_degree(bid, weight="weight")),
                "unweighted_betweenness": centrality[bid],
            }
            for bid in graph
        ],
    }


def impact_ranking(data: Dataset, recovery: float = 0.4) -> pd.DataFrame:
    """Force each bank to default separately on unchanged starting balance sheets.

    No external shock is applied. Rank by secondary defaults, then posted
    interbank loss, then ID. This is conditional scenario impact, not a failure
    probability, additive risk attribution, or a regulatory systemic score.
    """
    rows = []
    for bank in data.banks:
        result = furfine(data, Scenario(recovery=recovery, initial_defaults=[bank.id]))
        rows.append(
            {
                "bank_id": bank.id,
                "secondary_defaults": len(result["secondary_defaults"]),
                "total_defaults": result["default_count"],
                "posted_interbank_loss": result["interbank_loss"],
            }
        )
    return (
        pd.DataFrame(rows)
        .sort_values(
            ["secondary_defaults", "posted_interbank_loss", "bank_id"],
            ascending=[False, False, True],
        )
        .reset_index(drop=True)
    )


def monte_carlo_summary(trials: pd.DataFrame) -> dict:
    """Summarize independent simulation draws conditional on model parameters.

    MCSE is sample standard deviation / sqrt(n), estimating numerical error in
    the sample mean, not model or parameter uncertainty. For n=1 it is undefined
    (None). Quantiles use the empirical inverse CDF; q95 is not a confidence
    bound for the mean and no tail-loss or calibrated VaR claim is made.
    """
    columns = ["defaults", "secondary_defaults", "interbank_loss"]
    if len(trials) == 0:
        raise ValueError("At least one Monte Carlo trial is required")
    values = trials[columns].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Trial outcomes must be finite and nonnegative")
    summary = {}
    for name in columns:
        vector = trials[name].to_numpy(dtype=float)
        summary[name] = {
            "mean": float(vector.mean()),
            "mcse_mean": float(vector.std(ddof=1) / np.sqrt(len(vector))) if len(vector) > 1 else None,
            "empirical_q05": float(np.quantile(vector, 0.05, method="inverted_cdf")),
            "empirical_median": float(np.quantile(vector, 0.5, method="inverted_cdf")),
            "empirical_q95": float(np.quantile(vector, 0.95, method="inverted_cdf")),
        }
    return {"trials": len(trials), "conditional_summary": summary}


def topology_ensemble(
    seeds: Iterable[int] = range(10), n: int = 50, impairment: float = 0.1, recovery: float = 0.4
) -> pd.DataFrame:
    """Run three generator families across seeds; return every replicate.

    These presets differ in density, balance sheets and exposure totals as well
    as topology. Differences are descriptive generator-family comparisons, not
    isolated causal effects of topology. Seed numbers across families do not
    establish matched balance sheets or common random variates.
    """
    seeds = list(seeds)
    if not seeds or len(seeds) != len(set(seeds)):
        raise ValueError("Provide at least one unique seed; duplicate replicates are not independent")
    scenario = Scenario(external_impairment=impairment, recovery=recovery)
    rows = []
    for family in ["core_periphery", "random", "scale_free"]:
        for seed in seeds:
            data = generate(n, seed, family)
            result = furfine(data, scenario)
            rows.append(
                {
                    "family": family,
                    "seed": seed,
                    "banks": n,
                    "edges": len(data.exposures),
                    "directed_density": len(data.exposures) / (n * (n - 1)),
                    "total_exposure": sum(e.amount for e in data.exposures),
                    "total_assets": sum(b.total_assets for b in data.banks),
                    "total_equity": sum(b.equity for b in data.banks),
                    "initial_defaults": len(result["initial_defaults"]),
                    "secondary_defaults": len(result["secondary_defaults"]),
                    "total_defaults": result["default_count"],
                    "default_fraction": result["default_count"] / n,
                    "posted_interbank_loss": result["interbank_loss"],
                }
            )
    return pd.DataFrame(rows)
