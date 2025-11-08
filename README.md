# hmetrics

Group-wise statistical plots (box/violin/point) with pairwise tests and significance annotations — in a familiar **seaborn-style** API.

- **Stats**: Mann–Whitney (nonparametric) or Welch’s t-test (parametric) via **Pingouin**, with multiple-testing correction (Holm, Bonferroni, FDR, etc).
- **Plots**: box, violin, or point mean with error bars; optional raw points overlay (swarm/strip).
- **Annotations**: star annotations via **statannotations**.
- **Ergonomics**: pass a tidy `DataFrame` like seaborn; or use a CLI (`hmetrics-plot`) on a CSV.

---

## Installation

### From source (editable dev install)

```bash
git clone https://example.com/hmetrics.git
cd hmetrics
pip install -e .
````

### Dependencies

```
pandas>=1.3
numpy>=1.21
matplotlib>=3.5
seaborn>=0.12
pingouin>=0.5.0
statannotations>=0.6.0
```

> Tip: `seaborn>=0.12` is required because we use the new `errorbar=` API in `pointplot`.

---

## Quickstart (Python)

```python
import pandas as pd
from hmetrics import hmetrics_plot

df = pd.DataFrame({
    "group": ["A","A","A","B","B","B","C","C","C"],
    "value": [1.2, 0.9, 1.1, 2.1, 2.4, 1.9, 1.7, 1.8, 1.6],
})

fig, ax = hmetrics_plot(
    df=df, group="group", value="value",
    plot_kind="box",
    show_points="swarm",
    nonparametric=True,
    padjust="holm",
    alpha=0.05,
    title="Group comparison",
    ylabel="Measured value",
)
```

The function returns `(fig, ax)` and respects an external `ax=` if provided.

---

## Quickstart (CLI)

```bash
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
```

CLI help:

```
usage: hmetrics-plot [-h] --csv CSV --group GROUP --value VALUE
                     [--kind {box,violin,point}] [--nonparametric]
                     [--padjust PADJUST] [--alpha ALPHA] [--only-sig]
                     [--title TITLE] [--ylabel YLABEL] [--out OUT]
```

You can also run:

```bash
python -m hmetrics ...
```

---

## Data format

Provide a **tidy** DataFrame or CSV with at least two columns:

Example `data.csv`:

```csv
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
```

---

## API

```python
hmetrics_plot(
    df, group, value,
    order=None,
    nonparametric=True,
    padjust="holm",
    alpha=0.05,
    show_only_significant=False,
    plot_kind="box",
    show_points="swarm",
    point_error=("ci",95),
    point_markersize=6,
    point_linewidth=2.2,
    figsize=(6,5),
    title=None,
    ylabel=None,
    ax=None
) -> (fig, ax)
```

**Behavior highlights**

* If `order=None`, categories are sorted alphabetically from `df[group]`.
* Pairwise tests are computed using **Pingouin**:

  * `nonparametric=True` → Mann–Whitney U
  * `nonparametric=False` → Welch’s t-test
* Automatically detects correct p-value column name across Pingouin versions.
* Significance stars drawn via **statannotations** if installed.

---

## Styling & seaborn parity

* Calls `sns.set(style="whitegrid", context="talk")` by default.
* Accepts external `ax` and returns `(fig, ax)` like seaborn/matplotlib.
* For global style control:

```python
import seaborn as sns
sns.set_theme(style="ticks", context="paper")
```

---

## Reproducibility

* Results are deterministic (no randomization in tests).
* Seaborn’s swarmplot placement is deterministic for a given input.

---

## Troubleshooting

* **No stars drawn** → `pip install statannotations`
* **Seaborn error** → upgrade seaborn≥0.12
* **Pingouin mismatch** → upgrade pingouin≥0.5
* **Title overlap** → increase `figsize` or adjust offsets in code.

---

## Development

```bash
pip install -e .
pip install pytest ruff black
```

### Minimal test (manual)

```python
import pandas as pd
from hmetrics import hmetrics_plot

df = pd.DataFrame({
    "group": list("AAABBBCCC"),
    "value": [1.2,0.9,1.1,2.1,2.4,1.9,1.7,1.8,1.6]
})
fig, ax = hmetrics_plot(df, "group", "value", plot_kind="violin")
assert fig is not None and ax is not None
```

---

## Why this package?

* One call to get publication-ready group comparisons with significance annotations.
* Familiar seaborn-like syntax.
* Built-in Pingouin integration for robust pairwise tests.

---

## Citation

If this tool helps your work, consider citing:

```bibtex
@software{hmetrics2025,
  title = {hmetrics: Group-wise statistical plots with pairwise tests},
  version = {0.1.0},
  year = {2025},
  license = {Apache-2.0}
}
```

---

## License

Apache License 2.0

---

## Changelog

* **0.1.0** — Initial release: box/violin/point plots, Pingouin pairwise tests, statannotations stars, CLI.
