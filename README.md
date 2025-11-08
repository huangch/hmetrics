# hmetrics

Group-wise statistical plots (box/violin/point) with pairwise tests and significance annotations — in a familiar seaborn-style API.

* Stats: Mann–Whitney (nonparametric) or Welch’s t-test (parametric) via Pingouin, with multiple-testing correction (Holm, Bonferroni, FDR, …).
* Plots: box, violin, or point mean with error bars; optional raw points overlay (swarm/strip).
* Annotations: star annotations via statannotations.
* Ergonomics: pass a tidy DataFrame like seaborn; or use a CLI (hmetrics-plot) on a CSV.

## Installation

### From source (editable dev install)

'''
git clone https://example.com/hmetrics.git
cd hmetrics
pip install -e .
'''

### Dependencies

'''
pandas>=1.3
numpy>=1.21
matplotlib>=3.5
seaborn>=0.12
pingouin>=0.5.0
statannotations>=0.6.0
'''

Tip: seaborn>=0.12 is required because we use the new errorbar= API in pointplot.

## Quickstart (Python)

'''
import pandas as pd
from hmetrics import hmetrics_plot
'''

### Tidy example data

'''
df = pd.DataFrame({
    "group": ["A","A","A","B","B","B","C","C","C"],
    "value": [1.2, 0.9, 1.1, 2.1, 2.4, 1.9, 1.7, 1.8, 1.6],
})

fig, ax = hmetrics_plot(
    df=df, group="group", value="value",
    plot_kind="box",         # 'box', 'violin', or 'point'
    show_points="swarm",     # 'swarm', 'strip', or None
    nonparametric=True,      # True -> Mann–Whitney; False -> Welch t-test
    padjust="holm",          # 'holm','bonferroni','fdr_bh',...
    alpha=0.05,
    title="Group comparison",
    ylabel="Measured value",
)
'''

The function returns (fig, ax) and respects an external ax= if provided.

## Quickstart (CLI)

'''
The package exposes a simple command to work directly from CSV files.
hmetrics-plot \
  --csv data.csv \
  --group treatment \
  --value expression \
  --kind violin \
  --nonparametric \
  --padjust fdr_bh \
  --only-sig \
  --title "Treatment vs Expression" \
  --out plot.png
'''

CLI help:

'''
usage: hmetrics-plot [-h] --csv CSV --group GROUP --value VALUE
                     [--kind {box,violin,point}] [--nonparametric]
                     [--padjust PADJUST] [--alpha ALPHA] [--only-sig]
                     [--title TITLE] [--ylabel YLABEL] [--out OUT]
'''

You can also run: python -m hmetrics ...

## Data format

Provide a tidy DataFrame / CSV with at least two columns:

* *group (categorical): x-axis groups (e.g., “control”, “treat1”, “treat2”)
* value (numeric): y-axis measurements

Example data.csv:

'''
group,value
A,1.2
A,0.9
A,1.1
B,2.1
B,2.4
B,1.9
C,1.7
C,1.8
C,1.6
'''

## API

'''
hmetrics_plot(
    df,                     # pd.DataFrame with columns [group, value]
    group,                  # str: column name for x categories
    value,                  # str: column name for numeric y
    order=None,             # list[str] to control x order
    nonparametric=True,     # True -> Mann–Whitney; False -> Welch
    padjust="holm",         # pingouin style: 'holm','bonferroni','fdr_bh',...
    alpha=0.05,             # significance threshold for filtering annotations
    show_only_significant=False,
    plot_kind="box",        # 'box','violin','point'
    show_points="swarm",    # 'swarm','strip', or None (for box/violin)
    point_error=("ci", 95), # for pointplot: ('ci',95) or ('se',1)
    point_markersize=6,     # for pointplot
    point_linewidth=2.2,    # for pointplot
    figsize=(6,5),
    title=None,
    ylabel=None,
    ax=None                 # optional external matplotlib Axes
) -> (fig, ax)
'''

## Behavior highlights

* If order=None, categories are sorted alphabetically from df[group].
* Pairwise tests are computed across all pairs in order using Pingouin:

    . nonparametric=True → Mann–Whitney U
    . nonparametric=False → Welch’s t-test
	
* P-value column compatibility across Pingouin versions:

    . We detect "pval-corr" → else "p-corr" → else "pval-unc" → else "p-unc".

* Significance stars are drawn via statannotations (Annotator) if installed.

## Styling & seaborn parity

* The function calls sns.set(style="whitegrid", context="talk") for clean defaults.
* Accepts external ax and returns (fig, ax), matching matplotlib/seaborn patterns.
* For more control, set your theme globally before calling:

'''
import seaborn as sns
sns.set_theme(style="ticks", context="paper")
'''

## Reproducibility notes

* Statistical results depend on your data only; no randomization is used in the tests here.
* If you overlay swarm points, seaborn’s swarm layout is deterministic for a given input.

## Troubleshooting

* No stars drawn / Annotator not found

Ensure statannotations is installed:
pip install statannotations

* Seaborn complains about errorbar=

Upgrade seaborn to ≥ 0.12:
pip install -U seaborn

* Pingouin column mismatch (p-value)

We auto-detect the correct column name. If you use an older Pingouin, consider upgrading:
pip install -U pingouin

* Axes/title overlap

We place annotations inside the axes by default to avoid title clashes. If labels overlap, try a larger figsize or adjust line_offset/line_height in the code.

## Development

* Editable install: pip install -e .
* Suggested extras for development:

'''
pip install pytest ruff black
'''

## Minimal test (manual)

'''
def test_runs():
    import pandas as pd
    from hmetrics import hmetrics_plot
    df = pd.DataFrame({"group": list("AAABBBCCC"),
                       "value": [1.2,0.9,1.1,2.1,2.4,1.9,1.7,1.8,1.6]})
    fig, ax = hmetrics_plot(df, "group", "value", plot_kind="violin")
    assert fig is not None and ax is not None
'''

## Why this package?

* One call to get publication-ready group comparisons with statistics annotated.
* Seaborn-like interface: lower learning curve if you already use pandas/seaborn.
* Pingouin integration: simple access to common pairwise tests and p-adjust methods.

## Citation

If this tool helps your work, consider citing:

'''
@software{hmetrics2025,
  title = {hmetrics: Group-wise statistical plots with pairwise tests},
  version = {0.1.0},
  year = {2025},
  license = {Apache-2.0}
}
'''

## License

Apache License 2.0 — see LICENSE file.

## Changelog

* 0.1.0 — Initial release: box/violin/point plots, Pingouin pairwise tests, statannotations stars, CLI.