"""Tests for the cleaning contract in src/data_cleaner.py.

These lock the two claims the README makes about data hygiene: exactly two
rows are dropped, and `sex` is never imputed.
"""

import pandas as pd
import pytest

from src.data_cleaner import (
    CORE_METRICS,
    REQUIRED_COLUMNS,
    clean_penguins_data,
    get_species_morphological_profile,
    validate_schema,
)


def test_raw_dataset_is_the_documented_one(raw_df):
    assert raw_df.shape == (344, 8)
    assert set(REQUIRED_COLUMNS).issubset(raw_df.columns)


def test_cleaning_drops_exactly_the_two_unmeasured_rows(raw_df, clean_df):
    assert len(raw_df) == 344
    assert len(clean_df) == 342
    # Every dropped row must be missing ALL four biometrics, never just one.
    dropped = raw_df.loc[~raw_df.index.isin(clean_df.index)]
    assert len(dropped) == 2
    assert dropped[CORE_METRICS].isna().all(axis=None)


def test_no_core_metric_is_null_after_cleaning(clean_df):
    assert clean_df[CORE_METRICS].notna().all(axis=None)


def test_sex_is_never_imputed(clean_df):
    """The bias-prevention guarantee: missing sex stays missing.

    Imputing sex by species mode would manufacture the sexual dimorphism
    signal that the body-mass analysis is supposed to measure.
    """
    assert clean_df["sex"].isna().sum() == 9
    assert set(clean_df["sex"].dropna().unique()) == {"male", "female"}


def test_categorical_whitespace_is_stripped():
    df = pd.DataFrame(
        {
            "species": ["  Adelie  "],
            "island": ["\tBiscoe"],
            "sex": ["male "],
            "bill_length_mm": [39.1],
            "bill_depth_mm": [18.7],
            "flipper_length_mm": [181.0],
            "body_mass_g": [3750.0],
        }
    )
    cleaned = clean_penguins_data(df)
    assert cleaned.loc[0, "species"] == "Adelie"
    assert cleaned.loc[0, "island"] == "Biscoe"
    assert cleaned.loc[0, "sex"] == "male"


def test_cleaning_does_not_mutate_its_input(raw_df):
    before = raw_df.copy()
    clean_penguins_data(raw_df)
    pd.testing.assert_frame_equal(raw_df, before)


def test_species_profile_covers_every_species(clean_df):
    profile = get_species_morphological_profile(clean_df)
    assert set(profile.index) == {"Adelie", "Chinstrap", "Gentoo"}
    assert list(profile.columns) == CORE_METRICS


# --- Schema validation (regression: the dashboard used to crash here) --------


def test_validate_schema_accepts_the_reference_dataset(raw_df):
    assert validate_schema(raw_df) == []


def test_validate_schema_rejects_biometrics_only_upload(clean_df):
    """Regression guard for the custom-CSV crash.

    A file carrying only the four biometric columns passes cleaning and then
    raised KeyError('species') deep inside the dashboard sidebar. Validation
    has to reject it up front.
    """
    biometrics_only = clean_df[CORE_METRICS].copy()
    missing = validate_schema(biometrics_only)

    assert missing == ["species", "island", "sex"]
    # It really does survive cleaning - which is why cleaning is not a gate.
    assert not clean_penguins_data(biometrics_only).empty


@pytest.mark.parametrize("dropped", REQUIRED_COLUMNS)
def test_validate_schema_reports_each_missing_column(clean_df, dropped):
    assert validate_schema(clean_df.drop(columns=[dropped])) == [dropped]
