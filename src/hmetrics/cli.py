from __future__ import annotations
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from .plotting import hmetrics_plot

def main():
    p = argparse.ArgumentParser(
        description="Plot group-wise metrics with significance annotations."
    )
    p.add_argument("--csv", required=True, help="Path to CSV with tidy data")
    p.add_argument("--group", required=True, help="Categorical column name")
    p.add_argument("--value", required=True, help="Numeric column name")
    p.add_argument("--kind", default="box", choices=["box","violin","point"])
    p.add_argument("--nonparametric", action="store_true", help="Use Mann–Whitney instead of Welch")
    p.add_argument("--padjust", default="holm")
    p.add_argument("--alpha", type=float, default=0.05)
    p.add_argument("--only-sig", action="store_true", help="Annotate only significant pairs")
    p.add_argument("--title", default=None)
    p.add_argument("--ylabel", default=None)
    p.add_argument("--out", default=None, help="Save figure to this path (e.g., out.png)")
    args = p.parse_args()

    df = pd.read_csv(args.csv)
    fig, ax = hmetrics_plot(
        df=df, group=args.group, value=args.value,
        plot_kind=args.kind,
        nonparametric=args.nonparametric,
        padjust=args.padjust,
        alpha=args.alpha,
        show_only_significant=args.only_sig,
        title=args.title,
        ylabel=args.ylabel,
    )
    if args.out:
        fig.savefig(args.out, dpi=300, bbox_inches="tight")
    else:
        plt.show()
