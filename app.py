"""
Palmer Penguins — Institutional Data Analytics & AI Training Dashboard
Author: Jean Carlos Rojas Herrera (RojasJeanDL)
Description:
    State-of-the-art Streamlit dashboard adhering to Google/Institutional
    design standards (Theme-aware CSS, Card-wrapped Plotly charts,
    custom Metric cards with deltas, and HTML data tables).
"""

import html
import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

# Ensure project root is available for local imports
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data_cleaner import (
    REQUIRED_COLUMNS,
    clean_penguins_data,
    load_raw_data,
    validate_schema,
)

# ==============================================================================
# 1. PAGE CONFIGURATION & THEME STATE
# ==============================================================================
st.set_page_config(
    page_title="Palmer Penguins — Institutional Analytics Dashboard",
    page_icon="🐧",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme" not in st.session_state:
    st.session_state.theme = "dark"


def toggle_theme():
    st.session_state.theme = (
        "dark" if st.session_state.theme == "light" else "light"
    )


IS_DARK = st.session_state.theme == "dark"

# ==============================================================================
# 2. INSTITUTIONAL CSS DESIGN SYSTEM (ZINC / CARD-BASED PALETTE)
# ==============================================================================
# Dynamic CSS token switching based on theme state
bg = "#09090b" if IS_DARK else "#ffffff"
bg_subtle = "#0c0c0f" if IS_DARK else "#f9fafb"
card_bg = "#121216" if IS_DARK else "#ffffff"
card_hover = "#18181c" if IS_DARK else "#f4f4f5"
border = "#27272a" if IS_DARK else "#e4e4e7"
border_subtle = "#1e1e24" if IS_DARK else "#f0f0f2"
text = "#fafafa" if IS_DARK else "#09090b"
text_muted = "#a1a1aa" if IS_DARK else "#71717a"
text_dim = "#71717a" if IS_DARK else "#a1a1aa"
shadow = (
    "none"
    if IS_DARK
    else "0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03)"
)

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;600&display=swap');

    :root {{
        --bg: {bg};
        --bg-subtle: {bg_subtle};
        --card: {card_bg};
        --card-hover: {card_hover};
        --border: {border};
        --border-subtle: {border_subtle};
        --text: {text};
        --text-muted: {text_muted};
        --text-dim: {text_dim};
        --accent: #2563eb;
        --accent-muted: #1d4ed8;
        --green: #22c55e;
        --green-muted: rgba(34,197,94,0.12);
        --red: #ef4444;
        --red-muted: rgba(239,68,68,0.12);
        --amber: #f59e0b;
        --amber-muted: rgba(245,158,11,0.12);
        --shadow: {shadow};
        --radius: 12px;
    }}

    /* Hide default Streamlit chrome for clean presentation */
    header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton {{
        display: none !important;
    }}

    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container {{
        background-color: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'DM Sans', -apple-system, sans-serif !important;
    }}

    .block-container {{
        padding: 1.8rem 2.5rem 3rem !important;
        max-width: 1380px !important;
    }}

    /* Institutional Header Banner */
    .brand-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 1.2rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.5rem;
    }}
    .brand-title {{
        font-size: 1.85rem;
        font-weight: 700;
        color: var(--text);
        letter-spacing: -0.025em;
    }}
    .brand-subtitle {{
        font-size: 0.95rem;
        color: var(--text-muted);
        margin-top: 0.2rem;
    }}

    /* Pill-style Tabs */
    button[data-baseweb="tab"] {{
        background: transparent !important;
        color: var(--text-muted) !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.25rem !important;
        border: 1px solid transparent !important;
        border-radius: 8px !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--text) !important;
        background: var(--card) !important;
        border-color: var(--border) !important;
        box-shadow: var(--shadow) !important;
    }}
    [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{
        display: none !important;
    }}
    [data-baseweb="tab-list"] {{
        gap: 6px !important;
        background: var(--bg-subtle) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 4px;
    }}

    /* Metric Card (KPI) */
    .metric-card {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.25rem 1.4rem;
        box-shadow: var(--shadow);
        transition: transform 0.15s ease, border-color 0.15s ease;
    }}
    .metric-card:hover {{
        border-color: #3b82f6;
        transform: translateY(-2px);
    }}
    .metric-label {{
        font-size: 0.76rem;
        color: var(--text-muted);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .metric-value {{
        font-size: 1.85rem;
        font-weight: 700;
        color: var(--text);
        letter-spacing: -0.03em;
        margin-top: 0.25rem;
        font-family: 'JetBrains Mono', monospace;
    }}
    .metric-delta {{
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 0.45rem;
        padding: 3px 8px;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }}
    .delta-up {{ color: var(--green); background: var(--green-muted); }}
    .delta-down {{ color: var(--red); background: var(--red-muted); }}
    .delta-warn {{ color: var(--amber); background: var(--amber-muted); }}
    .delta-blue {{ color: #60a5fa; background: rgba(37,99,235,0.15); }}

    /* Chart Card Container */
    .chart-wrap {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.35rem 1.35rem 0.8rem;
        box-shadow: var(--shadow);
        margin-top: 1rem;
    }}
    .chart-title {{
        font-size: 0.98rem;
        font-weight: 700;
        color: var(--text);
    }}
    .chart-subtitle {{
        font-size: 0.8rem;
        color: var(--text-dim);
        margin-bottom: 0.75rem;
    }}

    /* Styled HTML Data Table */
    .data-table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.85rem;
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        overflow: hidden;
    }}
    .data-table th {{
        text-align: left;
        padding: 0.75rem 1rem;
        color: var(--text-muted);
        font-weight: 600;
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        background: var(--bg-subtle);
        border-bottom: 1px solid var(--border);
    }}
    .data-table td {{
        padding: 0.7rem 1rem;
        color: var(--text);
        border-bottom: 1px solid var(--border-subtle);
        font-family: 'DM Sans', sans-serif;
    }}
    .data-table tr:last-child td {{
        border-bottom: none;
    }}

    /* Badges */
    .badge {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.74rem;
        font-weight: 600;
    }}
    .badge-gentoo {{ color: #60a5fa; background: rgba(37,99,235,0.15); }}
    .badge-chinstrap {{ color: var(--amber); background: var(--amber-muted); }}
    .badge-adelie {{ color: var(--green); background: var(--green-muted); }}

    /* Insight Banner */
    .insight-box {{
        background: var(--bg-subtle);
        border: 1px solid var(--border);
        border-left: 4px solid #3b82f6;
        padding: 1.1rem 1.25rem;
        border-radius: 8px;
        margin-top: 1.1rem;
        font-size: 0.92rem;
        color: var(--text);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# 3. COMPONENT HELPERS (METRIC CARDS & PLOT THEME)
# ==============================================================================
def metric_card(label, value, delta=None, delta_type="up"):
    """Renders a sleek institutional KPI card with delta badge."""
    arrow = (
        "↑" if delta_type == "up" else ("↓" if delta_type == "down" else "●")
    )
    delta_html = (
        f'<div class="metric-delta delta-{delta_type}">{arrow} {delta}</div>'
        if delta
        else ""
    )
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


KNOWN_SPECIES_BADGES = {"adelie", "chinstrap", "gentoo"}


def esc(value, missing="—"):
    """HTML-escapes a cell value for the hand-built markup tables.

    Values can originate from a user-uploaded CSV and are injected into
    st.markdown(unsafe_allow_html=True), so escaping is mandatory. Pandas NA
    is rendered as an em dash instead of the literal string '<NA>'.
    """
    if value is None or (not isinstance(value, str) and pd.isna(value)):
        return missing
    return html.escape(str(value))


def badge_class(species):
    """Returns the CSS badge class, falling back for unknown species."""
    key = str(species).strip().lower()
    return f"badge badge-{key}" if key in KNOWN_SPECIES_BADGES else "badge"


def get_plot_layout():
    """Returns standardized theme-aware Plotly layout configuration."""
    grid_color = "rgba(255,255,255,0.06)" if IS_DARK else "rgba(0,0,0,0.06)"
    text_color = "#a1a1aa" if IS_DARK else "#52525b"
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color=text_color, size=11),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(
            gridcolor=grid_color,
            zerolinecolor=grid_color,
            tickfont=dict(size=10, color=text_color),
        ),
        yaxis=dict(
            gridcolor=grid_color,
            zerolinecolor=grid_color,
            tickfont=dict(size=10, color=text_color),
        ),
    )


# ==============================================================================
# ==============================================================================
# 4. DATA LOADING & FILTERING
# ==============================================================================
@st.cache_data
def load_default_data():
    csv_path = os.path.join(PROJECT_ROOT, "data", "penguins.csv")
    df_raw = load_raw_data(csv_path)
    df_clean = clean_penguins_data(df_raw)
    return df_raw, df_clean

# Sidebar Setup
st.sidebar.markdown("### ⚙️ " + ("Controles / Settings"))
language = st.sidebar.radio(
    "Idioma / Language:", options=["English 🇬🇧", "Español 🇪🇸"], index=0
)
is_es = "Español" in language

st.sidebar.markdown("---")
st.sidebar.markdown(
    "#### 📂 "
    + ("Cargar Dataset Propio (.CSV)" if is_es else "Upload Custom Dataset (.CSV)")
)
uploaded_file = st.sidebar.file_uploader(
    (
        "Sube un archivo CSV con columnas morfológicas:"
        if is_es
        else "Upload a CSV with morphological columns:"
    ),
    type=["csv"],
    help=(
        "Permite evaluar nuevos datasets o muestras adicionales usando el mismo pipeline de limpieza analítica."
        if is_es
        else "Allows evaluating new datasets or extra samples through the same analytical cleaning pipeline."
    ),
)

st.sidebar.caption(
    ("Columnas requeridas: " if is_es else "Required columns: ")
    + ", ".join(f"`{c}`" for c in REQUIRED_COLUMNS)
)

is_custom = False
if uploaded_file is not None:
    try:
        df_raw = pd.read_csv(uploaded_file)

        # Schema is validated BEFORE cleaning. A file carrying only the four
        # biometric columns survives clean_penguins_data() and then crashes
        # downstream on df["species"], so cleaning is not a sufficient gate.
        missing = validate_schema(df_raw)
        if missing:
            raise ValueError(
                ("Faltan columnas obligatorias: " if is_es else "Missing required columns: ")
                + ", ".join(missing)
            )

        df_clean = clean_penguins_data(df_raw)
        if df_clean.empty:
            raise ValueError(
                "0 filas válidas tras la limpieza."
                if is_es
                else "0 valid rows remaining after cleaning."
            )
        st.sidebar.success(
            f"✅ {'Dataset Personalizado (' + str(len(df_clean)) + ' filas)' if is_es else 'Custom Dataset (' + str(len(df_clean)) + ' rows)'}"
        )
        is_custom = True
    except Exception as exc:
        st.sidebar.error(
            f"❌ {'Error en el CSV:' if is_es else 'CSV Error:'} {exc}"
        )
        st.sidebar.info(
            "Se ha restaurado el dataset Palmer Penguins por defecto."
            if is_es
            else "Falling back to the default Palmer Penguins dataset."
        )
        df_raw, df_clean = load_default_data()
else:
    df_raw, df_clean = load_default_data()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "#### 🔍 " + ("Filtros Biométricos" if is_es else "Biometric Filters")
)

selected_species = st.sidebar.multiselect(
    "Especies / Species:" if is_es else "Species:",
    options=sorted(df_clean["species"].unique()),
    default=sorted(df_clean["species"].unique()),
)

selected_islands = st.sidebar.multiselect(
    "Islas / Islands:" if is_es else "Islands:",
    options=sorted(df_clean["island"].unique()),
    default=sorted(df_clean["island"].unique()),
)

sex_options = sorted(s for s in df_clean["sex"].dropna().unique())
selected_sex = st.sidebar.multiselect(
    "Sexo / Sex:" if is_es else "Sex:",
    options=sex_options,
    default=sex_options,
)

n_unknown_sex = int(df_clean["sex"].isna().sum())
include_unknown_sex = st.sidebar.checkbox(
    (
        f"Incluir sexo no registrado ({n_unknown_sex})"
        if is_es
        else f"Include unrecorded sex ({n_unknown_sex})"
    ),
    value=True,
    help=(
        "Estas filas no se imputan para no distorsionar el análisis de dimorfismo sexual."
        if is_es
        else "These rows are never imputed, so sexual dimorphism analysis stays unbiased."
    ),
)

# Apply filters. The sex mask is always applied (an earlier revision only
# filtered when fewer than 2 options were selected, which silently kept
# unrecorded-sex rows in some states and dropped them in others).
sex_mask = df_clean["sex"].isin(selected_sex)
if include_unknown_sex:
    sex_mask = sex_mask | df_clean["sex"].isna()

df_filtered = df_clean[
    df_clean["species"].isin(selected_species)
    & df_clean["island"].isin(selected_islands)
    & sex_mask
].copy()

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Arquitectura & Mentoría:**  
    [Jean Carlos Rojas Herrera](https://github.com/RojasJeanDL)  
    *AI Trainer (Contractor) · Data Analyst*
    """
)

# ==============================================================================
# 5. HEADER WITH BRANDING & THEME TOGGLE
# ==============================================================================
h_left, h_right = st.columns([8, 1])
with h_left:
    title_text = (
        "🐧 Palmer Penguins — Plataforma de Análisis e Inteligencia de Datos"
        if is_es
        else "🐧 Palmer Penguins — Executive Analytics & Data Intelligence Platform"
    )
    custom_badge = (
        '<span class="badge badge-gentoo" style="margin-left: 10px;">📂 Custom CSV Dataset Active</span>'
        if is_custom
        else ""
    )
    sub_text = (
        "Auditoría visual interactiva, detección de sesgos agregados (Paradoja de Simpson) y evaluación cualitativa para modelos LLM."
        if is_es
        else "Interactive visual audit, aggregated bias detection (Simpson's Paradox), and qualitative evaluation for LLMs."
    )
    st.markdown(
        f"""
        <div class="brand-header">
            <div>
                <div class="brand-title">{title_text} {custom_badge}</div>
                <div class="brand-subtitle">{sub_text}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with h_right:
    theme_label = "☀️ Light" if IS_DARK else "🌙 Dark"
    st.button(theme_label, on_click=toggle_theme, width="stretch")

# ==============================================================================
# 6. TABS ARCHITECTURE
# ==============================================================================
if df_filtered.empty:
    st.warning(
        "⚠️ "
        + (
            "Ninguna observación cumple los filtros seleccionados. "
            "Amplíe la selección de especies, islas o sexo en la barra lateral."
            if is_es
            else "No observations match the current filters. "
            "Widen the species, island or sex selection in the sidebar."
        )
    )
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 " + ("Explorador Ejecutivo y KPIs" if is_es else "Executive KPIs"),
        "🐧 "
        + (
            "Paradoja de Simpson (Detección de Sesgo)"
            if is_es
            else "Simpson's Paradox (Bias Alert)"
        ),
        "📈 "
        + ("Análisis Biomórfico Completo" if is_es else "Biomorphic Insights"),
        "🤖 "
        + (
            "Rúbrica para AI Trainer (LLM QA)"
            if is_es
            else "AI Trainer Rubric (LLM QA)"
        ),
    ]
)

# ------------------------------------------------------------------------------
# TAB 1: EXECUTIVE KPIS & HTML DATA TABLE
# ------------------------------------------------------------------------------
with tab1:
    # Every delta below is recomputed from df_filtered. Hardcoded deltas were
    # removed: they kept claiming "Gentoo +35%" and "r = 0.87" even when the
    # user had filtered Gentoo out entirely.
    n_total = len(df_clean)
    n_shown = len(df_filtered)
    share = n_shown / n_total * 100 if n_total else 0.0

    mass_by_species = df_filtered.groupby("species", observed=True)[
        "body_mass_g"
    ].mean()
    r_flipper_mass = (
        df_filtered["flipper_length_mm"].corr(df_filtered["body_mass_g"])
        if n_shown > 2
        else float("nan")
    )
    n_species_available = df_clean["species"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(
            "Muestras Filtradas" if is_es else "Filtered Samples",
            f"{n_shown}",
            delta=(
                f"{share:.0f}% de {n_total} limpias"
                if is_es
                else f"{share:.0f}% of {n_total} clean"
            ),
            delta_type="up" if share > 50 else "warn",
        )
    with c2:
        if len(mass_by_species) >= 2:
            heaviest = mass_by_species.idxmax()
            rest = mass_by_species.drop(heaviest).mean()
            uplift = (mass_by_species.max() / rest - 1) * 100
            mass_delta = f"{heaviest} +{uplift:.1f}%"
        elif len(mass_by_species) == 1:
            only = mass_by_species.index[0]
            mass_delta = (
                f"{only} únicamente" if is_es else f"{only} only"
            )
        else:
            mass_delta = "—"
        metric_card(
            "Masa Corporal Media" if is_es else "Mean Body Mass",
            f"{df_filtered['body_mass_g'].mean():,.0f} g",
            delta=mass_delta,
            delta_type="blue",
        )
    with c3:
        if pd.notna(r_flipper_mass):
            r_delta = (
                f"r = {r_flipper_mass:.2f} con masa"
                if is_es
                else f"r = {r_flipper_mass:.2f} vs mass"
            )
            r_type = "up" if r_flipper_mass >= 0.5 else "warn"
        else:
            r_delta, r_type = ("n < 3", "warn")
        metric_card(
            "Longitud de Aleta Media" if is_es else "Mean Flipper Length",
            f"{df_filtered['flipper_length_mm'].mean():.1f} mm",
            delta=r_delta,
            delta_type=r_type,
        )
    with c4:
        n_species_shown = df_filtered["species"].nunique()
        metric_card(
            "Diversidad de Especies" if is_es else "Species Diversity",
            f"{n_species_shown} / {n_species_available}",
            delta=(
                f"{df_filtered['island'].nunique()} islas"
                if is_es
                else f"{df_filtered['island'].nunique()} islands"
            ),
            delta_type="blue" if n_species_shown == n_species_available else "warn",
        )

    st.markdown("###")
    st.subheader(
        "📋 "
        + (
            "Muestra Institucional del Dataset (Primeras 10 Observaciones)"
            if is_es
            else "Institutional Dataset Preview (Top 10 Observations)"
        )
    )

    # Render custom styled HTML table for the first 10 rows
    sample_rows = df_filtered.head(10)
    rows_html = ""
    for _, r in sample_rows.iterrows():
        rows_html += f"""
        <tr>
            <td><span class="{badge_class(r['species'])}">{esc(r['species'])}</span></td>
            <td>{esc(r['island'])}</td>
            <td>{r['bill_length_mm']:.1f} mm</td>
            <td>{r['bill_depth_mm']:.1f} mm</td>
            <td>{r['flipper_length_mm']:.0f} mm</td>
            <td><b>{r['body_mass_g']:,.0f} g</b></td>
            <td>{esc(r['sex'])}</td>
        </tr>
        """
    st.markdown(
        f"""
        <table class="data-table">
            <thead>
                <tr>
                    <th>Especie / Species</th>
                    <th>Isla / Island</th>
                    <th>Pico Largo / Bill Len</th>
                    <th>Pico Prof. / Bill Depth</th>
                    <th>Aleta / Flipper</th>
                    <th>Masa / Body Mass</th>
                    <th>Sexo / Sex</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("###")
    with st.expander(
        "📂 "
        + (
            "Ver Tabla Completa y Exportar CSV"
            if is_es
            else "View Full Dataset & Export CSV"
        )
    ):
        st.dataframe(df_filtered, width="stretch", height=280)
        csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 "
            + ("Descargar Dataset Filtrado (.CSV)" if is_es else "Download CSV"),
            data=csv_bytes,
            file_name="palmer_penguins_filtered.csv",
            mime="text/csv",
        )

# ------------------------------------------------------------------------------
# TAB 2: SIMPSON'S PARADOX INTERACTIVE EXPLORER
# ------------------------------------------------------------------------------
with tab2:
    st.markdown(
        f"""
        <div class="chart-wrap">
            <div class="chart-title">{"Paradoja de Simpson en Mediciones de Pico (Longitud vs Profundidad)" if is_es else "Simpson's Paradox in Bill Dimensions (Length vs. Depth)"}</div>
            <div class="chart-subtitle">{"Demostración empírica de cómo la agregación estadística oculta correlaciones positivas reales dentro de cada subgrupo biológico." if is_es else "Empirical demonstration of how population aggregation obscures true positive correlations within biological subgroups."}</div>
        """,
        unsafe_allow_html=True,
    )

    toggle_mode = st.radio(
        "Seleccionar Modo de Regresión / Select Regression Mode:",
        options=[
            (
                "Segmentado por Especie (Tendencia Real — Pendiente POSITIVA)"
                if is_es
                else "Segmented by Species (True Biological Correlation — POSITIVE Slope)"
            ),
            (
                "Población Agregada / Sin Segmentar (Sesgo de Simpson — Pendiente INVERSA)"
                if is_es
                else "Pooled Population (Simpson's Paradox Bias — INVERSE Slope)"
            ),
        ],
        horizontal=True,
    )

    is_segmented = "Segmentado" in toggle_mode or "Segmented" in toggle_mode

    # An OLS fit needs at least 2 points per group; drop the trendline rather
    # than let statsmodels raise on a heavily filtered selection.
    group_sizes = (
        df_filtered.groupby("species", observed=True).size()
        if is_segmented
        else pd.Series([len(df_filtered)])
    )
    trend = "ols" if group_sizes.min() >= 2 else None
    if trend is None:
        st.info(
            "ℹ️ "
            + (
                "Regresión omitida: algún grupo tiene menos de 2 observaciones."
                if is_es
                else "Trendline omitted: a group has fewer than 2 observations."
            )
        )

    if is_segmented:
        fig_simpson = px.scatter(
            df_filtered,
            x="bill_length_mm",
            y="bill_depth_mm",
            color="species",
            trendline=trend,
            labels={
                "bill_length_mm": "Longitud del Pico / Bill Len (mm)",
                "bill_depth_mm": "Profundidad del Pico / Bill Depth (mm)",
                "species": "Especie",
            },
            height=460,
            color_discrete_sequence=["#60a5fa", "#f59e0b", "#22c55e"],
        )
    else:
        fig_simpson = px.scatter(
            df_filtered,
            x="bill_length_mm",
            y="bill_depth_mm",
            trendline=trend,
            labels={
                "bill_length_mm": "Longitud del Pico / Bill Len (mm)",
                "bill_depth_mm": "Profundidad del Pico / Bill Depth (mm)",
            },
            height=460,
            color_discrete_sequence=["#ef4444"],
        )

    fig_simpson.update_layout(**get_plot_layout())
    st.plotly_chart(
        fig_simpson, width="stretch", config={"displayModeBar": False}
    )
    st.markdown("</div>", unsafe_allow_html=True)

    insight_es = """
    <b>Razonamiento Crítico para Toma de Decisiones:</b><br>
    Al analizar la población total de pingüinos sin segmentar, el modelo de regresión lineal simple sugiere una relación inversa (pendiente negativa): <i>picos más largos parecerían ser más estrechos</i>. Sin embargo, en cuanto estratificamos por especie, <b>la correlación en cada subgrupo es estrictamente positiva</b>. Esta paradoja resalta por qué los Analistas de Datos y los evaluadores de IA deben desconfiar de los promedios globales agregados.
    """
    insight_en = """
    <b>Executive Critical Thinking Insight:</b><br>
    When inspecting the pooled Antarctic bird population, a simple linear regression model suggests an inverse correlation (negative slope): <i>longer bills appear shallower</i>. However, once stratified by species, <b>the true correlation within every single subgroup is strictly positive</b>. This paradox illustrates why Data Analysts and AI Trainers must rigorously audit aggregated data for subgroup bias.
    """
    st.markdown(
        f'<div class="insight-box">{"🔍 " + (insight_es if is_es else insight_en)}</div>',
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------------------
# TAB 3: VISUAL STATISTICAL INSIGHTS
# ------------------------------------------------------------------------------
with tab3:
    chart_opt = st.selectbox(
        "Seleccione Vista Analítica / Select Analytical View:",
        options=[
            (
                "1. Distribución Geográfica y Clústeres por Isla"
                if is_es
                else "1. Geographic Distribution & Island Clustering"
            ),
            (
                "2. Dimorfismo Sexual y Jerarquía de Masa Corporal"
                if is_es
                else "2. Sexual Dimorphism & Body Mass Hierarchy"
            ),
            (
                "3. Distribución Discriminativa de Longitud de Aleta"
                if is_es
                else "3. Discriminative Flipper Length Distribution"
            ),
            (
                "4. Matriz de Correlación Biológica de Pearson"
                if is_es
                else "4. Pearson Biomorphic Correlation Matrix"
            ),
        ],
    )

    if "1." in chart_opt:
        st.markdown(
            f"""
            <div class="chart-wrap">
                <div class="chart-title">{"Distribución Geográfica de Especies por Isla" if is_es else "Geographic Species Distribution Across Islands"}</div>
                <div class="chart-subtitle">{"Frecuencia de observaciones en Biscoe, Dream y Torgersen." if is_es else "Observation frequency across Biscoe, Dream, and Torgersen."}</div>
            """,
            unsafe_allow_html=True,
        )
        fig = px.histogram(
            df_filtered,
            x="island",
            color="species",
            barmode="group",
            height=430,
            color_discrete_sequence=["#60a5fa", "#f59e0b", "#22c55e"],
            labels={
                "island": "Isla / Island",
                "count": "Observaciones / Count",
                "species": "Especie",
            },
        )
        fig.update_layout(**get_plot_layout())
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    elif "2." in chart_opt:
        st.markdown(
            f"""
            <div class="chart-wrap">
                <div class="chart-title">{"Dimorfismo Sexual y Distribución de Masa Corporal" if is_es else "Sexual Dimorphism & Body Mass Distribution"}</div>
                <div class="chart-subtitle">{"Comparativa en gramos diferenciando machos y hembras." if is_es else "Body mass boxplot comparing males and females."}</div>
            """,
            unsafe_allow_html=True,
        )
        df_sex = df_filtered.dropna(subset=["sex"]).copy()
        fig = px.box(
            df_sex,
            x="species",
            y="body_mass_g",
            color="sex",
            height=430,
            color_discrete_sequence=["#3b82f6", "#ec4899"],
            labels={
                "species": "Especie",
                "body_mass_g": "Peso / Mass (g)",
                "sex": "Sexo",
            },
        )
        fig.update_layout(**get_plot_layout())
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    elif "3." in chart_opt:
        st.markdown(
            f"""
            <div class="chart-wrap">
                <div class="chart-title">{"Separación Morfológica por Longitud de Aleta (mm)" if is_es else "Morphological Separation by Flipper Length (mm)"}</div>
                <div class="chart-subtitle">{"Histograma y KDE demostrando el clúster discriminativo del pingüino Gentoo." if is_es else "Histogram showing clean cluster separation for Gentoo (>210 mm)."}</div>
            """,
            unsafe_allow_html=True,
        )
        fig = px.histogram(
            df_filtered,
            x="flipper_length_mm",
            color="species",
            nbins=25,
            opacity=0.65,
            height=430,
            color_discrete_sequence=["#60a5fa", "#f59e0b", "#22c55e"],
            labels={
                "flipper_length_mm": "Longitud de Aleta / Flipper Length (mm)",
                "species": "Especie",
            },
        )
        fig.update_layout(**get_plot_layout())
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    elif "4." in chart_opt:
        st.markdown(
            f"""
            <div class="chart-wrap">
                <div class="chart-title">{"Matriz de Correlación de Pearson entre Variables Biométricas" if is_es else "Pearson Biometric Feature Correlation Heatmap"}</div>
                <div class="chart-subtitle">{"Coeficientes r entre longitud de pico, profundidad, aleta y masa." if is_es else "Correlation coefficients across bill length, depth, flipper, and mass."}</div>
            """,
            unsafe_allow_html=True,
        )
        num_cols = [
            "bill_length_mm",
            "bill_depth_mm",
            "flipper_length_mm",
            "body_mass_g",
        ]
        corr = df_filtered[num_cols].corr()
        fig = px.imshow(
            corr,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            height=430,
        )
        fig.update_layout(**get_plot_layout())
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 4: AI TRAINER QUALITY RUBRIC & ANNOTATION
# ------------------------------------------------------------------------------
with tab4:
    st.markdown(
        f"""
        <div class="chart-wrap">
            <div class="chart-title">{"🤖 Demostración Operativa: Evaluación de Modelos LLM & Anotación de Datos" if is_es else "🤖 Operational Demo: LLM Quality Evaluation & Data Annotation"}</div>
            <div class="chart-subtitle">{"Este módulo evidencia la capacidad del candidato para auditar, justificar y puntuar salidas de IA en inglés y español." if is_es else "Demonstrating candidate competence in LLM output evaluation, factuality checking, and rubric scoring."}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### 📝 Prompt de Prueba / Evaluation Prompt:")
    st.code(
        "Explain the relationship between bill length and bill depth in Palmer Penguins, and state whether bill depth is a good single predictor of species.",
        language="text",
    )

    colA, colB = st.columns(2)
    with colA:
        st.markdown(
            "##### 🔴 Model Response A (Naive / Flawed)"
            if is_es
            else "##### 🔴 Model Response A (Naive / Flawed)"
        )
        st.error(
            "In Palmer Penguins, bill length and bill depth have a strong negative correlation (-0.24). This means that penguins with longer bills always have shallower bills. Therefore, bill depth alone is not enough to classify species, but overall longer bills mean thinner bills across all penguins in Antarctica."
        )
        st.markdown(
            "**Calificación / Rating:** `2 / 5 (Factually Misleading & Biased)`"
        )
    with colB:
        st.markdown(
            "##### 🟢 Model Response B (Factually Accurate)"
            if is_es
            else "##### 🟢 Model Response B (Factually Accurate)"
        )
        st.success(
            "While the aggregate correlation between bill length and depth appears negative (-0.24), this is a classic manifestation of Simpson's Paradox. When analyzed within individual species, the correlation is strongly positive (Adélie r=0.39, Chinstrap r=0.65, Gentoo r=0.64). Bill depth alone is a strong discriminator to separate Gentoo (shallower bills) from Adélie and Chinstrap."
        )
        st.markdown(
            "**Calificación / Rating:** `5 / 5 (Excellent Analytical Depth)`"
        )

    st.markdown(
        """
        <div class="insight-box">
        <b>✍️ Written Human Feedback & Justification (Why & How to Improve):</b><br>
        <i>Response A</i> suffers from severe aggregation bias by interpreting the unsegmented pooled statistic without identifying <b>Simpson's Paradox</b>. It incorrectly claims that 'longer bills always mean shallower bills', which is false within every individual species.<br><br>
        <i>Response B</i> correctly identifies the statistical paradox, reports the stratified positive correlation coefficients for Adélie, Chinstrap, and Gentoo, and accurately identifies bill depth as an effective discriminator for Gentoo penguins. <b>Preference: Response B</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )
