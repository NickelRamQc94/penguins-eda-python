"""Shared pytest fixtures for the Palmer Penguins test suite."""

import os
import sys

import matplotlib

matplotlib.use("Agg")  # Headless backend: CI runners have no display server

import pandas as pd
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data_cleaner import clean_penguins_data, load_raw_data


@pytest.fixture(scope="session")
def raw_df() -> pd.DataFrame:
    """The immutable CC0 Palmer Penguins dataset, exactly as shipped."""
    return load_raw_data(os.path.join(PROJECT_ROOT, "data", "penguins.csv"))


@pytest.fixture(scope="session")
def clean_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    """The dataset after the project's documented cleaning rules."""
    return clean_penguins_data(raw_df)
