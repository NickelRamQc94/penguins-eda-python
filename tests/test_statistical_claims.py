"""Executable verification of every statistic quoted in the README.

The point of this file is that no number in the documentation is an assertion
of trust: each one is recomputed from `data/penguins.csv` on every CI run. If a
claim drifts from the data, the build fails.
"""

import pytest

SPECIES = ["Adelie", "Chinstrap", "Gentoo"]


# --- Claim: flipper length is the strongest correlate of body mass (r = 0.87)


def test_flipper_length_body_mass_correlation_is_087(clean_df):
    r = clean_df["flipper_length_mm"].corr(clean_df["body_mass_g"])
    assert r == pytest.approx(0.87, abs=0.005)


def test_flipper_mass_is_the_strongest_pair(clean_df):
    corr = clean_df[
        ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    ].corr()
    strongest = corr.where(corr < 0.999).abs().stack().idxmax()
    assert set(strongest) == {"flipper_length_mm", "body_mass_g"}


# --- Claim: Simpson's Paradox in bill dimensions ----------------------------


def test_pooled_bill_correlation_is_negative(clean_df):
    r = clean_df["bill_length_mm"].corr(clean_df["bill_depth_mm"])
    assert r == pytest.approx(-0.24, abs=0.005)
    assert r < 0


@pytest.mark.parametrize(
    "species,expected_r",
    [("Adelie", 0.39), ("Chinstrap", 0.65), ("Gentoo", 0.64)],
)
def test_within_species_bill_correlation_is_positive(clean_df, species, expected_r):
    subset = clean_df[clean_df["species"] == species]
    r = subset["bill_length_mm"].corr(subset["bill_depth_mm"])
    assert r > 0, f"{species} must correlate positively for the paradox to hold"
    assert r == pytest.approx(expected_r, abs=0.01)


# --- Claim: island geography segregates species -----------------------------


def test_gentoo_only_on_biscoe_and_chinstrap_only_on_dream(clean_df):
    islands = clean_df.groupby("species", observed=True)["island"].unique()
    assert set(islands["Gentoo"]) == {"Biscoe"}
    assert set(islands["Chinstrap"]) == {"Dream"}
    assert set(islands["Adelie"]) == {"Biscoe", "Dream", "Torgersen"}


# --- Claim: Gentoo mass hierarchy -------------------------------------------


def test_gentoo_mass_uplift(clean_df):
    means = clean_df.groupby("species", observed=True)["body_mass_g"].mean()
    assert means["Gentoo"] == pytest.approx(5076, abs=1)
    assert (means["Gentoo"] / means["Adelie"] - 1) * 100 == pytest.approx(37.2, abs=0.1)
    assert (means["Gentoo"] / means["Chinstrap"] - 1) * 100 == pytest.approx(36.0, abs=0.1)


def test_adelie_and_chinstrap_are_not_separable_by_mass(clean_df):
    """Guards the README against overclaiming a three-way mass split."""
    means = clean_df.groupby("species", observed=True)["body_mass_g"].mean()
    assert abs(means["Adelie"] - means["Chinstrap"]) < 50


def test_males_outweigh_females_in_every_species(clean_df):
    sexed = clean_df.dropna(subset=["sex"])
    means = sexed.groupby(["species", "sex"], observed=True)["body_mass_g"].mean()
    for species in SPECIES:
        assert means[(species, "male")] > means[(species, "female")]


# --- Claim: flipper length discriminates Gentoo at 207 mm / 97.7% -----------


def _threshold_scan(clean_df):
    is_gentoo = clean_df["species"].eq("Gentoo")
    scan = {}
    for threshold in range(195, 226):
        predicted = clean_df["flipper_length_mm"] >= threshold
        scan[threshold] = int((predicted != is_gentoo).sum())
    return scan


def test_optimal_flipper_threshold_is_207mm(clean_df):
    scan = _threshold_scan(clean_df)
    best = min(scan, key=scan.get)
    assert best == 207
    assert scan[best] == 8
    accuracy = (len(clean_df) - scan[best]) / len(clean_df) * 100
    assert accuracy == pytest.approx(97.7, abs=0.05)


def test_210mm_threshold_is_measurably_worse(clean_df):
    """The round 210 mm figure the first draft quoted is not optimal."""
    scan = _threshold_scan(clean_df)
    assert scan[210] > scan[207]


def test_gentoo_and_non_gentoo_flipper_ranges_overlap(clean_df):
    """The separation is strong but not clean - the README must not say 'clean'."""
    is_gentoo = clean_df["species"].eq("Gentoo")
    gentoo_min = clean_df.loc[is_gentoo, "flipper_length_mm"].min()
    other_max = clean_df.loc[~is_gentoo, "flipper_length_mm"].max()
    assert gentoo_min == 203
    assert other_max == 212
    assert gentoo_min < other_max, "ranges overlap: 'clean separation' is false"
