from __future__ import annotations
import itertools as it
import numpy as np
import pandas as pd
import pingouin as pg

def run_pairwise_tests(
    df: pd.DataFrame,
    group: str,
    value: str,
    order: list[str],
    *,
    nonparametric: bool,
    padjust: str,
) -> pd.DataFrame:
    """
    Wrapper around pingouin.pairwise_tests with robust column handling across versions.
    Returns a tidy DataFrame with columns: ['A','B','pair','pval'] filtered to 'order'.
    """
    tests = pg.pairwise_tests(
        data=df,
        dv=value,
        between=group,
        parametric=not nonparametric,
        padjust=padjust,
        alternative="two-sided",
    )

    # Filter to requested order
    tests = tests[tests["A"].isin(order) & tests["B"].isin(order)].copy()

    # Normalize pair direction (left<right) so dict lookups are stable
    idx = {lvl: i for i, lvl in enumerate(order)}
    tests["pair"] = tests.apply(
        lambda r: (r.A, r.B) if idx[r.A] < idx[r.B] else (r.B, r.A), axis=1
    )

    # Pingouin p-value column may vary
    pcol = (
        "pval-corr" if "pval-corr" in tests.columns else
        "p-corr"    if "p-corr"    in tests.columns else
        "pval-unc"  if "pval-unc"  in tests.columns else
        "p-unc"
    )
    tests = tests.assign(pval=tests[pcol]).loc[:, ["A", "B", "pair", "pval"]]

    # Ensure all pairs exist (fill with NaN if missing)
    all_pairs = list(it.combinations(order, 2))
    lookup = {p: np.nan for p in all_pairs}
    lookup.update({tuple(p): pv for p, pv in zip(tests["pair"], tests["pval"])})
    out = pd.DataFrame({
        "A": [p[0] for p in all_pairs],
        "B": [p[1] for p in all_pairs],
        "pair": all_pairs,
        "pval": [lookup[p] for p in all_pairs],
    })
    return out