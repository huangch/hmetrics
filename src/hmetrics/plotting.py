from __future__ import annotations
import itertools as it
from typing import Iterable, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pingouin as pg

try:
    from statannotations.Annotator import Annotator
    _HAS_ANNOT = True
except Exception:
    # Graceful degrade if statannotations is missing
    _HAS_ANNOT = False

def hmetrics_plot(
    df: pd.DataFrame,
    group: str,
    value: str,
    order: Optional[Iterable[str]] = None,
    nonparametric: bool = True,            # True -> Mann–Whitney; False -> Welch t-test
    padjust: str = "holm",                 # 'holm','bonferroni','fdr_bh',...
    alpha: float = 0.05,
    show_only_significant: bool = False,
    plot_kind: str = "box",                # 'box', 'point', or 'violin'
    show_points: Optional[str] = "swarm",  # for box/violin: 'swarm','strip', or None
    point_error: Tuple[str, float] = ("ci", 95),  # for pointplot: ('ci',95) or ('se',1)
    point_markersize: float = 6,           # for pointplot
    point_linewidth: float = 2.2,          # for pointplot
    figsize: Tuple[float, float] = (6, 5),
    title: Optional[str] = None,
    ylabel: Optional[str] = None,
    ax: Optional[plt.Axes] = None          # allow external axes
):
    """
    Draw a group-wise statistical plot with pairwise tests and significance annotations.

    Parameters
    ----------
    df : DataFrame
        Must contain columns [group (categorical), value (numeric)] in tidy form.
    group : str
        Categorical column name (x-axis).
    value : str
        Numeric column name (y-axis).
    order : list[str] | None
        Category order on the x-axis. If None, alphabetical order of unique levels.
    nonparametric : bool
        If True use Mann–Whitney; else Welch's t-test.
    padjust : str
        Multiple-testing correction method (pingouin style).
    alpha : float
        Significance threshold.
    show_only_significant : bool
        If True, annotate only pairs with p < alpha.
    plot_kind : {'box','violin','point'}
        Plot style.
    show_points : {'swarm','strip',None}
        Overlay raw points for box/violin.
    point_error : tuple
        Seaborn error spec for pointplot, e.g. ('ci',95) or ('se',1).
    point_markersize : float
        Marker size for pointplot.
    point_linewidth : float
        Line width for pointplot.
    figsize : (w,h)
        Figure size if ax is None.
    title : str | None
        Title text.
    ylabel : str | None
        Y-axis label; default to `value`.
    ax : matplotlib.axes.Axes | None
        Existing axes to draw on.

    Returns
    -------
    (fig, ax)
    """
    # ---- order categories on x ----
    if order is None:
        order = sorted(df[group].dropna().unique().tolist())
    idx = {lvl: i for i, lvl in enumerate(order)}

    # ---- pairwise tests with multiple-testing correction ----
    tests = pg.pairwise_tests(
        data=df, dv=value, between=group,
        parametric=not nonparametric,
        padjust=padjust, alternative="two-sided"
    )
    # keep only requested levels
    tests = tests[tests["A"].isin(order) & tests["B"].isin(order)].copy()

    # normalize pairs so (A,B) is always left<right by order
    tests["pair"] = tests.apply(
        lambda r: (r.A, r.B) if idx[r.A] < idx[r.B] else (r.B, r.A), axis=1
    )

    # column name differences across Pingouin versions
    if "pval-corr" in tests.columns:
        pcol = "pval-corr"
    elif "p-corr" in tests.columns:
        pcol = "p-corr"
    elif "pval-unc" in tests.columns:
        pcol = "pval-unc"
    else:
        pcol = "p-unc"

    all_pairs = list(it.combinations(order, 2))
    p_lookup  = tests.set_index("pair")[pcol].to_dict()
    if show_only_significant:
        pairs = [p for p in all_pairs if p_lookup.get(p, 1.0) < alpha]
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
    kind = str(plot_kind).lower()
    if kind == "box":
        showf = (show_points is None)  # hide fliers if overlaying points
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
                color="black", size=3.5, jitter=0.28, alpha=0.85,
                zorder=2, ax=ax
            )

    elif kind == "violin":
        sns.violinplot(
            data=df, x=group, y=value, order=order,
            inner="quartile", cut=0, linewidth=1.5,
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
                color="black", size=3.5, jitter=0.28, alpha=0.85,
                zorder=2, ax=ax
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

    # ---- significance annotations (inside axes) ----
    if pairs and _HAS_ANNOT:
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
    plt.xticks(rotation=15, ha="right", fontsize=10)
    plt.yticks(fontsize=10)
    sns.despine()
    if created_ax:
        plt.tight_layout()
    return fig, ax
