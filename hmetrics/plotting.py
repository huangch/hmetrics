from __future__ import annotations
import itertools as it
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Tuple

from statannotations.Annotator import Annotator
from .stats import run_pairwise_tests

def plot_hmetrics(
    df: pd.DataFrame, group: str, value: str,
    order: Optional[list] = None,
    nonparametric: bool = True,        # True -> Mann–Whitney; False -> Welch t-test
    padjust: str = "holm",             # 'holm','bonferroni','fdr_bh',...
    alpha: float = 0.05,
    show_only_significant: bool = False,
    plot_kind: str = "box",            # 'box', 'point', or 'violin'
    show_points: Optional[str] = "swarm",  # for box/violin: 'swarm','strip', or None
    point_error: Tuple[str, float] = ("ci", 95),   # for pointplot: ('ci',95) or ('se',1)
    point_markersize: float = 6.0,     # for pointplot
    point_linewidth: float = 2.2,      # for pointplot
    figsize: Tuple[float, float] = (6, 5),
    title: Optional[str] = None,
    ylabel: Optional[str] = None,
    ax: Optional[plt.Axes] = None      # external axes support
):
    """
    df: DataFrame with columns [group (categorical), value (numeric)]
    Returns: (fig, ax, tests_df) where tests_df has columns ['A','B','pair','pval'].
    """
    # ---- order on x ----
    if order is None:
        order = sorted(pd.Series(df[group].dropna().unique()).tolist())
    idx = {lvl: i for i, lvl in enumerate(order)}

    # ---- pairwise tests with multiple-testing correction ----
    tests_df = run_pairwise_tests(
        df=df, group=group, value=value, order=order,
        nonparametric=nonparametric, padjust=padjust
    )
    all_pairs = list(it.combinations(order, 2))
    p_lookup = dict(zip(tests_df["pair"], tests_df["pval"]))
    if show_only_significant:
        pairs = [p for p in all_pairs if (p_lookup.get(p, 1.0) < alpha)]
    else:
        pairs = all_pairs
    pvals = [p_lookup.get(p, np.nan) for p in pairs]

    # ---- axes / figure ----
    sns.set(style="whitegrid", context="talk")
    created_ax = False
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
        created_ax = True
    else:
        fig = ax.figure

    # ---- plotting ----
    kind = plot_kind.lower()
    if kind == "box":
        showf = (show_points is None)
        sns.boxplot(
            data=df, x=group, y=value, order=order,
            width=0.5, showfliers=showf,
            boxprops=dict(linewidth=2, alpha=0.9),
            whiskerprops=dict(linewidth=2), capprops=dict(linewidth=2),
            medianprops=dict(linewidth=2.2, color="black"),
            ax=ax, zorder=1
        )
        if show_points == "swarm":
            sns.swarmplot(
                data=df, x=group, y=value, order=order,
                color="black", size=3.5, linewidth=0, zorder=2, ax=ax
            )
        elif show_points == "strip":
            sns.stripplot(
                data=df, x=group, y=value, order=order,
                color="black", size=3.5, jitter=0.28, alpha=0.85, zorder=2, ax=ax
            )

    elif kind == "violin":
        sns.violinplot(
            data=df, x=group, y=value, order=order,
            inner="quartile", cut=0, linewidth=1.5, ax=ax, zorder=1
        )
        if show_points == "swarm":
            sns.swarmplot(
                data=df, x=group, y=value, order=order,
                color="black", size=3.5, linewidth=0, zorder=2, ax=ax
            )
        elif show_points == "strip":
            sns.stripplot(
                data=df, x=group, y=value, order=order,
                color="black", size=3.5, jitter=0.28, alpha=0.85, zorder=2, ax=ax
            )

    elif kind == "point":
        sns.pointplot(
            data=df, x=group, y=value, order=order,
            estimator="mean", errorbar=point_error,
            markers="o", linestyles="-",
            markersize=point_markersize, linewidth=point_linewidth,
            capsize=0.18, err_kws={"linewidth": 2},
            ax=ax, zorder=2
        )
    else:
        raise ValueError("plot_kind must be 'box', 'point', or 'violin'.")

    # ---- significance annotations (inside to avoid title overlap) ----
    if pairs:
        annot = Annotator(ax, pairs, data=df, x=group, y=value, order=order)
        annot.configure(
            test=None,  # we pass p-values directly
            text_format="star", show_test_name=False,
            pvalue_thresholds=[(1e-4,"****"), (1e-3,"***"), (1e-2,"**"), (5e-2,"*"), (1,"ns")],
            loc="inside", line_height=0.02, line_offset=0.02
        )
        annot.set_pvalues_and_annotate(pvalues=pvals)

    # ---- cosmetics ----
    if title:
        ax.set_title(title, fontsize=12, weight="bold", pad=12)
    ax.set_xlabel("")
    ax.set_ylabel(ylabel or value, fontsize=10)
    ax.tick_params(axis="x", labelrotation=15, labelsize=10)
    ax.tick_params(axis="y", labelsize=10)
    sns.despine()
    if created_ax:
        fig.tight_layout()

    return fig, ax, tests_df