"""Tests for the exported figures.

The headline test here is `test_flipper_legend_binds_labels_to_correct_colours`.
A previous revision overrode the histogram legend with a literal label list
(`labels=["Gentoo", "Chinstrap", "Adélie"]`), which silently remapped two of the
three species onto the wrong colours. The figure was published in the README and
the bug survived a manual QA pass, so it is pinned by an automated assertion.
"""

import matplotlib.pyplot as plt
import pytest

from src.generate_charts import generate_all_portfolio_charts
from src.visualization_utils import (
    get_species_palette,
    plot_bill_dimensions_simpson_paradox,
    plot_body_mass_by_species_and_sex,
    plot_correlation_heatmap,
    plot_flipper_length_histogram,
    plot_species_distribution,
    setup_visualization_theme,
)

EXPECTED_CHARTS = [
    "01_species_distribution.png",
    "02_bill_scatter.png",
    "03_mass_by_species.png",
    "04_correlation_heatmap.png",
    "05_flipper_histogram.png",
]


@pytest.fixture(autouse=True)
def theme():
    setup_visualization_theme(dpi=120, export_dpi=150, palette="colorblind")
    yield
    plt.close("all")


def _legend_pairs(ax):
    """Returns [(label, rgb), ...] as actually rendered in the legend."""
    legend = ax.get_legend()
    assert legend is not None, "figure must carry a legend"
    pairs = []
    for handle, text in zip(legend.legend_handles, legend.get_texts()):
        facecolor = handle.get_facecolor()
        rgb = facecolor[0] if hasattr(facecolor[0], "__len__") else facecolor
        pairs.append((text.get_text(), tuple(round(c, 3) for c in rgb[:3])))
    return pairs


def test_flipper_legend_binds_labels_to_correct_colours(clean_df, tmp_path):
    """Every legend label must point at its own species' colour."""
    palette = get_species_palette(clean_df)
    fig = plot_flipper_length_histogram(
        clean_df, save_path=str(tmp_path / "hist.png")
    )

    pairs = _legend_pairs(fig.axes[0])

    assert {label for label, _ in pairs} == set(palette)
    for label, rgb in pairs:
        expected = tuple(round(c, 3) for c in palette[label][:3])
        assert rgb == expected, (
            f"legend entry {label!r} is drawn in {rgb}, but {label} is "
            f"plotted in {expected} - labels and handles are desynchronised"
        )


def test_flipper_legend_does_not_drop_a_species(clean_df, tmp_path):
    fig = plot_flipper_length_histogram(
        clean_df, save_path=str(tmp_path / "hist.png")
    )
    labels = [label for label, _ in _legend_pairs(fig.axes[0])]
    assert sorted(labels) == ["Adelie", "Chinstrap", "Gentoo"]


def test_species_distribution_legend_matches_palette(clean_df, tmp_path):
    palette = get_species_palette(clean_df)
    fig = plot_species_distribution(
        clean_df, save_path=str(tmp_path / "dist.png")
    )
    for label, rgb in _legend_pairs(fig.axes[0]):
        assert rgb == tuple(round(c, 3) for c in palette[label][:3])


def test_simpson_figure_draws_within_and_pooled_fits(clean_df, tmp_path):
    """The paradox needs 3 within-species fits plus 1 pooled fit to be visible.

    A scatter plot on its own does not demonstrate Simpson's Paradox, which is
    what the earlier version of this figure shipped.
    """
    fig = plot_bill_dimensions_simpson_paradox(
        clean_df, save_path=str(tmp_path / "simpson.png")
    )
    ax = fig.axes[0]

    # Seaborn's style= parameter registers empty marker proxies in ax.lines;
    # only artists with real data are regression fits.
    fits = [ln for ln in ax.lines if len(ln.get_xdata()) > 1]
    assert len(fits) == 4, "expected 3 species fits + 1 pooled fit"

    dashed = [ln for ln in fits if ln.get_linestyle() in ("--", (0, (6.4, 1.6)))]
    assert len(dashed) == 1, "the pooled fit must be visually distinct (dashed)"

    # The pooled fit must slope down while every species fit slopes up.
    def slope(line):
        x, y = line.get_xdata(), line.get_ydata()
        return (y[-1] - y[0]) / (x[-1] - x[0])

    pooled_slope = slope(dashed[0])
    species_slopes = [slope(ln) for ln in fits if ln is not dashed[0]]

    assert pooled_slope < 0, "pooled fit should slope negative"
    assert all(s > 0 for s in species_slopes), "every species fit should slope positive"

    labels = [t.get_text() for t in ax.get_legend().get_texts()]
    assert any("Pooled" in label for label in labels)


def test_boxplot_and_heatmap_render(clean_df, tmp_path):
    mass = plot_body_mass_by_species_and_sex(
        clean_df, save_path=str(tmp_path / "mass.png")
    )
    assert (tmp_path / "mass.png").exists()
    assert mass.axes[0].get_ylabel() == "Body Mass (g)"

    heat = plot_correlation_heatmap(
        clean_df, save_path=str(tmp_path / "corr.png")
    )
    ticks = [t.get_text() for t in heat.axes[0].get_xticklabels()]
    assert "Flipper Length (mm)" in ticks, "axis labels must be human-readable"


def test_full_export_pipeline_writes_all_five_charts(tmp_path):
    saved = generate_all_portfolio_charts(output_dir=str(tmp_path))
    assert len(saved) == 5
    for name in EXPECTED_CHARTS:
        chart = tmp_path / name
        assert chart.exists(), f"{name} was not exported"
        assert chart.stat().st_size > 20_000, f"{name} looks truncated"
