"""
Palmer Penguins Data Cleaner & Prep Module
Author: Jean Carlos Rojas Herrera (RojasJeanDL)
Description:
    Provides reproducible, unbiased data cleaning and preprocessing utilities
    for the Palmer Penguins dataset.
"""

from typing import List

import pandas as pd

CORE_METRICS: List[str] = [
    "bill_length_mm",
    "bill_depth_mm",
    "flipper_length_mm",
    "body_mass_g",
]
CATEGORICAL_COLS: List[str] = ["species", "island", "sex"]
REQUIRED_COLUMNS: List[str] = CORE_METRICS + CATEGORICAL_COLS


def load_raw_data(filepath: str = "../data/penguins.csv") -> pd.DataFrame:
    """Loads raw Palmer Penguins CSV data from disk.

    Args:
        filepath (str): Path to the CSV dataset file.

    Returns:
        pd.DataFrame: Raw penguins dataframe.
    """
    df = pd.read_csv(filepath)
    return df


def clean_penguins_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans Palmer Penguins dataset with an unbiased, documented strategy.

    Cleaning Rules:
        1. Drop rows where all primary morphological features are missing
           ('bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g').
           These rows correspond to unmeasured birds and carry zero information.
        2. Normalize categorical text columns by stripping whitespace.
        3. Avoid imputing 'sex' to prevent introducing artificial bias in
           dimorphism analysis (we keep NaN sex rows for species/island EDA
           and filter locally when analyzing sexual dimorphism).

    Args:
        df (pd.DataFrame): Raw dataframe.

    Returns:
        pd.DataFrame: Cleaned dataframe.
    """
    # Drop uninformative rows where core biological measurements are all missing
    df_clean = df.dropna(subset=CORE_METRICS).copy()

    # Defensive string normalization on categorical features
    for col in CATEGORICAL_COLS:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype("string").str.strip()

    return df_clean


def validate_schema(df: pd.DataFrame) -> List[str]:
    """Returns the list of required columns missing from a dataframe.

    Used to reject malformed user-uploaded CSVs *before* the dashboard tries
    to group or filter by columns that do not exist. Cleaning alone is not a
    sufficient gate: a file carrying only the four biometric columns survives
    ``clean_penguins_data`` and then fails downstream on ``species``.

    Args:
        df (pd.DataFrame): Candidate dataframe (typically user-uploaded).

    Returns:
        List[str]: Missing required column names, empty if the schema is valid.
    """
    return [col for col in REQUIRED_COLUMNS if col not in df.columns]


def get_species_morphological_profile(df_clean: pd.DataFrame) -> pd.DataFrame:
    """Computes mean biological metrics grouped by penguin species.

    Args:
        df_clean (pd.DataFrame): Cleaned penguins dataframe.

    Returns:
        pd.DataFrame: Summary table of mean morphological measurements.
    """
    profile = (
        df_clean.groupby("species")[
            [
                "bill_length_mm",
                "bill_depth_mm",
                "flipper_length_mm",
                "body_mass_g",
            ]
        ]
        .mean()
        .round(2)
    )
    return profile
