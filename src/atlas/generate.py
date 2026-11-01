"""Seeded synthetic loan networks with reconciled balance sheets."""

import networkx as nx
import numpy as np

from atlas.models import Bank, Dataset, Exposure, GenerateRequest


def generate(n=50, seed=42, topology="core_periphery") -> Dataset:
    """Build loans first, then reconcile both sides into funded balance sheets."""
    req = GenerateRequest(banks=n, seed=seed, topology=topology)
    rng = np.random.default_rng(req.seed)
    core_n = max(2, n // 5)
    if topology == "scale_free":
        raw = nx.barabasi_albert_graph(n, min(3, n - 1), seed=seed)
        pairs = [(u, v) if rng.random() < 0.5 else (v, u) for u, v in raw.edges]
    else:
        pairs = []
        for u in range(n):
            for v in range(n):
                p = (
                    0.08
                    if topology == "random"
                    else (0.65 if u < core_n and v < core_n else 0.18 if u < core_n or v < core_n else 0.015)
                )
                if u != v and rng.random() < p:
                    pairs.append((u, v))
    ids = [f"B{i + 1:03d}" for i in range(n)]
    loans = [
        Exposure(lender=ids[u], borrower=ids[v], amount=float(rng.uniform(5, 40))) for u, v in sorted(pairs)
    ]
    assets, liabilities = dict.fromkeys(ids, 0.0), dict.fromkeys(ids, 0.0)
    for e in loans:
        assets[e.lender] += e.amount
        liabilities[e.borrower] += e.amount
    banks = []
    for i, bid in enumerate(ids):
        # External assets cover net borrowing, leaving positive outside funding.
        external = float(rng.uniform(150, 700)) + liabilities[bid]
        total = external + assets[bid]
        equity = total * float(rng.uniform(0.06, 0.14))
        banks.append(
            Bank(
                id=bid,
                name=f"Atlas Synthetic Bank {i + 1:02d}",
                tier=("core" if i < core_n else "periphery") if topology == "core_periphery" else "other",
                external_assets=external,
                interbank_assets=assets[bid],
                interbank_liabilities=liabilities[bid],
                equity=equity,
                deposits=total - liabilities[bid] - equity,
            )
        )
    return Dataset(seed=seed, topology=topology, banks=banks, exposures=loans)
