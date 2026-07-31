"""
Palmer Penguins Visualization Helper Module
Author: Jean Carlos Rojas Herrera (RojasJeanDL)
Description:
    Provides standardized plotting helpers using Seaborn and Matplotlib
    to produce publication-ready statistical figures for EDA and README.
"""

import os
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.lines import Line2D

# Human-readable axis labels for the raw snake_case dataset columns.
FEATURE_LABELS: Dict[str, str] = {
    "bill_length_mm": "Bill Length (mm)",
    "bill_depth_mm": "Bill Depth (mm)",
    "flipper_length_mm": "Flipper Length (mm)",
    "body_mass_g": "Body Mass (g)",
}


def setup_visualization_theme(
    dpi: int = 120, export_dpi: int = 150, palette: str = "colorblind"
) -> None:
    """Configures global Matplotlib and Seaborn styles for executive charts.

    Args:
        dpi (int): On-screen figure resolution.
        export_dpi (int): Resolution used when figures are written to disk.
            Applied via ``savefig.dpi`` so that exports honour this setting
            instead of a hardcoded value inside the save helper.
        palette (str): Seaborn palette name (colorblind-accessible by default).
    """
    sns.set_theme(style="whitegrid", palette=palette)
    plt.rcParams["figure.dpi"] = dpi
    plt.rcParams["savefig.dpi"] = export_dpi
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.titlesize"] = 13
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["axes.labelsize"] = 11
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10


def get_species_palette(df: pd.DataFrame) -> Dict[str, tuple]:
    """Maps every species to a stable colour from the active Seaborn palette.

    Seaborn derives its hue order from order of appearance, so colours are
    bound explicitly here to guarantee that a species keeps the same colour
    across every figure regardless of row order or filtering.
    """
    species_order: List[str] = sorted(df["species"].dropna().unique())
    colors = sns.color_palette(n_colors=len(species_order))
    return dict(zip(species_order, colors))


def save_or_show_chart(
    fig: plt.Figure, save_path: Optional[str] = None
) -> None:
    """Saves figure to disk if save_path is provided, otherwise displays it."""
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        # dpi is intentionally omitted: it resolves to rcParams["savefig.dpi"],
        # which setup_visualization_theme() owns.
        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()


def plot_species_distribution(
    df: pd.DataFrame, save_path: Optional[str] = None
) -> plt.Figure:
    """Plots species distribution across the three Palmer Archipelago islands."""
    palette = get_species_palette(df)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.countplot(
        data=df,
        x="island",
        hue="species",
        hue_order=list(palette.keys()),
        palette=palette,
        # Seaborn desaturates categorical fills to 75% by default, which would
        # render "Adelie blue" differently here than in the scatter and
        # histogram figures. Full saturation keeps species colours identical
        # across all five exported charts.
        saturation=1.0,
        ax=ax,
        edgecolor="black",
    )
    ax.set_title("Penguin Species Distribution Across Antarctic Islands")
    ax.set_xlabel("Antarctic Island (Palmer Archipelago)")
    ax.set_ylabel("Number of Observations")
    ax.legend(title="Species", frameon=True)
    plt.tight_layout()
    save_or_show_chart(fig, save_path)
    return fig


def plot_bill_dimensions_simpson_paradox(
    df: pd.DataFrame, save_path: Optional[str] = None
) -> plt.Figure:
    """Plots Bill Length vs Bill Depth illustrating Simpson's Paradox.

    The paradox is only visible when both regression layers are drawn: one
    OLS fit per species (all positive) against the pooled fit over the whole
    population (negative). A scatter plot alone does not demonstrate it.
    """
    palette = get_species_palette(df)
    species_order = list(palette.keys())

    fig, ax = plt.subplots(figsize=(8.5, 6.4))
    sns.scatterplot(
        data=df,
        x="bill_length_mm",
        y="bill_depth_mm",
        hue="species",
        hue_order=species_order,
        palette=palette,
        style="species",
        style_order=species_order,
        s=70,
        alpha=0.75,
        ax=ax,
        edgecolor="w",
    )

    # Layer 1 — within-species OLS fits (the true biological signal).
    r_within = {}
    for species in species_order:
        subset = df[df["species"] == species]
        r_within[species] = subset["bill_length_mm"].corr(
            subset["bill_depth_mm"]
        )
        sns.regplot(
            data=subset,
            x="bill_length_mm",
            y="bill_depth_mm",
            scatter=False,
            ci=None,
            ax=ax,
            color=palette[species],
            line_kws={"linewidth": 2.4},
        )

    # Layer 2 — pooled OLS fit across all species (the aggregation artefact).
    r_pooled = df["bill_length_mm"].corr(df["bill_depth_mm"])
    sns.regplot(
        data=df,
        x="bill_length_mm",
        y="bill_depth_mm",
        scatter=False,
        ci=None,
        ax=ax,
        color="#404040",
        line_kws={"linewidth": 2.8, "linestyle": "--"},
    )

    ax.set_title("Bill Length vs. Bill Depth — Simpson's Paradox")
    ax.set_xlabel(FEATURE_LABELS["bill_length_mm"])
    ax.set_ylabel(FEATURE_LABELS["bill_depth_mm"])

    # Seaborn's own legend swallows labels passed through regplot's line_kws,
    # so the pooled fit is added as an explicit proxy handle instead.
    handles, labels = ax.get_legend_handles_labels()
    handles.append(
        Line2D([0], [0], color="#404040", linewidth=2.8, linestyle="--")
    )
    labels.append(f"Pooled fit (r = {r_pooled:.2f})")
    ax.legend(
        handles,
        labels,
        title="Species & Trend",
        frameon=True,
        framealpha=1.0,
        loc="upper left",
    ).set_zorder(10)

    within_txt = "  ·  ".join(
        f"{sp} r = {r:+.2f}" for sp, r in r_within.items()
    )
    ax.text(
        0.5,
        -0.15,
        f"Within-species (all positive):  {within_txt}"
        f"\nPooled across species:  r = {r_pooled:+.2f}  →  slope inverts",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=9.5,
        color="#333333",
        bbox=dict(
            boxstyle="round,pad=0.55",
            facecolor="#f4f4f5",
            edgecolor="#d4d4d8",
        ),
    )

    plt.tight_layout()
    save_or_show_chart(fig, save_path)
    return fig


def plot_body_mass_by_species_and_sex(
    df: pd.DataFrame, save_path: Optional[str] = None
) -> plt.Figure:
    """Plots Boxplot of Body Mass by Species and Sex."""
    df_sex = df.dropna(subset=["sex"]).copy()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(
        data=df_sex,
        x="species",
        order=sorted(df_sex["species"].dropna().unique()),
        y="body_mass_g",
        hue="sex",
        ax=ax,
        linewidth=1.2,
    )
    ax.set_title("Body Mass Distribution by Penguin Species & Sex")
    ax.set_xlabel("Penguin Species")
    ax.set_ylabel(FEATURE_LABELS["body_mass_g"])
    ax.legend(title="Sex", frameon=True)
    plt.tight_layout()
    save_or_show_chart(fig, save_path)
    return fig


def plot_correlation_heatmap(
    df: pd.DataFrame, save_path: Optional[str] = None
) -> plt.Figure:
    """Plots Heatmap of Correlation across numerical biomimetic features."""
    num_cols = [
        "bill_length_mm",
        "bill_depth_mm",
        "flipper_length_mm",
        "body_mass_g",
    ]
    corr_matrix = df[num_cols].corr()
    pretty = [FEATURE_LABELS[c] for c in num_cols]

    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        fmt=".2f",
        ax=ax,
        xticklabels=pretty,
        yticklabels=pretty,
        cbar_kws={"label": "Pearson Correlation Coefficient"},
    )
    ax.set_title("Correlation Heatmap of Biological Features")
    ax.tick_params(axis="x", rotation=25)
    ax.tick_params(axis="y", rotation=0)
    for label in ax.get_xticklabels():
        label.set_ha("right")
    plt.tight_layout()
    save_or_show_chart(fig, save_path)
    return fig


def plot_flipper_length_histogram(
    df: pd.DataFrame, save_path: Optional[str] = None
) -> plt.Figure:
    """Plots Flipper Length histogram demonstrating species separation."""
    palette = get_species_palette(df)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(
        data=df,
        x="flipper_length_mm",
        hue="species",
        hue_order=list(palette.keys()),
        palette=palette,
        element="step",
        kde=True,
        ax=ax,
        bins=25,
        alpha=0.45,
    )
    ax.set_title(
        "Flipper Length Distribution (Discriminative Cluster of Gentoo)"
    )
    ax.set_xlabel(FEATURE_LABELS["flipper_length_mm"])
    ax.set_ylabel("Count")
    # Seaborn owns the legend contents on purpose: overriding it with a literal
    # label list silently remaps species onto the wrong colours. Only the title
    # is restyled, which cannot desynchronise labels from handles.
    legend = ax.get_legend()
    if legend is not None:
        legend.set_title("Species")
    plt.tight_layout()
    save_or_show_chart(fig, save_path)
    return fig
