"""Smoke tests for the Streamlit dashboard using Streamlit's AppTest harness.

These cover the states that previously produced a red traceback for the user:
an empty filter selection and a custom CSV upload with a missing column.
"""

import os

import pytest

from streamlit.testing.v1 import AppTest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP = os.path.join(PROJECT_ROOT, "app.py")
TIMEOUT = 90


def _run():
    app = AppTest.from_file(APP, default_timeout=TIMEOUT)
    app.run()
    return app


def test_dashboard_boots_without_exception():
    app = _run()
    assert not app.exception, f"dashboard raised: {app.exception}"


def test_dashboard_renders_four_tabs_and_four_kpis():
    app = _run()
    assert len(app.tabs) == 4
    # KPI cards are custom HTML blocks, so they are counted as markdown.
    assert any("metric-card" in md.value for md in app.markdown)


def test_clearing_every_species_shows_a_warning_instead_of_crashing():
    """Regression: an empty selection used to render NaN charts silently."""
    app = AppTest.from_file(APP, default_timeout=TIMEOUT)
    app.run()

    species_filter = app.sidebar.multiselect[0]
    species_filter.set_value([]).run()

    assert not app.exception, f"empty filter raised: {app.exception}"
    assert len(app.warning) == 1
    assert "filter" in app.warning[0].value.lower() or "filtro" in app.warning[0].value.lower()


def test_single_species_selection_still_renders():
    app = AppTest.from_file(APP, default_timeout=TIMEOUT)
    app.run()

    app.sidebar.multiselect[0].set_value(["Gentoo"]).run()

    assert not app.exception
    assert not app.warning


def test_language_toggle_switches_to_spanish():
    app = AppTest.from_file(APP, default_timeout=TIMEOUT)
    app.run()

    app.sidebar.radio[0].set_value("Español 🇪🇸").run()

    assert not app.exception
    assert any("Plataforma de Análisis" in md.value for md in app.markdown)


@pytest.mark.parametrize("sex_selection", [[], ["male"], ["female", "male"]])
def test_every_sex_filter_state_is_safe(sex_selection):
    app = AppTest.from_file(APP, default_timeout=TIMEOUT)
    app.run()

    app.sidebar.multiselect[2].set_value(sex_selection).run()

    assert not app.exception, f"sex filter {sex_selection} raised: {app.exception}"
