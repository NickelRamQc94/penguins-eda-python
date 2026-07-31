"""
Palmer Penguins Figure Generator & Exporter (Headless Agg Backend)
Author: Jean Carlos Rojas Herrera (RojasJeanDL)
Description:
    Generates and exports all 5 publication-quality Seaborn/Matplotlib charts
    into the images/ directory for README and documentation rendering.
"""

import os
import sys
import matplotlib
matplotlib.use("Agg")  # Use headless backend for server/CLI environments

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data_cleaner import load_raw_data, clean_penguins_data
from src.visualization_utils import (
    setup_visualization_theme,
    plot_species_distribution,
    plot_bill_dimensions_simpson_paradox,
    plot_body_mass_by_species_and_sex,
    plot_correlation_heatmap,
    plot_flipper_length_histogram,
)


def generate_all_portfolio_charts(
    csv_path: str = "data/penguins.csv", output_dir: str = "images"
) -> list:
    """Executes full visualization pipeline and saves 5 PNG charts."""
    abs_csv = os.path.join(PROJECT_ROOT, csv_path)
    abs_output = os.path.join(PROJECT_ROOT, output_dir)
    os.makedirs(abs_output, exist_ok=True)

    print(f"[INFO] Loading raw dataset from: {abs_csv}")
    df_raw = load_raw_data(abs_csv)

    print("[INFO] Cleaning Palmer Penguins data...")
    df_clean = clean_penguins_data(df_raw)
    print(f"[INFO] Clean dataset ready: {len(df_clean)} rows.")

    print("[INFO] Setting up visualization theme...")
    setup_visualization_theme(dpi=120, export_dpi=150, palette="colorblind")

    charts = [
        (
            "01_species_distribution.png",
            plot_species_distribution,
            "Species distribution by island",
        ),
        (
            "02_bill_scatter.png",
            plot_bill_dimensions_simpson_paradox,
            "Simpson's Paradox scatter plot",
        ),
        (
            "03_mass_by_species.png",
            plot_body_mass_by_species_and_sex,
            "Body mass boxplot by species/sex",
        ),
        (
            "04_correlation_heatmap.png",
            plot_correlation_heatmap,
            "Correlation heatmap of biological features",
        ),
        (
            "05_flipper_histogram.png",
            plot_flipper_length_histogram,
            "Flipper length histogram by species",
        ),
    ]

    saved_paths = []
    for filename, plot_fn, desc in charts:
        out_path = os.path.join(abs_output, filename)
        print(f"[INFO] Generating chart: {desc} -> {filename}")
        plot_fn(df_clean, save_path=out_path)
        if os.path.exists(out_path):
            size_kb = os.path.getsize(out_path) / 1024
            print(f"       -> Saved successfully: {filename} ({size_kb:.1f} KB)")
            saved_paths.append(out_path)
        else:
            raise RuntimeError(f"Chart export failed for {filename}")

    print(f"[SUCCESS] All 5 portfolio charts generated in: {abs_output}")
    return saved_paths


if __name__ == "__main__":
    generate_all_portfolio_charts()
