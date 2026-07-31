"""
Palmer Penguins Dataset Downloader / Exporter (Zero-Dependency Standard Library)
Author: Jean Carlos Rojas Herrera (RojasJeanDL)
Description:
    Downloads the CC0 Palmer Penguins dataset to data/penguins.csv using
    Python's standard library (urllib.request), requiring no external packages.
"""

import os
import urllib.request

OFFICIAL_CSV_URL = (
    "https://raw.githubusercontent.com/allisonhorst/palmerpenguins/master/inst/extdata/penguins.csv"
)


def acquire_penguins_dataset(
    output_filepath: str = "../data/penguins.csv",
) -> str:
    """Downloads the Palmer Penguins dataset and saves it to disk."""
    abs_filepath = os.path.abspath(
        os.path.join(os.path.dirname(__file__), output_filepath)
    )
    output_dir = os.path.dirname(abs_filepath)
    os.makedirs(output_dir, exist_ok=True)

    print("[INFO] Downloading Palmer Penguins dataset from official repository...")
    try:
        urllib.request.urlretrieve(OFFICIAL_CSV_URL, abs_filepath)
        print(f"[SUCCESS] Dataset saved to {abs_filepath}")
        return abs_filepath
    except Exception as exc:
        print(f"[ERROR] Failed to download dataset: {exc}")
        raise


if __name__ == "__main__":
    acquire_penguins_dataset()
